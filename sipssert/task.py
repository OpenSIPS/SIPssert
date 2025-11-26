#!/usr/bin/env python
##
## This file is part of the SIPssert Testing Framework project
## Copyright (C) 2023 OpenSIPS Solutions
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.
##

"""This file is the manager of a Docker container"""

import re
import os
import time
from sipssert import logger
from sipssert import dependencies
from sipssert.state import State
import docker

class Task():
    
    default_image = None
    default_daemon = False
    default_config_file = None
    default_mount_point = '/home'
    default_stop_timeout = 0
    default_console_log = False

    def __init__(self, test_dir, configuration):
        self.config = configuration
        self.network = self.config.get("network", None)
        self.networks = self.config.get("networks", [])
        self.controller = None
        self.test_dir = test_dir
        self.volumes = self.config.get("volumes", {})
        self.logs_dir = None
        self.container = None
        self.root_password = None
        self.start_time = None
        self.stop_signal = None
        self.name = self.config.get("name", self.__class__.__name__)
        self.set_container_name(self.name)
        self.log = logger.IdenfierAdapter(self.name)
        self.image = self.config.get("image", self.default_image)
        self.ip = self.config.get("ip")
        self.entrypoint = self.config.get("entrypoint")
        self.resolve_networks()
        self.healthcheck = self.config.get("healthcheck", {"test": []})
        self.checklogs = self.get_checklogs()
        self.extra_hosts = self.config.get("extra_hosts", {})
        self.sysctls = self.config.get("sysctls", {})
        self.deps = dependencies.parse_dependencies(self.config.get("require"))
        # keep this for backwards compatibility
        self.delay_start = self.config.get("delay_start", 0)
        if int(self.delay_start) != 0:
            self.deps.append(dependencies.TaskDepDelay(self.delay_start))
        logging = self.config.get("logging")
        self.console_log = logging.get("console", self.default_console_log) \
                if isinstance(logging, dict) else self.default_console_log
        self.ready_deps = dependencies.parse_dependencies(self.config.get("ready"))
        self.stop_timeout = self.config.get("stop_timeout", self.default_stop_timeout)
        self.mount_point = self.config.get("mount_point", self.default_mount_point)
        self.config_file = self.config.get("config_file", self.default_config_file)
        if self.config_file and not os.path.isabs(self.config_file):
            self.config_file = os.path.join(self.mount_point, self.config_file)
        self.labels = self.parse_labels()
        self.daemon = self.config.get("daemon", self.default_daemon)
        if self.image is None:
            raise Exception(f"task {self.name} does not have an image available")
        self.logs_ok = True
        self.exit_code = None
        self.state = State.PENDING

    def __repr__(self):
        return self.name

    def resolve_networks(self):
        self.ports = self.get_ports()
        if self.networks and not isinstance(self.networks, list):
            self.networks = [ self.networks ]
        self.host_network = self.get_net_mode()
        if self.host_network:
            if self.ports:
                #self.log.warn("'port'/'ports' are incompatible with 'host' network")
                self.ports = None
            # if we have a host network, then no other networks can be used
            if self.networks and len(self.networks) > 0:
                self.log.warn(self.networks)
                nets = self.networks
                self.networks = None
                for network in nets:
                    if not 'disabled' in network or not network['disabled']:
                        self.log.warn("'host' network used - ignoring 'networks' settings")
                        return
            return
        nets = []
        if self.network:
            nets.append((self.network, self.ip))
        for net in self.networks:
            if isinstance(net, str):
                nets.append((net, None))
            else:
                if "network" in net:
                    if "disabled" in net and net.disabled:
                        continue
                    ip = net["ip"] if "ip" in net else None
                    nets.append((net['network'], ip))

        self.networks = nets

    def set_container_name(self, name):
        self.container_name = re.sub(r'[^a-zA-Z0-9_\.\-]', "_", name)

    def set_logs_dir(self, path):
        self.logs_dir = path

    def add_volume_dir(self, path, dest=None, mode="ro"):
        mount_point = dest if dest else self.mount_point
        self.log.info("mounting {} to {}".format(path, mount_point))
        self.volumes[path] = {
                "bind": mount_point,
                "mode": mode
        }

    def parse_labels(self):
        labels = self.config.get("labels", [])
        if not isinstance(labels, list):
            labels = [labels]
        label = self.config.get("label")
        if label:
            labels.append(label)
        return labels

    def match(self, name):
        return self.name == name or name in self.labels

    def create(self, controller, prefix=None):
        self.controller = controller
        args = self.get_args()

        if prefix:
            self.set_container_name(prefix + "." + self.container_name)

        env = self.get_task_env()
        # make sure the image is available
        try:
            self.controller.docker.images.get(self.image);
        except docker.errors.ImageNotFound as e:
            self.log.info(f"pulling image {self.image}")
            self.controller.docker.images.pull(self.image)

        self.args_dict = { 'image': self.image,
                           'command': args,
                           'entrypoint': self.entrypoint,
                           'detach': True,
                           'healthcheck': self.healthcheck,
                           'volumes': self.volumes,
                           'ports': self.ports,
                           'name': self.container_name,
                           'environment': env,
                           'stop_signal': self.stop_signal,
                           'network_mode': self.host_network,
                           'extra_hosts': self.extra_hosts,
                           'sysctls': self.sysctls
                          }

        self.log.info("container {} prepared".format(self.container_name))
        self.state = State.CREATED

    def get_task_args(self):
        return []

    def get_config_args(self):
        """Returns arguments specified in the config"""
        if "args" in self.config:
            args = self.config["args"]
            if isinstance(args, int):
                args = [str(args)]
            elif not isinstance(args, list):
                args = args.split(" ")
            else:
                args = [ str(x) for x in args ]
        else:
            args = []
        return args

    def parse_port(self, p):
        if isinstance(p, str):
            return p.split("/")
        else:
            return p, None

    def get_ports(self):
        r = {}
        if "ports" in self.config:
            for p in self.config["ports"]:
                port, proto = self.parse_port(p)
                r[p] = port
        if "port" in self.config:
            p = self.config["port"]
            port, proto = self.parse_port(p)
            r[p] = port
        return r
    

    def get_args(self):
        return self.get_task_args() + self.get_config_args()

    def parse_env_file(self, env_file):
        env_file_dict = {}
        path = os.path.join(self.test_dir, env_file)

        if not os.path.exists(path):
            self.log.error(f"environment file {path} does not exist")
            return {}

        with open(path, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                key, value = line.strip().split('=', 1)
                env_file_dict[key] = value
        return env_file_dict

    def get_task_env(self):
        if "env_file" in self.config:
            env_file_dict = self.parse_env_file(self.config["env_file"])
        else:
            env_file_dict = {}
        
        return self.config.get("env", env_file_dict)

    def run(self):
        self.log.debug(f"running {self.image}: {self.args_dict['command']}")
        self.container = self.controller.docker.containers.create(**self.args_dict)

        if not self.host_network:
            bridge = False
            for network in self.networks:
                if network == "bridge":
                    bridge = True
                try:
                    self.controller.docker.networks.get(network[0]).\
                            connect(self.container, ipv4_address = network[1])
                    if network[1]:
                        self.log.debug("attached ip {} in network {}".format(network[1], network[0]))
                    else:
                        self.log.debug("attached to network {}".format(network[0]))
                except docker.errors.APIError as err:
                    self.log.exception(err)
                    raise err
            if not bridge:
                try:
                    self.controller.docker.networks.get("bridge").disconnect(self.container)
                except docker.errors.APIError as err:
                    self.log.exception(err)
        self.container.start()
        self.start_time = time.time()
        self.state = State.ACTIVE
        self.log.info("started")

    def get_net_mode(self):
        if not self.network and len(self.networks) == 0:
            return "host"
        return "host" if self.network == "host" else None

    def stop(self):
        if self.controller and self.controller.no_delete:
            return
        self.container.stop(timeout=self.stop_timeout)

    def get_exit_code(self):
        if self.exit_code is None:
            self.update()
            self.exit_code = int(self.container.attrs["State"]["ExitCode"])
        return self.exit_code

    def update(self):
        self.container.reload()

    def remove(self):
        if self.container:
            self.container.stop()
            if self.controller and not self.controller.no_delete:
                self.log.debug("removing container")
                self.container.remove(v=True)
            self.container = None

    def write(self, suffix, data):
        if not self.logs_dir:
            return
        path = os.path.join(self.logs_dir, f"{self.name}.{suffix}")
        with open(path, 'w') as f:
            f.write(data)

    def write_logs(self):
        logs = self.container.logs().decode('UTF-8')
        self.write("log", logs)
        if self.console_log:
            self.log.debug(logs)
        self.log.debug("logs fetched")

    def write_status(self):
        status = self.get_exit_code()
        self.write("status", str(status))
        if status == 0:
            self.log.debug("exited with status {}".format(status))
        else:
            self.log.error("exited with status {}".format(status))

    def get_checklogs(self):
        checklogs = self.config.get("checklogs", {})
        if isinstance(checklogs, str):
            return {"all": checklogs.split(" "), "none": []}
        elif isinstance(checklogs, list):
            return {"all": [str(x) for x in checklogs], "none": []}
        elif isinstance(checklogs, dict):
            all = checklogs.get("all", [])
            none = checklogs.get("none", [])
            if isinstance(all, str):
                all = all.split(" ")
            if isinstance(none, str):
                none = none.split(" ")
            return {"all": all, "none": none}
        else:
            return {"all": [], "none": []}

    def check_logs(self):
        logs = self.container.logs().decode("UTF-8")
        self.log.info(self.checklogs)
        for rule in self.checklogs["all"]:
            try:
                if isinstance(rule, dict):
                    pattern = rule.get("expr", "")
                    expected = rule.get("cnt", None)

                    if not pattern:
                        self.log.error("logs check: empty pattern in rule")
                        return False

                    matches = re.findall(pattern, logs)
                    count = len(matches)

                    if expected is not None and count != expected:
                        self.log.error(
                            f"logs check failed for {pattern}; "
                            f"expected {expected} matches, got {count}"
                        )
                        return False
                    elif expected is None and count == 0:
                        self.log.error(
                            f"logs check failed for {pattern}; should match"
                        )
                        return False
                else:
                    pattern = rule
                    if not re.search(pattern, logs):
                        self.log.error(
                            f"logs check failed for {pattern}; should match"
                        )
                        return False

            except Exception as e:
                self.log.error(f"error while checking logs: {e}")
                return False


        for regex in self.checklogs["none"]:
            try:
                if re.search(regex, logs):
                    self.log.error(f"logs check failed for {regex}; shouldn't match")
                    return False
            except Exception as e:
                self.log.error(f"error while checking logs: {e}")
                return False
        return True

    def has_finished(self):
        return self.state == State.ENDED

    def finish(self):
        if self.has_finished():
            return
        self.logs_ok = self.check_logs()
        self.write_logs()
        self.write_status()
        self.end_time = time.time()
        self.state = State.ENDED
        self.remove()

    def satisfied(self, task_list, current_time):
        for dep in self.deps:
            if not dep.satisfied(self, task_list, current_time):
                return False
        return True

    def ready(self, task_list, current_time):
        for dep in self.ready_deps:
            if not dep.satisfied(self, task_list, current_time):
                return False
        return True
    
    def healthy(self):
        try:
            inspect_results = docker.APIClient().inspect_container(self.container_name)
        except docker.errors.APIError as e:
            self.log.debug(f"Error while inspecting container: {e}")
            return False
        status = inspect_results['State'].get('Status', None)
        if not status or status == 'created':
            return False
        health = inspect_results['State'].get('Health', None)
        if status == 'running' and not health:
            return True
        if not health:
            return False
        if health['Status'] == 'healthy':
            self.log.debug("task is healthy")
        return health['Status'] == 'healthy'

    def __del__(self):
        self.remove()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
