#!/usr/bin/env python
"""Unit tests for the tracer interface selection (sipssert.tracer.Tracer).

Regression test: with a single network named "host" the tracer must fall back
to the "any" pseudo-interface instead of passing "host" to tcpdump -i (a list
is compared against a string, which is always False, so tcpdump started with
a non-existent interface and produced no capture).
"""

import os
import shutil
import tempfile
import unittest

from sipssert import logger
from sipssert.tracer import Tracer

# Tracer.__init__() emits log records, so the global logger must be
# initialized before constructing a Tracer (otherwise logger.slog is None).
LOG_DIR = tempfile.mkdtemp(prefix="sipssert_test_")


def setUpModule():
    logger.init_logger({"file": os.path.join(LOG_DIR, "test.log")}, None)


def tearDownModule():
    shutil.rmtree(LOG_DIR, ignore_errors=True)


class TestTracerInterface(unittest.TestCase):
    """The tracer must pick a capture interface that actually exists."""

    def test_no_networks(self):
        t = Tracer(LOG_DIR, "capture", [], "t", {})
        self.assertEqual(t.interface, "any")

    def test_single_host_network(self):
        t = Tracer(LOG_DIR, "capture", ["host"], "t", {})
        self.assertEqual(t.interface, "any")

    def test_single_bridge_network(self):
        t = Tracer(LOG_DIR, "capture", ["br_net"], "t", {})
        self.assertEqual(t.interface, "br_net")

    def test_multiple_networks(self):
        t = Tracer(LOG_DIR, "capture", ["net_a", "net_b"], "t", {})
        self.assertEqual(t.interface, "any")

    def test_explicit_interface(self):
        t = Tracer(LOG_DIR, "capture", [], "t", {"interface": "eth1"})
        self.assertEqual(t.interface, "eth1")


if __name__ == "__main__":
    unittest.main()
