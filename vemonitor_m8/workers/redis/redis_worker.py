# -*- coding: utf-8 -*-
"""Redis Worker Helper"""
import logging
from typing import Optional, Union
from ve_utils.utype import UType as Ut
from vemonitor_m8.workers.redis.redis_app import RedisApp
from vemonitor_m8.models.workers import InputDictWorker
from vemonitor_m8.models.workers import OutputWorker
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


class RedisInputWorker(InputDictWorker):
    """Redis reader app Helper"""
    def __init__(self, conf: dict):
        InputDictWorker.__init__(self)
        if self.set_conf(conf):
            self.set_worker_status()

    def is_ready(self) -> bool:
        """Test if worker is ready."""
        return isinstance(self.worker, RedisApp)\
            and self.worker.is_ready()

    def notify_worker_error(self) -> bool:
        """Add message to logger if worker is not ready."""
        if self._status is False:
            logger.warning(
                "Redis Connection Error: "
                "Redis worker is not ready. "
                "Worker Name: %s",
                self.get_name()
            )

    def set_worker_status(self) -> bool:
        """Test if Worker status is ready."""
        self._status = self.worker.ping()
        self.notify_worker_error()
        return self._status

    def set_worker(self, worker: Union[dict, RedisApp]) -> bool:
        """Set redis worker"""
        result = False
        if Ut.is_dict(worker, not_null=True):
            self.worker = RedisApp(**worker)
            result = True
        elif isinstance(worker, RedisApp):
            self.worker = worker
            result = True
        return result

    def set_conf(self, conf: dict) -> bool:
        """Set Configuration data."""
        result = False
        connector = RedisInputWorker.prepare_connector_data(conf)
        if RedisInputWorker.is_connector(connector)\
                and self.set_worker_conf(
                    WorkersHelper.get_worker_conf_from_dict(conf)
                ):
            self.set_worker(connector)
            result = True
        else:
            raise SettingInvalidException(
                "[RedisInputWorker] Fatal error: "
                "Some configuration parameters are missing/invalid."
            )
        return result

    def read_data(self,
                  timeout: int = 2
                  ) -> dict:
        """Get input data from VeDirect controller."""
        if self.is_ready()\
                and self.has_columns():
            pass

    @staticmethod
    def get_worker_conf_from_dict(conf: dict) -> Optional[dict]:
        """Test if is configuration data."""
        result = None
        if Ut.is_dict(conf, not_null=True) \
                and Ut.is_dict(conf.get('item'), not_null=True):
            result = {
                "name": conf['item'].get('name'),
                "worker_key": conf.get('worker_key'),
                "enum_key": conf.get('enum_key'),
                "time_interval": conf['item'].get('time_interval'),
                "cache_interval": conf['item'].get('cache_interval'),
                "redis_node": conf['item'].get('redis_node'),
                "columns": conf['item'].get('columns'),
                "ref_cols": conf['item'].get('ref_cols')
            }
        return result

    @staticmethod
    def prepare_connector_data(conf: dict) -> Optional[dict]:
        """Get formatted configuration data."""
        result = None
        if Ut.is_dict(conf, not_null=True):
            if Ut.is_dict(conf.get('connector'), not_null=True):
                result = conf.get('connector')
                result.pop("active")
            elif isinstance(conf.get('connector'), RedisApp):
                result = conf.get('connector')
        return result

    @staticmethod
    def is_connector(data) -> bool:
        """Test if is configuration data."""
        return (Ut.is_dict(data)
                and Ut.is_str(data.get('host'), not_null=True)
                and Ut.is_str(data.get('port'), not_null=True)) \
            or isinstance(data, RedisApp)


class RedisOutputWorker(OutputWorker):
    """Redis Output Worker Helper"""
    def __init__(self, conf: dict):
        OutputWorker.__init__(self)
        self.cache_interval = 5
        self.set_min_req_interval(1)
        self.set_conf(conf)

    def is_ready(self) -> bool:
        """Test if worker is ready."""
        return isinstance(self.worker, RedisApp)\
            and self.worker.is_ready()

    def set_worker(self, worker: dict) -> bool:
        """Set redis worker"""
        result = False
        if RedisOutputWorker.is_connector(worker):
            self.worker = RedisApp(worker)
            result = True
        elif isinstance(worker, RedisApp):
            self.worker = worker
            result = True
        return result

    def set_conf(self, conf: dict) -> bool:
        """Set Configuration data."""
        connector = RedisOutputWorker.prepare_connector_data(conf)
        if self.set_worker(connector) \
                and self.set_worker_conf(
                    WorkersHelper.get_worker_conf_from_dict(conf)
                ):
            result = True
        else:
            raise SettingInvalidException(
                "[RedisOutputWorker] Fatal error: "
                "Some configuration parameters are missing/invalid."
            )
        return result

    def send_data(self,
                  data: dict,
                  input_structure: dict
                  ) -> bool:
        """Send data to redis worker."""

    @staticmethod
    def prepare_connector_data(conf: dict) -> Optional[dict]:
        """Get formatted configuration data."""
        result = None
        if Ut.is_dict(conf, not_null=True):
            if Ut.is_dict(conf.get('connector'), not_null=True):
                result = conf.get('connector')
                result.pop("active")
            elif isinstance(conf.get('connector'), RedisApp):
                result = conf.get('connector')
        return result

    @staticmethod
    def is_connector(data) -> bool:
        """Test if is configuration data."""
        return (Ut.is_dict(data)
                and Ut.is_str(data.get('host'), not_null=True)
                and Ut.is_str(data.get('port'), not_null=True)) \
            or isinstance(data, RedisApp)
