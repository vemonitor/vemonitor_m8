#!/usr/bin/python
# -*- coding: utf-8 -*-
"""AsyncMiddlewaresRun Helper"""
import logging
from vemonitor_m8.apps.async_inputs_run import AsyncInputsRun
from vemonitor_m8.middlewares.middlware_loader import MiddlewaresLoader
from vemonitor_m8.models.config import Config
from vemonitor_m8.models.middlwares import Middlewares

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AsyncMiddlewaresRun(AsyncInputsRun):
    """AsyncMiddlewaresRun Helper"""

    def __init__(self, conf: Config):
        AsyncInputsRun.__init__(self, conf=conf)
        self.middlwares = Middlewares()

    def cancel_all_timers(self):
        """Cancell all Thread timers."""
        AsyncInputsRun.cancel_all_timers(self)

    def init_events(self):
        """Init AppBlock run events"""
        AsyncInputsRun.init_events(self)

    def has_middlewares(self):
        """Init AppBlock run events"""
        return isinstance(self.middlwares, Middlewares)

    def register_cache_mid_nodes(self):
        """Init AppBlock run events"""
        result = False
        if self.has_middlewares():
            pass
        return result

    def setup_middlwares(self) -> bool:
        """Setup block outputs."""
        result = False
        if self.is_ready():
            result = True
            self.middlwares = Middlewares()
            for key in self.get_active_middlewares():

                if key == "battery_bank_mid":
                    is_added = self.middlwares.add_middleware(
                        key=key,
                        middleware=MiddlewaresLoader.get_battery_monitor_mid(
                            battery_bank=self.conf.get_battery_bank()
                        )
                    )
                    if is_added is True:
                        node = self.middlwares.get_middleware_node(
                            key=key
                        )
                        # init nodes in cache data
                        self.inputs_data.register_node(
                            node=node
                        )
                    else:
                        result = False
                else:
                    result = False
        return result

    def read_worker_data_callback(self,
                                  time_key: int,
                                  data: dict
                                  ):
        """Get connector by key item and source."""
        return self.middlwares.read_worker_data_callbacks(
            time_key=time_key,
            data=data
        )

    @staticmethod
    def get_active_middlewares() -> list:
        """Get new thread interval"""
        return [
            'battery_bank_mid',
        #    'solar_plant_mid'
        ]
