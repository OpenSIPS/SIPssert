#!/usr/bin/env python
"""Unit tests for the scheduler run loop (sipssert.tasks_list).

Regression tests for the scheduler stall: the run loop used to poll
windowed docker.events(since, until) calls on every iteration. The
`until` argument makes the docker daemon hold the HTTP stream open
until that wall-clock time is reached by the daemon itself, so any
clock skew between the host and the docker daemon (common with desktop
hypervisors after host sleep) blocked the whole scheduling loop, and
events whose timestamps follow the daemon clock were systematically
missed when filtered against host-clock windows. The loop also had a
broken throttle expression and never slept, hammering the daemon with
event requests hundreds of times per second.
"""

import os
import queue
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import sipssert.tasks_list as tasks_list_module
from sipssert import logger
from sipssert.state import State
from sipssert.tasks_list import TasksList
from sipssert.testing import TestStatus

LOG_DIR = tempfile.mkdtemp(prefix="sipssert_test_")


def setUpModule():
    logger.init_logger({"file": os.path.join(LOG_DIR, "test.log"),
                        "level": "CRITICAL"}, None)


def tearDownModule():
    shutil.rmtree(LOG_DIR, ignore_errors=True)


def make_tasks_list(defs, timeout=None):
    """Builds a real TasksList with a mocked docker controller."""
    ctrl = MagicMock()
    # an empty (iterable) events stream by default
    ctrl.docker.events.return_value = iter([])
    # containers are created inside Task.run(): make them well-behaved mocks
    container = MagicMock()
    container.logs.return_value = b""
    container.attrs = {"State": {"ExitCode": 0}}
    ctrl.docker.containers.create.return_value = container
    cfg = {"tasks": defs}
    logs_dir = tempfile.mkdtemp(prefix="sipssert_test_")
    tasks = TasksList("tasks", "/test", logs_dir, cfg, ctrl,
                      None, None, {}, {}, "prefix", {})
    if timeout:
        tasks.set_timeout(timeout)
    return tasks, ctrl


def mock_container(exit_code=0):
    """A docker container mock as it looks after the task has started."""
    container = MagicMock()
    container.logs.return_value = b""
    container.attrs = {"State": {"ExitCode": exit_code}}
    return container


class TestEventStream(unittest.TestCase):

    def test_single_live_stream_without_time_window(self):
        tasks, ctrl = make_tasks_list([
            {"name": "t1", "image": "busybox"},
        ], timeout=0.3)
        tasks.run()
        self.assertEqual(ctrl.docker.events.call_count, 1,
                         "the run loop must consume one live events stream, "
                         "not open a new windowed stream per iteration")
        args, kwargs = ctrl.docker.events.call_args
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {"decode": True})

    def test_die_event_from_stream_finishes_task(self):
        tasks, _ = make_tasks_list([
            {"name": "t1", "image": "busybox"},
        ])
        task = tasks.get_task("t1")
        self.assertIsNotNone(task)
        task.container = mock_container()
        tasks.pending_tasks.remove(task)
        tasks.running_tasks.append(task)
        tasks._event_queue = queue.Queue()
        tasks._event_queue.put({
            "Type": "container",
            "Action": "die",
            "Actor": {"Attributes": {
                "name": task.container_name, "exitCode": "0"}},
        })
        tasks.handle_events()
        self.assertEqual(task.state, State.ENDED)
        self.assertEqual(tasks.status, TestStatus.PASS)
        self.assertNotIn(task, tasks.running_tasks)


class TestRunLoopThrottle(unittest.TestCase):

    def test_run_loop_sleeps_between_iterations(self):
        tasks, _ = make_tasks_list([
            {"name": "t1", "image": "busybox"},
        ], timeout=0.3)
        with patch("time.sleep") as mock_sleep:
            tasks.run()
        self.assertTrue(mock_sleep.called,
                        "the run loop must throttle itself between "
                        "iterations instead of spinning")


class TestTerminateHardening(unittest.TestCase):

    def test_terminate_continues_after_stop_error(self):
        tasks, _ = make_tasks_list([
            {"name": "d1", "image": "busybox", "daemon": True},
            {"name": "d2", "image": "busybox", "daemon": True},
        ])
        d1 = tasks.get_task("d1")
        self.assertIsNotNone(d1)
        d1.container = mock_container()
        d1.container.stop.side_effect = RuntimeError("docker stop failed")
        tasks.pending_tasks.remove(d1)
        tasks.daemon_tasks.append(d1)
        d2 = tasks.get_task("d2")
        self.assertIsNotNone(d2)
        d2.container = mock_container()
        tasks.pending_tasks.remove(d2)
        tasks.daemon_tasks.append(d2)

        tasks.terminate(None)

        self.assertEqual(d2.state, State.ENDED,
                         "one failing stop must not skip the remaining "
                         "tasks: their logs and status would be lost")
        self.assertEqual(tasks.status, TestStatus.FAIL)
        # keep interpreter shutdown quiet: __del__ stops the container
        d1.container.stop.side_effect = None


class TestRequireChainScheduling(unittest.TestCase):
    """Regression: a long require.started chain must fully schedule."""

    CHAIN_LEN = 12

    def _chain_defs(self):
        defs = [{"name": "d0", "image": "busybox", "daemon": True}]
        prev = "d0"
        for i in range(1, self.CHAIN_LEN + 1):
            defs.append({
                "name": f"t{i}",
                "image": "busybox",
                "require": [{"started": {"task": prev, "wait": 0.05}}],
            })
            prev = f"t{i}"
        return defs

    def test_all_tasks_of_require_chain_get_scheduled(self):
        granularity = tasks_list_module.TIMEOUT_GRANULARITY
        tasks_list_module.TIMEOUT_GRANULARITY = 0.02
        try:
            tasks, ctrl = make_tasks_list(self._chain_defs(), timeout=2)
            tasks.run()
        finally:
            tasks_list_module.TIMEOUT_GRANULARITY = granularity

        started = [t for t in tasks if t.start_time]
        self.assertEqual(len(tasks.pending_tasks), 0,
                         "all chained tasks must be scheduled")
        self.assertEqual(len(started), self.CHAIN_LEN + 1)


if __name__ == "__main__":
    unittest.main()
