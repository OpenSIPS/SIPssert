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


"""Task used to run an API command"""

import uuid
import json
from framework.tasks.task import Task

class OSSAPITask(Task):

    """Class that implements the Task"""

    default_image = "badouralix/curl-jq"

    default_schema = "http"
    default_host = "127.0.0.1"
    default_port = 5000
    default_path = ""
    default_params = "{}"

    def __init__(self, config):
        super().__init__(config)

        self.resource = config["resource"]
        self.command = config["command"]
        self.schema = config.get("schema", self.default_schema)
        self.host = config.get("host", self.default_host)
        self.port = config.get("port", self.default_port)
        self.path = config.get("path", self.default_path)
        self.params = config.get("params", self.default_params)

    def get_task_args(self):

        command = """curl -X POST """ + \
                f"""{self.schema}://{self.host}:{self.port}/{self.path}/{self.resource} """ + \
                '''-H "Content-Type: application/json" ''' + \
                f'''-d '{{ "jsonrpc": 2.0, "method": "{self.command}", ''' + \
                f'''"params": {json.dumps(self.params)}, "id": "{uuid.uuid4()}" }}' ''' + \
                """2>/dev/null | jq -e 'if has("result") then .["result"] else .["error"] | halt_error(1) end'"""

        args = ["sh", "-c", command]

        return args

if __name__ == "__main__":
    t = OSSAPITask(".", {"resource":"pbx", "command":"getPBX"}, None, None)
    print(t.get_task_args())

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
