#!/usr/bin/env python
"""Unit tests for task network attachment in Task.run() (sipssert.task).

Regression test: the default-bridge detection compared a (network, ip)
tuple against the string "bridge", which is always False. As a result,
a task explicitly attached to the default "bridge" network was also
disconnected from it right before start, ending up without any network
at all ("Network is unreachable" inside the container).
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from sipssert import logger
from sipssert.task import Task

# Task.run() emits log records, so the global logger must be initialized
# before running the tasks (otherwise logger.slog is None).
LOG_DIR = tempfile.mkdtemp(prefix="sipssert_test_")


def setUpModule():
    logger.init_logger({"file": os.path.join(LOG_DIR, "test.log")}, None)


def tearDownModule():
    shutil.rmtree(LOG_DIR, ignore_errors=True)


def make_controller():
    """A controller mock whose docker networks.get() returns a distinct
    mock per network name, so tests can assert on per-network calls."""
    ctrl = MagicMock()
    nets = {}

    def get(name):
        if name not in nets:
            nets[name] = MagicMock()
        return nets[name]

    ctrl.docker.networks.get.side_effect = get
    ctrl.docker.images.get.return_value = MagicMock()  # image exists: no pull
    return ctrl, nets


def run_task(networks):
    ctrl, nets = make_controller()
    cfg = {"name": "nettest", "image": "busybox", "networks": networks}
    task = Task("/test", cfg)
    task.create(ctrl)
    task.run()
    return nets


class TestDefaultBridgeHandling(unittest.TestCase):
    """run() must keep the container attached to networks it asks for."""

    def test_bridge_network_stays_attached(self):
        nets = run_task(["bridge"])
        self.assertFalse(nets["bridge"].disconnect.called,
                         "container was disconnected from the bridge "
                         "network it explicitly requested")

    def test_other_network_disconnected_from_default_bridge(self):
        nets = run_task(["mynet"])
        self.assertTrue(nets["mynet"].connect.called)
        self.assertTrue(nets["bridge"].disconnect.called)


if __name__ == "__main__":
    unittest.main()
