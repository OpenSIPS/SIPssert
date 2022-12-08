#!/usr/bin/env python
##
## TODO: update project's name
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

import os
from datetime import datetime
from framework import logger
from framework import config
import time
import docker
import re


class Task():
    
    default_image = None
    default_daemon = False
    default_config_file = None
    default_mount_point = '/home'

    def __init__(self, configuration):
        self.config = configuration
        self.net_mode = self.config.get("network", None)
        self.finished = False
        self.controller = None
        self.test_dir = None
        self.volumes = {}
        self.logs_dir = None
        self.container = None
        self.root_password = None
        self.name = self.config.get("name", self.__class__.__name__)
        self.set_container_name(self.name)
        self.log = logger.IdenfierAdapter(self.name)
        self.image = self.config.get("image", self.default_image)
        self.ip = self.config.get("ip")
        self.delay_start = self.config.get("delay_start", 0)
        self.mount_point = self.config.get("mount_point", self.default_mount_point)
        self.config_file = self.config.get("config_file", self.default_config_file)
        if self.config_file and not os.path.isabs(self.config_file):
            self.config_file = os.path.join(self.mount_point, self.config_file)
        self.daemon = self.config.get("daemon", self.default_daemon)
        if self.image is None:
            raise Exception("task {} does not have an image available".
                    format(self.name))
        self.exit_code = None

    def __repr__(self):
        return self.name

    def set_container_name(self, name):
        self.container_name = re.sub(r'[^a-zA-Z0-9_\.\-]', "_", name)

    def set_logs_dir(self, path):
        self.logs_dir = path

    def add_volume_dir(self, path, dest=None, mode="ro"):
        self.volumes[path] = {
                "bind": dest if dest else self.mount_point,
                "mode": mode
        }

    def create(self, controller, prefix=None):
        self.controller = controller
        args = self.get_args()

        if prefix:
            self.set_container_name(prefix + "." + self.container_name)

        ports = self.get_ports()
        env = self.get_task_env()
        net_mode = self.get_net_mode()
        self.container = self.controller.docker.containers.create(
                self.image,
                self.get_args(),
                detach=True,
                volumes=self.volumes,
                ports=ports,
                name=self.container_name,
                environment=env,
                network_mode=net_mode)
        self.log.info("container {} created".format(self.container_name))
        self.log.debug("running {}: {}".format(self.image, args))

        if net_mode == "bridge" and self.ip:
            try:
                self.controller.docker.networks.get(self.net_mode).\
                        connect(self.container, ipv4_address = self.ip)
                self.log.debug("network attached")
            except docker.errors.APIError as err:
                self.log.exception(err)

    def get_task_args(self):
        return []

    def get_extra_params(self):
        """Returns extra parameters from the config"""
        if "extra_params" in self.config:
            extra_params = self.config["extra_params"].split(" ")
        else:
            extra_params = []
        return extra_params

    def get_ports(self):
        r = {}
        if "ports" in self.config:
            for p in self.config["ports"]:
                port, proto = p.split("/")
                r[p] = port
        return r
    

    def get_args(self):
        return self.get_task_args() + self.get_extra_params()

    def get_task_env(self):
        return {}

    def run(self):
        time.sleep(self.delay_start)
        try:
            self.container.start()
            self.log.info("started")
        except docker.errors.APIError as err:
            self.log.exception(err)
        

    def get_net_mode(self):
        if not self.net_mode or self.netMode == "host":
            return "host"
        else:
            return "bridge"

    def stop(self):
        self.container.stop()
        self.log.info("container stopped")

    def get_exit_code(self):
        if not self.exit_code:
            self.exit_code = self.container.attrs["State"]["ExitCode"]
        return self.exit_code

    def update(self):
        self.container.reload()

    def remove(self):
        #self.container.remove()
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
        self.log.debug("logs fetched")

    def write_status(self):
        status = self.get_exit_code()
        self.write("status", str(status))
        self.log.debug("exited with status {}".format(status))

    def has_ended(self):
        if self.daemon:
            return False
        self.update()
        return self.container.status == "exited"

    def wait_end(self):
        while not self.has_ended(self):
            time.sleep(0.1)

    def finish(self):
        if self.finished:
            return
        self.write_logs()
        self.write_status()
        self.finished = True

    def __del__(self):
        if self.container:
            self.container.stop()
            self.container.remove()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
