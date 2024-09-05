#!/usr/bin/python
# -*- coding: utf-8 -*-
"""AsyncMiddlewaresRun Helper"""
import logging
from vemonitor_m8.apps.async_inputs_run import AsyncInputsRun
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.config import Config

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AsyncMiddlewaresRun(AsyncInputsRun):
    """AsyncMiddlewaresRun Helper"""

    def __init__(self, conf: Config):
        AsyncInputsRun.__init__(self, conf=conf)

    def cancel_all_timers(self):
        """Cancell all Thread timers."""
        AsyncInputsRun.cancel_all_timers(self)

    def init_events(self):
        """Init AppBlock run events"""
        AsyncInputsRun.init_events(self)
