#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Emoncms Worker Helper
ToDo:
    - control if server unavailable, and wait on 1s to 10s interval.
      depending on nb and type of errors
"""
import logging
import time
from typing import Optional, Union
from ve_utils.utype import UType as Ut
from vemonitor_m8.workers.emoncms.emoncms_app import EmoncmsApp
from vemonitor_m8.models.workers import OutputWorker
from vemonitor_m8.models.workers import WorkersHelper
from vemonitor_m8.core.exceptions import SettingInvalidException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class EmoncmsWorker(OutputWorker):
    """Emoncms Worker Helper"""
    def __init__(self, conf: dict):
        OutputWorker.__init__(self)
        self.cache_interval = 5
        self.set_min_req_interval(1)
        if self.set_conf(conf):
            self.set_worker_status()

    def is_ready(self) -> bool:
        """Test if worker is ready."""
        return isinstance(self.worker, EmoncmsApp)\
            and self.worker.is_ready()

    def notify_worker_error(self) -> bool:
        """Add message to logger if worker is not ready."""
        if self._status is False:
            logger.warning(
                "EmonCms Connection Error: "
                "Vedirect worker is not ready. "
                "Worker Name: %s",
                self.get_name()
            )

    def set_worker_status(self) -> bool:
        """Test if Worker status is ready."""
        self._status = self.worker.ping()
        self.notify_worker_error()
        return self._status

    def set_worker(self, worker: Union[dict, EmoncmsApp]) -> bool:
        """Set vedirect worker"""
        result = False
        if EmoncmsWorker.is_connector(worker):
            self.worker = EmoncmsApp(worker)
            result = True
        elif isinstance(worker, EmoncmsApp):
            self.worker = worker
            result = True
        return result

    def set_conf(self, conf: dict) -> bool:
        """Set Configuration data."""
        result = False
        connector = EmoncmsWorker.prepare_connector_data(conf)
        if self.set_worker(connector) \
                and self.set_worker_conf(
                    WorkersHelper.get_worker_conf_from_dict(conf)
                ):
            result = True
        else:
            raise SettingInvalidException(
                "[VedirectReader] Fatal error: "
                "Some configuration parameters are missing/invalid."
            )
        return result

    def send_data(self,
                  data: dict,
                  input_structure: dict
                  ) -> bool:
        """Send data to emoncms worker."""
        result = False
        if self.is_ready()\
                and Ut.is_dict(data, not_null=True)\
                and Ut.is_dict(input_structure, not_null=True):

            data_bulk, offset = EmoncmsApp.prepare_bulk_from_cache(
                data=data,
                input_structure=input_structure
            )
            if Ut.is_dict(data, not_null=True)\
                    and Ut.is_int(offset)\
                    and self.worker.api.input_bulk(
                            data=data_bulk,
                            offset=offset
                    ):
                result = True
                logger.debug(
                    "[EmoncmsWorker] Sending bulk data to emoncms at %s: \n"
                    "result: %s -- offset: %s "
                    "data_bulk(%s):\n %s",
                    time.time(),
                    result,
                    offset,
                    len(data_bulk),
                    data_bulk
                )
                # Respect minimum time interval between two requests.
                # If not sleep the needed time (see OutputWorker class)
                self.respect_req_interval()
                self.update_req_time()

        return result

    @staticmethod
    def prepare_connector_data(conf: dict) -> Optional[dict]:
        """Get formatted configuration data."""
        result = None
        if Ut.is_dict(conf, not_null=True):
            if Ut.is_dict(conf.get('connector'), not_null=True):
                result = conf.get('connector')
                result.pop("active")
            elif isinstance(conf.get('connector'), EmoncmsApp):
                result = conf.get('connector')
        return result

    @staticmethod
    def is_connector(data) -> bool:
        """Test if is configuration data."""
        return (Ut.is_dict(data)
                and Ut.is_str(data.get('addr'), not_null=True)
                and Ut.is_str(data.get('apikey'), not_null=True))\
            or isinstance(data, EmoncmsApp)
