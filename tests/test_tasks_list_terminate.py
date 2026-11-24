#!/usr/bin/env python
"""Unit tests for the termination status of a task list (sipssert.tasks_list).

Regression test: a scenario in which some tasks were never scheduled
(pending) silently reported success. terminate() only derived the
scenario status from the exit codes of the tasks that had been started
(daemons exiting 0 on forced stop turned the whole scenario green), and
the unscheduled tasks influenced nothing but a warning line.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from sipssert import logger
from sipssert.tasks_list import TasksList
from sipssert.testing import TestStatus

LOG_DIR = tempfile.mkdtemp(prefix="sipssert_test_")


def setUpModule():
    logger.init_logger({"file": os.path.join(LOG_DIR, "test.log"),
                        "level": "CRITICAL"}, None)


def tearDownModule():
    shutil.rmtree(LOG_DIR, ignore_errors=True)


def make_tasks_list(defs):
    """Builds a real TasksList with a mocked docker controller."""
    ctrl = MagicMock()
    cfg = {"tasks": defs}
    logs_dir = tempfile.mkdtemp(prefix="sipssert_test_")
    tasks = TasksList("tasks", "/test", logs_dir, cfg, ctrl,
                      None, None, {}, {}, "prefix", {})
    return tasks, ctrl


def mock_started_daemon(task, exit_code):
    """Mimics a daemon task that has been started and then stopped.

    In the real flow the docker container object only appears after
    Task.run(), so the tests inject a mock directly.
    """
    task.container = MagicMock()
    task.container.attrs = {"State": {"ExitCode": exit_code}}
    task.container.logs.return_value = b""
    return task


class TestTerminateStatus(unittest.TestCase):

    def test_pending_tasks_mark_scenario_failed(self):
        tasks, _ = make_tasks_list([
            {"name": "t1", "image": "busybox"},
            {"name": "t2", "image": "busybox"},
        ])
        # nothing was ever started: all tasks are still pending
        self.assertEqual(len(tasks.pending_tasks), 2)
        tasks.terminate(None)
        self.assertEqual(tasks.status, TestStatus.FAIL,
                         "unscheduled tasks must fail the scenario")

    def test_daemon_exit_zero_cannot_mask_pending_fail(self):
        tasks, _ = make_tasks_list([
            {"name": "d1", "image": "busybox", "daemon": True},
            {"name": "t1", "image": "busybox"},
        ])
        daemon = mock_started_daemon(tasks.get_task("d1"), exit_code=0)
        tasks.pending_tasks.remove(daemon)
        tasks.daemon_tasks.append(daemon)
        tasks.terminate(None)
        self.assertEqual(tasks.status, TestStatus.FAIL,
                         "a clean daemon exit must not mask unscheduled tasks")

    def test_running_task_timeout_marks_tout(self):
        tasks, _ = make_tasks_list([
            {"name": "t1", "image": "busybox"},
        ])
        task = mock_started_daemon(tasks.get_task("t1"), exit_code=0)
        tasks.pending_tasks.remove(task)
        tasks.running_tasks.append(task)
        tasks.terminate(None)
        self.assertEqual(tasks.status, TestStatus.TOUT)

    def test_failed_daemon_with_pending_stays_failed(self):
        tasks, _ = make_tasks_list([
            {"name": "d1", "image": "busybox", "daemon": True},
            {"name": "t1", "image": "busybox"},
        ])
        daemon = mock_started_daemon(tasks.get_task("d1"), exit_code=1)
        tasks.pending_tasks.remove(daemon)
        tasks.daemon_tasks.append(daemon)
        tasks.terminate(None)
        self.assertEqual(tasks.status, TestStatus.FAIL)


if __name__ == "__main__":
    unittest.main()
