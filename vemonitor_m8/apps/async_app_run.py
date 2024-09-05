#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Async App block run Helper"""
import logging
import time
import sys
import signal
from vemonitor_m8.apps.app_run_main import AppBlockRun
from vemonitor_m8.apps.async_outputs_run import AsyncOutputsRun
from vemonitor_m8.core.threads_controller import ThreadsController
from vemonitor_m8.models.config import Config
from vemonitor_m8.core.exceptions import WorkerException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AsyncAppBlockRun(AsyncOutputsRun):
    """Async App block run Helper"""

    def __init__(self, conf: Config):
        AsyncOutputsRun.__init__(self, conf=conf)
        self._threads = ThreadsController()
        signal.signal(signal.SIGINT, self.signal_handler)
        self.init_events()

    def exit_handler(self):
        """Exit handler"""
        self.cancel_all_timers()
        sys.exit(1)

    def signal_handler(self, sig, frame):
        """Sig handler"""
        self.exit_handler()

    def cancel_all_timers(self):
        """Cancell all Thread timers."""
        AsyncOutputsRun.cancel_all_timers(self)

    def init_events(self):
        """Init AppBlock run events"""
        AsyncOutputsRun.init_events(self)


    def run_block(self):
        """Run Block inputs and outputs."""
        try:
            if AppBlockRun.is_conf(self.conf):

                # inputs workers blocks run on background (Threads),
                # executed by a timer
                self.add_input_items_timer()
                # inputs workers blocks run
                self.setup_outputs_workers()
                if not self.workers.get_workers_status():
                    self.cancel_all_timers()
                    logger.error(
                        "Fatal Error: Some output workers fails. "
                        "Please control all outputs conectors, "
                        "are up and ready."
                    )
                    raise WorkerException(
                        "Fatal Error: Some output workers fails. "
                        "Unable to open a connexion "
                        "with some output connectors. "
                        "Workers Status : "
                        f"{self.workers.get_output_workers_status()}"
                    )
                time.sleep(2)
                while self._run:
                    self.run_output_workers()

                    time.sleep(0.1)
        except (
                    SystemExit,
                    KeyboardInterrupt
                ) as ex:
            logger.warning(
                "Exit vemonitor... "
                "ex: %s",
                ex
            )
            self.exit_handler()
