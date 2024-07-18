#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Init vemonitor_m8 App"""
import logging
import sys
import argparse
from ve_utils.utype import UType as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")

def parse_args(args):
    """
    Parsing function
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    parser = argparse.ArgumentParser(description='Monitor From VE.Direct protocol')
    parser.add_argument("--debug", action='store_true',
                        help="Show debug output")
    parser.add_argument('-v', '--version', action='version',
                        version='VeMonitor ' + __version__)

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

    logger.debug("VeMonitor args: %s", parser)

    try:
        main_app = 2
    except SystemExit:
        sys.exit(1)


class AppFilter(logging.Filter):
    """
    Class used to add a custom entry into the logger
    """

    def filter(self, record):
        record.app_version = f"vemonitor-{__version__}"
        return True

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

    formatter = logging.Formatter(
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
