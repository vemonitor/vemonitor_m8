#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Vedirect reader app Helper"""
import logging
import os
from typing import Optional, Union
from ve_utils.utype import UType as Ut

from vemonitor_m8.workers.vedirect.vedirect_app import VedirectApp
from vemonitor_m8.models.workers import InputWorker
from vemonitor_m8.models.workers import WorkersHelper
from vemonitor_m8.core.exceptions import SettingInvalidException


__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class VedirectWorker(InputWorker):
    """Vedirect reader app Helper"""
    def __init__(self, conf: dict):
        InputWorker.__init__(self)
        self.min_source_interval = 1
        if self.set_conf(conf):
            self.set_worker_status()

    def is_ready(self) -> bool:
        """Test if worker is ready."""
        return isinstance(self.worker, VedirectApp)\
            and self.worker.is_ready()

    def notify_worker_error(self) -> bool:
        """Add message to logger if worker is not ready."""
        if self._status is False:
            logger.warning(
                "Serial Connection Error: "
                "Vedirect worker is not ready. "
                "Worker Name: %s",
                self.get_name()
            )

    def set_worker_status(self) -> bool:
        """Test if Worker status is ready."""
        self._status = self.worker.try_serial_connection(self.get_name())
        self.notify_worker_error()
        return self._status

    def set_worker(self, worker: Union[dict, VedirectApp]) -> bool:
        """Set vedirect worker"""
        result = False
        if Ut.is_dict(worker, not_null=True):
            self.worker = VedirectApp(**worker)
            result = True
        elif isinstance(worker, VedirectApp):
            self.worker = worker
            result = True
        return result

    def set_conf(self, conf: dict) -> bool:
        """Set Configuration data."""
        connector = VedirectWorker.get_connector_conf(conf)
        if VedirectWorker.is_connector(connector)\
                and self.set_worker_conf(
                    WorkersHelper.get_worker_conf_from_dict(conf)
                ):
            self.set_worker(connector)
            result = True
        else:
            raise SettingInvalidException(
                "[VedirectReader] Fatal error: "
                "Some configuration parameters are missing/invalid."
            )
        return result

    def read_data(self,
                  timeout: int = 2
                  ) -> dict:
        """
        Read data on worker
        """
        return self.worker.read_data(
            caller_key=self.get_name(),
            timeout=timeout
        )

    @staticmethod
    def get_connector_conf(conf: dict) -> Optional[dict]:
        """Get formatted connector configuration data."""
        result = None
        if Ut.is_dict(conf, not_null=True):
            if Ut.is_dict(conf.get('connector'), not_null=True):
                connector = conf.get('connector')
                result = {
                    "serial_conf": {},
                    "serial_test": connector.get('serialTest'),
                    "source_name": "VedirectWorker",
                    "auto_start": False,
                    "wait_connection": True,
                    "wait_timeout": 2
                }
                serial_conf = {}
                if Ut.is_str(connector.get('serialPort'), not_null=True):
                    serial_port = connector.get('serialPort')
                    if '/${HOME}' in serial_port:
                        serial_port = serial_port.replace('/${HOME}', os.getenv("HOME"))
                    serial_conf["serial_port"] = serial_port

                if Ut.is_int(connector.get('baud'), positive=True):
                    serial_conf["baud"] = connector.get('baud')

                if Ut.is_int(connector.get('timeout'), positive=True):
                    serial_conf["timeout"] = connector.get('timeout')
                result.update({"serial_conf": serial_conf})
            elif isinstance(conf.get('connector'), VedirectApp):
                result = conf.get('connector')
        return result

    @staticmethod
    def is_connector(data) -> bool:
        """Test if is configuration data."""
        return (Ut.is_dict(data)
                and Ut.is_dict(data.get('serial_test'), not_null=True))\
            or isinstance(data, VedirectApp)
