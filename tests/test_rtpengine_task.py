#!/usr/bin/env python
"""Unit tests for the reusable rtpengine task (sipssert.tasks.rtpengine)."""

import importlib
import unittest


def make(config=None):
    cfg = {"name": "rtpengine"}
    if config:
        cfg.update(config)
    mod = importlib.import_module("sipssert.tasks.rtpengine")
    return mod.RTPEngineTask("/test", cfg)


class TestRTPEngineDefaults(unittest.TestCase):

    def test_class_resolves_from_type(self):
        # the framework derives the class name from the task `type`: the
        # normalized class name must be "rtpenginetask" so `type: rtpengine`
        # selects it.
        mod = importlib.import_module("sipssert.tasks.rtpengine")
        cls = mod.RTPEngineTask
        normalized = "".join(c for c in "rtpengine" if c.isalnum()) + "task"
        self.assertEqual(cls.__name__.lower(), normalized)

    def test_defaults(self):
        t = make()
        self.assertTrue(t.daemon)               # media proxy runs as a daemon
        self.assertEqual(t.stop_timeout, 3)
        self.assertEqual(t.image, "debian:trixie-slim")
        self.assertEqual(t.entrypoint, "sh")
        self.assertEqual(str(t.ng_port), "22222")
        self.assertEqual(t.interface, t.ip)     # interface defaults to ip
        self.assertEqual(t.ip, "127.0.0.1")
        self.assertEqual(str(t.table), "-1")

    def test_default_healthcheck_gates_on_ng_socket(self):
        t = make({"ng_port": 23456})
        self.assertEqual(t.healthcheck["test"], "ss -lnu | grep -q :23456")
        self.assertEqual(t.healthcheck["retries"], 120)

    def test_custom_healthcheck_is_preserved(self):
        hc = {"test": "true", "retries": 1}
        t = make({"healthcheck": hc})
        self.assertEqual(t.healthcheck, hc)


class TestRTPEngineRunCommand(unittest.TestCase):

    def test_run_command_has_required_flags(self):
        t = make({"ip": "192.168.52.4", "ng_port": "22222"})
        run = t.get_run_command()
        self.assertIn("exec rtpengine", run)
        self.assertIn("--table=-1", run)
        self.assertIn("--interface=192.168.52.4", run)
        self.assertIn("--listen-ng=192.168.52.4:22222", run)
        self.assertIn("--foreground", run)
        self.assertIn("--log-stderr", run)

    def test_ng_port_is_the_only_knob(self):
        t = make({"ng_port": "30000"})
        self.assertEqual(str(t.ng_port), "30000")
        self.assertIn(":30000", t.get_run_command())

    def test_base_port_is_not_aliased_to_ng_port(self):
        # `port` belongs to the base Task (container port publishing) and must
        # NOT silently retarget the ng control port.
        t = make({"port": 30000})
        self.assertEqual(str(t.ng_port), "22222")
        self.assertIn(":22222", t.get_run_command())

    def test_custom_interface_and_table(self):
        t = make({"ip": "10.0.0.1", "interface": "eth0/10.0.0.1",
                  "table": "0"})
        run = t.get_run_command()
        self.assertIn("--interface=eth0/10.0.0.1", run)
        self.assertIn("--table=0", run)

    def test_options_as_list_are_appended(self):
        t = make({"options": ["--delete-delay=0", "--no-fallback"]})
        run = t.get_run_command()
        self.assertIn("--delete-delay=0", run)
        self.assertIn("--no-fallback", run)

    def test_options_as_string_are_split(self):
        t = make({"options": "--delete-delay=0 --no-fallback"})
        run = t.get_run_command()
        self.assertIn("--delete-delay=0", run)
        self.assertIn("--no-fallback", run)


class TestRTPEngineSetup(unittest.TestCase):

    def test_install_commands_present_by_default(self):
        cmds = make().get_setup_commands()
        joined = " && ".join(cmds)
        self.assertIn("policy-rc.d", joined)
        self.assertIn("apt-get update", joined)
        self.assertIn("apt-get install", joined)
        self.assertIn("rtpengine-daemon", joined)
        self.assertIn("iproute2", joined)

    def test_install_disabled_skips_apt(self):
        self.assertEqual(make({"install": False}).get_setup_commands(), [])

    def test_custom_packages(self):
        cmds = make({"packages": ["rtpengine-daemon", "tcpdump"]}).get_setup_commands()
        joined = " ".join(cmds)
        self.assertIn("tcpdump", joined)
        self.assertNotIn("iproute2", joined)

    def test_task_args_chain_setup_then_run(self):
        args = make().get_task_args()
        self.assertEqual(args[0], "-c")
        self.assertEqual(len(args), 2)
        # the run command is the last link of the && chain
        self.assertTrue(args[1].rstrip().endswith("--log-stderr"))
        self.assertIn("apt-get install", args[1])
        self.assertLess(args[1].index("apt-get install"), args[1].index("exec rtpengine"))

    def test_task_args_when_install_disabled_is_only_run(self):
        args = make({"install": False}).get_task_args()
        self.assertEqual(args[0], "-c")
        self.assertNotIn("apt-get", args[1])
        self.assertIn("exec rtpengine", args[1])


class TestRTPEngineAdversarial(unittest.TestCase):

    def test_normalize_list_none_empty_str(self):
        t = make()
        self.assertEqual(t.normalize_list(None), [])
        self.assertEqual(t.normalize_list(""), [])
        self.assertEqual(t.normalize_list([]), [])

    def test_normalize_list_mixed_types(self):
        t = make()
        self.assertEqual(t.normalize_list(["a", 1]), ["a", "1"])

    def test_package_with_space_is_quoted(self):
        # a value containing a space must survive as a single shell token
        cmds = make({"packages": ["weird pkg"]}).get_setup_commands()
        install = [c for c in cmds if "install" in c][0]
        self.assertIn("'weird pkg'", install)

    def test_option_with_backslash_is_quoted(self):
        t = make({"options": ["--cfg=a\\b"]})
        run = t.get_run_command()
        # the backslash token must not be word-split away
        self.assertIn("a\\b", run)
        self.assertIn("--cfg=a\\b", "".join(t.normalize_options(["--cfg=a\\b"])))

    def test_option_with_special_chars_quoted(self):
        t = make({"options": ["--x=$(echo hi)"]})
        run = t.get_run_command()
        # must be quoted so the subshell is not evaluated by the container shell
        self.assertIn("'--x=$(echo hi)'", run)


if __name__ == "__main__":
    unittest.main()
