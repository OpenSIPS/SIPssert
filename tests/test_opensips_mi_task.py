#!/usr/bin/env python
"""Regression tests pinning that the opensips-mi task can run an arbitrary
python script with forwarded arguments (via the base task `args:` support).

This is what lets the rtp_relay ng_checker run as `type: opensips-mi` instead of
a bespoke generic task.
"""

import importlib
import unittest


def make(config=None):
    cfg = {"name": "ng checker"}
    if config:
        cfg.update(config)
    mod = importlib.import_module("sipssert.tasks.opensips-mi")
    return mod.OpenSIPSMITask("/test", cfg)


class TestOpenSIPSMIScript(unittest.TestCase):

    def test_script_relative_is_mounted_under_home(self):
        t = make({"script": "scripts/ng_checker.py"})
        self.assertEqual(t.get_task_args(), ["/home/scripts/ng_checker.py"])

    def test_script_absolute_is_left_untouched(self):
        t = make({"script": "/abs/checker.py"})
        self.assertEqual(t.get_task_args(), ["/abs/checker.py"])

    def test_script_args_are_forwarded_after_script(self):
        t = make({
            "script": "scripts/ng_checker.py",
            "args": ["/caps/ng.pcap", "savpf", "--ng-port", "22222"],
        })
        self.assertEqual(
            t.get_args(),
            ["/home/scripts/ng_checker.py",
             "/caps/ng.pcap", "savpf", "--ng-port", "22222"],
        )

    def test_args_with_special_chars_pass_through_as_argv(self):
        # args are argv elements (no shell), so special chars survive verbatim
        t = make({"script": "scripts/c.py", "args": ["a b", "x\\y", "--re=$x"]})
        self.assertEqual(
            t.get_args(),
            ["/home/scripts/c.py", "a b", "x\\y", "--re=$x"],
        )

    def test_integer_args_are_stringified(self):
        t = make({"script": "scripts/c.py", "args": [22222]})
        self.assertEqual(t.get_args(), ["/home/scripts/c.py", "22222"])

    def test_no_script_keeps_mi_cli_fallback(self):
        t = make({"mi_ip": "192.168.52.1", "mi_port": 8888})
        self.assertEqual(
            t.get_task_args(),
            ["-t", "http", "-i", "192.168.52.1", "-p", "8888"],
        )


if __name__ == "__main__":
    unittest.main()
