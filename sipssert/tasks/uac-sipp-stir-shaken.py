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

"""SIPP User-Agent Client class"""

from sipssert.config import ConfigParamNotFound
from sipssert.tasks.sipp import SIPPTask
import jwt
import time

class UacSIPPStirShakenTask(SIPPTask):

    """UAC SIPP class"""

    default_image = "allomediadocker/sipp:3.7.1"
    default_stir_shaken_private_key = b"-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIIOvgr23lbJ5rIOhiF+LR/VU4piEc1EYLT1CF5SN5HtZoAoGCCqGSM49AwEHoUQDQgAEuyQP0hteN1oKDUxo/2zvTp+0ppJ2IntNSdu36QFsUPDsCWlr4iTUMsjPtD+XQ58xQEf6n/zTE9cwZhs46NJWdA==\n-----END EC PRIVATE KEY-----"
    default_stir_shaken_info = "https://certs.example.org/cert.pem"
    default_stir_shaken_alg = "ES256"
    default_stir_shaken_ppt = "shaken"
    default_stir_shaken_typ = "passport"
    default_stir_shaken_attest = "A"
    default_stir_shaken_origid = "4437c7eb-8f7a-4f0e-a863-f53a0e60251a"

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)
        self.remote = config.get("remote")
        if not self.remote and not self.proxy:
            raise ConfigParamNotFound("proxy")
        if not self.proxy:
            self.proxy = self.remote
            self.remote = None
        elif self.remote:
            # we have both - swap them
            tmp = self.remote
            self.remote = self.proxy
            self.proxy = tmp
        self.caller = config.get("caller", self.username)
        # overwrite the username/service with the destination 
        if not self.service:
            self.service = config.get("destination", self.username)

        # parse stir and shaken configuration
        self.stir_shaken_private_key = config.get("stir_shaken_private_key", self.default_stir_shaken_private_key)
        self.stir_shaken_info = config.get("stir_shaken_info", self.default_stir_shaken_info)
        self.stir_shaken_alg = config.get("stir_shaken_alg", self.default_stir_shaken_alg)
        self.stir_shaken_ppt = config.get("stir_shaken_ppt", self.default_stir_shaken_ppt)
        self.stir_shaken_typ = config.get("stir_shaken_typ", self.default_stir_shaken_typ)
        self.stir_shaken_attest = config.get("stir_shaken_attest", self.default_stir_shaken_attest)
        self.stir_shaken_origid = config.get("stir_shaken_origid", self.default_stir_shaken_origid)

    def generate_jwt(self):
        return jwt.encode(
            {
                "dest": {
                    "tn": [
                        self.service
                    ]
                },
                "iat": int(time.time()),
                "orig": {
                    "tn": self.caller
                },
                "origid": self.stir_shaken_origid
            },
            self.stir_shaken_private_key,
            algorithm=self.stir_shaken_alg,
            headers=
            {
                "alg": self.stir_shaken_alg,
                "ppt": self.stir_shaken_ppt,
                "typ": self.stir_shaken_typ,
                "x5u": self.stir_shaken_info
            },
        )
        

    def get_task_args(self):

        """Returns the arguments the container uses to start"""

        args = super().get_task_args()

        jwt = self.generate_jwt()
        if jwt:
            args.append("-key")
            args.append("stir_and_shaken_jwt")
            args.append(jwt)
            args.append("-key")
            args.append("stir_and_shaken_info")
            args.append(self.stir_shaken_info)
            args.append("-key")
            args.append("stir_shaken_alg")
            args.append(self.stir_shaken_alg)
            args.append("-key")
            args.append("stir_shaken_ppt")
            args.append(self.stir_shaken_ppt)

        if not self.config_file:
            args.append("-sn")
            args.append("uac")
        if self.caller:
            args.append("-key")
            args.append("caller")
            args.append(self.caller)
        if self.remote:
            args.append("-rsa")
            args.append(self.remote)

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
