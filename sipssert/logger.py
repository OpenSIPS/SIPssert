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

"""
logger.py - implements coloured logging for the opensips-cli project
"""

import os
import time
import logging

slog = None # pylint: disable=invalid-name

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    """formats a single message accorging to the settings"""
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):

    """Class that colors the logs"""

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    FORMAT = "$BOLD%(levelname)s$RESET: %(message)s"

    def __init__(self, name):
        global LOG_CONSOLE # pylint: disable=global-statement
        global LOG_FILE # pylint: disable=global-statement
        global LOG_TIMESTAMP # pylint: disable=global-statement

        logging.Logger.__init__(self, name)
        if LOG_TIMESTAMP:
            self.FORMAT = "%(asctime)s " + self.FORMAT

        file_format = formatter_message(self.FORMAT, False)
        file_formatter = ColoredFormatter(file_format, self.TIME_FORMAT, False)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(file_formatter)
        self.addHandler(file_handler)

        if LOG_CONSOLE:
            color_format = formatter_message(self.FORMAT, True)
            color_formatter = ColoredFormatter(color_format, self.TIME_FORMAT)
            console = logging.StreamHandler()
            console.setFormatter(color_formatter)
            self.addHandler(console)

class IdenfierAdapter(logging.LoggerAdapter):

    """Class that enhances the logging with an identifier"""

    def __init__(self, identifier):
        global slog # pylint: disable=global-statement,invalid-name
        super().__init__(slog, extra={'id': identifier})

    def process(self, msg, kwargs):
        """returns the processed log format"""
        return '[%s] %s' %(self.extra['id'], msg), kwargs

class ColoredFormatter(logging.Formatter):

    """Class that formats a particular message"""

    LEVELS_COLORS = {
        'WARNING': ColoredLogger.YELLOW,
        'INFO': ColoredLogger.MAGENTA,
        'DEBUG': ColoredLogger.BLUE,
        'CRITICAL': ColoredLogger.YELLOW,
        'ERROR': ColoredLogger.RED
    }

    def __init__(self, msg, time_format, use_color = True):
        logging.Formatter.__init__(self, msg, time_format)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in self.LEVELS_COLORS:
            levelname_color = COLOR_SEQ % (30 + self.LEVELS_COLORS[levelname]) + \
                    levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

    def formatTime(self, record, datefmt=ColoredLogger.TIME_FORMAT):
        ct = self.converter(record.created)
        t = time.strftime(datefmt, ct)
        s = "%s.%03d" % (t, record.msecs)
        return s

def init_logger(config, logs_dir=None):
    """Initializes the logger according to config"""
    global slog # pylint: disable=global-statement,invalid-name
    global LOG_CONSOLE # pylint: disable=global-statement
    global LOG_LEVEL # pylint: disable=global-statement
    global LOG_FILE # pylint: disable=global-statement
    global LOG_TIMESTAMP # pylint: disable=global-statement

    LOG_CONSOLE = config.get("console", DEFAULT_LOG_CONSOLE) if config else DEFAULT_LOG_CONSOLE
    LOG_TIMESTAMP = config.get("timestamp", DEFAULT_LOG_TIMESTAMP) if config else DEFAULT_LOG_TIMESTAMP
    log_file = config.get("file", DEFAULT_LOG_FILE) if config else DEFAULT_LOG_FILE
    LOG_LEVEL = config.get("level", DEFAULT_LOG_LEVEL) if config else DEFAULT_LOG_LEVEL

    if os.path.isabs(log_file) or not logs_dir:
        LOG_FILE = log_file
    else:
        LOG_FILE = os.path.join(logs_dir, log_file)
    logging.setLoggerClass(ColoredLogger)
    slog = logging.getLogger(__name__ + "System")
    slog.setLevel(LOG_LEVEL)

DEFAULT_LOG_FILE = "controller.log"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_CONSOLE = False
DEFAULT_LOG_TIMESTAMP = True

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
