#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Init vemonitor_m8 App"""
import logging
import sys
import argparse
from vemonitor_m8.app_run import AppRun

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.0.3"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


def parse_args(args):
    """
    Parsing function
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    parser = argparse.ArgumentParser(
        description='Monitor From VE.Direct protocol'
    )
    parser.add_argument(
        '--block',
        help='Main block name to run in your configuration file.'
    )
    parser.add_argument(
        '--app',
        help='Main app to run'
    )
    parser.add_argument(
        '--conf_path', help='Main Configuration file path'
    )
    parser.add_argument(
        '--log_path', help='Console log file path'
    )
    parser.add_argument(
        "--debug", action='store_true',
        help="Show debug output"
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='VeMonitor ' + __version__
    )

    # parse arguments from script parameters
    return parser.parse_args(args)


def main():
    """Entry point of VeMonitor program."""
    # parse argument. the script name is removed
    try:
        parser = parse_args(sys.argv[1:])
    except SystemExit:
        sys.exit(1)

    # check if we want debug
    configure_logging(debug=parser.debug)
    logger.warning("---------- VeMonitor_m8 ----------")
    logger.debug("Args: %s", parser)

    AppRun(
        block=parser.block,
        app=parser.app
    )


class AppFilter(logging.Filter):
    """
    Class used to add a custom entry into the logger
    """

    def filter(self, record):
        record.app_version = f"vemonitor-{__version__}"
        return True


class CustomFormatter(logging.Formatter):
    """Logging custom formatter."""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self,
                 fmt: str,
                 date_format: str = "%Y-%m-%d %H:%M:%S"
                 ):
        super().__init__()
        self.fmt = fmt
        self.date_format = date_format
        self.colors_format = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.WARN: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.colors_format.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.date_format)
        return formatter.format(record)


def configure_logging(debug=None):
    """
    Prepare log folder in current home directory.

    :param debug: If true, set the lof level to debug

    """
    log = logging.getLogger("vemonitor")
    log.addFilter(AppFilter())
    log.propagate = False
    syslog = logging.StreamHandler()
    syslog.setLevel(logging.DEBUG)

    formatter = CustomFormatter(
        '%(asctime)s :: %(app_version)s :: %(message)s', "%Y-%m-%d %H:%M:%S"
    )
    syslog.setFormatter(formatter)

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    # add the handlers to logger
    log.addHandler(syslog)

    log.debug("Logger ready")
