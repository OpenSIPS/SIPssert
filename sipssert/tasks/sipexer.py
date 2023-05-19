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

"""Generic SipExer class"""

import os
from sipssert import logger
from sipssert.task import Task

class SipExerTask(Task):

    """Generic SipExer class"""

    default_image = "yaroslavonline/sipexer"
    default_daemon = False

    def __init__(self, test_dir, config):
        super().__init__(test_dir, config)

        self.port = config.get("port", None)

        # auth section
        self.auth = config.get("auth")
        self.auth_user = self.auth.get("user") if isinstance(self.auth, dict) else None
        self.auth_password = self.auth.get("password") if isinstance(self.auth,  dict) else None
        self.auth_ha1 = self.auth.get("ha1") if isinstance(self.auth, dict) else None

        # register section
        self.register = config.get("register")
        self.register_expires = self.register.get("expires") if isinstance(self.register, dict) else None
        self.register_party = self.register.get("party") if isinstance(self.register, dict) else None
        
        # contact section
        self.contact = config.get("contact")
        self.contact_build = self.contact.get("build") if isinstance(self.contact, dict) else None
        self.contact_uri = self.contact.get("uri") if isinstance(self.contact, dict) else None

        # from section
        self.from_ = config.get("from")
        self.from_uri = self.from_.get("uri") if isinstance(self.from_, dict) else None
        self.from_domain = self.from_.get("domain") if isinstance(self.from_, dict) else None
        self.from_user = self.from_.get("user") if isinstance(self.from_, dict) else None

        # to section
        self.to = config.get("to")
        self.to_uri = self.to.get("uri") if isinstance(self.to, dict) else None
        self.to_domain = self.to.get("domain") if isinstance(self.to, dict) else None
        self.to_user = self.to.get("user") if isinstance(self.to, dict) else None

        # ruri section
        self.ruri = config.get("ruri") 
        self.ruri_uri = self.ruri.get("uri") if isinstance(self.ruri, dict) else None
        self.ruri_user = self.ruri.get("user") if isinstance(self.ruri, dict) else None
        self.ruri_set_domains = self.ruri.get("set_domains") if isinstance(self.ruri, dict) else None
        self.ruri_set_user = self.ruri.get("set_user") if isinstance(self.ruri, dict) else None

        # message section
        self.message = config.get("message")
        self.message_method = self.message.get("method") if isinstance(self.message, dict) else None
        self.message_content_type = self.message.get("content_type") if isinstance(self.message, dict) else None
        self.message_body = self.message.get("body") if isinstance(self.message, dict) else None
        self.message_no_body = self.message.get("no_body") if isinstance(self.message, dict) else None

        # extra headers
        self.extra = config.get("extra")
        self.extra_headers = []
        if isinstance(self.extra, dict):
            self.extra_headers = [(k, v) for k, v in self.extra.items()]

        # fields
        self.fields = config.get("fields")
        self.field_values = []
        if isinstance(self.fields, dict):
            self.field_values = [(k, v) for k, v in self.fields.items()]
        
        # other
        self.user_agent = config.get("user_agent")
        self.no_parse = config.get("no_parse")
        self.no_crlf = config.get("no_crlf")

        # timeout section
        self.timeout = config.get("timeout") 
        self.timeout_session = self.timeout.get("session") if isinstance(self.timeout, dict) else None 
        self.timeout_receive = self.timeout.get("receive") if isinstance(self.timeout, dict) else None 
        self.timeout_write = self.timeout.get("write") if isinstance(self.timeout, dict) else None 

        # timer section
        self.timer = config.get("timer") 
        self.timer_t1 = self.timer.get("t1") if isinstance(self.timer, dict) else None 
        self.timer_t2 = self.timer.get("t2") if isinstance(self.timer, dict) else None 

        # transport section
        self.transport = config.get("transport")
        self.transport_udp_dial = None
        self.transport_tls_key = None
        self.transport_tls_certificate = None
        self.transport_tls_insecure = False
        self.transport_wss_origin = None
        self.transport_wss_proto = None

        if isinstance(self.transport, dict):
            # udp
            transport_udp = self.transport.get("udp")
            if isinstance(transport_udp, dict):
                self.transport_udp_dial = transport_udp.get("dial")
            # tls
            transport_tls = self.transport.get("tls")
            if isinstance(transport_tls, dict):
                self.transport_tls_key = transport_tls.get("key")
                self.transport_tls_certificate = transport_tls.get("certificate")
                self.transport_tls_insecure = transport_tls.get("insecure")
            # wss
            transport_wss = self.transport.get("wss")
            if isinstance(transport_wss, dict):
                self.transport_wss_origin = transport_wss.get("origin")
                self.transport_wss_proto = transport_wss.get("proto")

        self.template = config.get("template")
        self.template_fields_file = self.template.get("fields_file") if isinstance(self.template, dict) else None
        self.template_fields_eval = self.template.get("fields_eval") if isinstance(self.template, dict) else None
        self.template_raw = self.template.get("raw") if isinstance(self.template, dict) else None
        self.template_file = self.template.get("file") if isinstance(self.template, dict) else None
        self.template_body_file = self.template.get("body_file") if isinstance(self.template, dict) else None

        self.logging = config.get("logging")
        self.logging_verbose = self.logging.get("verbose") if isinstance(self.logging, dict) else None
        self.logging_color = self.logging.get("color") if isinstance(self.logging, dict) else None

        self.target = config.get("target")

        if self.template_file and not os.path.isabs(self.template_file):
            self.template_file = os.path.join(self.mount_point, self.template_file)
        if self.template_body_file and not os.path.isabs(self.template_body_file):
            self.template_body_file = os.path.join(self.mount_point, self.template_body_file)
        if self.template_fields_file and not os.path.isabs(self.template_fields_file):
            self.template_fields_file = os.path.join(self.mount_point, self.template_fields_file)
            
    def get_task_args(self):

        """Returns the arguments the container uses to start"""

        args = []

        # nagios exit codes
        args.append("-nagios")

        # handle config
        if self.message_method:
            if (self.message_method.lower() == "options"):
                args.append("-o")
            elif (self.message_method.lower() == "publish"):
                args.append("-publish")
            elif (self.message_method.lower() == "register"):
                args.append("-r")
            elif (self.message_method.lower() == "invite"):
                args.append("-i")
            elif (self.message_method.lower() == "info"):
                args.append("-info")
            elif (self.message_method.lower() == "notify"):
                args.append("-notify")
            elif (self.message_method.lower() == "subscribe"):
                args.append("-subscribe")
            elif (self.message_method.lower() == "message"):
                args.append("-m")
            else:
                args.append("-mt")
                args.append(str(self.message_method))

        if self.message_content_type:
            args.append("-ct")
            args.append(str(self.message_content_type))
            
        if self.message_body:
            args.append("-mb")
            args.append(str(self.message_body))
            
        if self.message_no_body:
            args.append("-no-body")
            
        if self.auth_user:
            args.append("-au")
            args.append(str(self.auth_user))

        if self.auth_password:
            args.append("-ap")
            args.append(str(self.auth_password))

        if self.auth_ha1:
            args.append("-ha1")

        if self.register_expires:
            args.append("-ex")
            args.append(str(self.register_expires))
        
        if self.register_party:
            args.append("-register-party")
        
        if self.from_uri:
            args.append("-from-uri")
            args.append(str(self.from_uri))

        if self.from_domain:
            args.append("-fd")
            args.append(str(self.from_domain))

        if self.from_user:
            args.append("-fu")
            args.append(str(self.from_user))

        if self.to_uri:
            args.append("-to-uri")
            args.append(str(self.to_uri))

        if self.to_domain:
            args.append("-td")
            args.append(str(self.to_domain))

        if self.to_user:
            args.append("-tu")
            args.append(str(self.to_user))

        if self.ruri_uri:
            args.append("-ru")
            args.append(str(self.ruri_uri))

        if self.ruri_user:
            args.append("-rn")
            args.append(str(self.ruri_user))

        if self.ruri_set_domains:
            args.append("-sd")

        if self.ruri_set_user:
            args.append("-su")

        if self.contact_build:
            args.append("-cb")
        
        if self.contact_uri:
            args.append("-cu")
            args.append(str(self.contact_uri))

        for name, body in self.extra_headers:
            args.append("-xh")
            args.append("{0}:{1}".format(name, body))

        for name, body in self.field_values:
            args.append("-fv")
            args.append("{0}:{1}".format(name, body))

        if self.template_fields_eval:
            args.append("-fe")
            
        if self.template_fields_file:
            args.append("-ff")
            args.append(str(self.template_fields_file))

        if self.template_file:
            args.append("-tf")
            args.append(str(self.template_file))

        if self.template_body_file:
            args.append("-tbf")
            args.append(str(self.template_body_file))

        if self.template_raw:
            args.append("-raw")

        if self.ip and self.port:
            args.append("-laddr")
            args.append("{0}:{1}".format(self.ip, self.port))
        elif self.port:
            args.append("-laddr")
            args.append(":{0}".format(self.port))

        if self.user_agent:
            args.append("-ua")
            args.append(str(self.user_agent))

        if self.logging_verbose:
            args.append("-vl")
            args.append(str(self.logging_verbose))

        if self.logging_color:
            args.append("-co")
            args.append("-com")

        if self.transport_udp_dial:
            args.append("-connect-udp")

        if self.transport_tls_key:
            args.append("-tk")
            args.append(str(self.transport_tls_key))

        if self.transport_tls_certificate:
            args.append("-tc")
            args.append(str(self.transport_tls_certificate))

        if self.transport_tls_insecure:
            args.append("-ti")

        if self.transport_wss_origin:
            args.append("-wso")
            args.append(str(self.transport_wss_origin))

        if self.transport_wss_proto:
            args.append("-wsp")
            args.append(str(self.transport_wss_proto))

        if self.no_crlf:
            args.append("-no-crlf")

        if self.no_parse:
            args.append("-no-parse")

        if self.timeout_session:
            args.append("-sw")
            args.append(str(self.timeout_session))

        if self.timeout_receive:
            args.append("-timeout")
            args.append(str(self.timeout_receive))

        if self.timeout_write:
            args.append("-timeout-write")
            args.append(str(self.timeout_write))

        if self.timer_t1:
            args.append("-timer-t1")
            args.append(str(self.timer_t1))

        if self.timer_t2:
            args.append("-timer-t2")
            args.append(str(self.timer_t2))

        if self.target:
            args.append(str(self.target))

        return args

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
