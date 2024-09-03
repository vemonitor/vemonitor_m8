# -*- coding: utf-8 -*-
"""Redis Worker Helper"""
import logging
from typing import Optional, Union
from ve_utils.utype import UType as Ut
from vemonitor_m8.workers.redis.redis_app import RedisApp
from vemonitor_m8.models.workers import InputDictWorker
from vemonitor_m8.models.workers import OutputWorker
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.workers.redis.redis_h_time_series import HmapTimeSeriesApp

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class RedisWorkerHelper:
    """Redis reader app Helper"""

    @staticmethod
    def prepare_connector_data(conf: dict) -> Optional[dict]:
        """Get formatted configuration data."""
        result = None
        if Ut.is_dict(conf, not_null=True):
            if Ut.is_dict(conf.get('connector'), not_null=True):
                result = conf.get('connector')
                # result.pop("active")
            elif isinstance(conf.get('connector'), RedisApp):
                result = conf.get('connector')
        return result

    @staticmethod
    def is_worker_connector(data) -> bool:
        """Test if is configuration data."""
        return (RedisApp.is_redis_connector(data)) \
            or isinstance(data, RedisApp)

    @staticmethod
    def is_connector(data) -> bool:
        """Test if is configuration data."""
        return RedisApp.is_redis_connector(data)

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
                "redis_data_structure": conf['item'].get('redis_data_structure'),
                "columns": conf['item'].get('columns'),
                "ref_cols": conf['item'].get('ref_cols')
            }
        return result


class RedisCommonWorker:
    """Redis worker shared Helper"""
    def __init__(self):
        self.redis_node: Optional[str] = None
        self.redis_data_structure: Optional[str] = None

    def set_redis_node(self, value: str) -> bool:
        """Set redis_node property."""
        result = False
        if Ut.is_str(value, not_null=True):
            self.redis_node = value
            result = True
        return result

    def set_redis_data_structure(self, value: str) -> bool:
        """Set redis_data_structure property."""
        result = False
        if Ut.is_str(value, not_null=True):
            self.redis_data_structure = value
            result = True
        return result

class RedisInputWorker(RedisCommonWorker, InputDictWorker):
    """Redis reader app Helper"""
    def __init__(self, conf: dict):
        RedisCommonWorker.__init__(self)
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
        if RedisWorkerHelper.is_connector(worker):
            if Ut.is_dict(worker, not_null=True)\
                    and worker.get('active'):
                worker.pop('active')
            self.worker = RedisApp(credentials=worker)
            result = True
        elif isinstance(worker, RedisApp):
            self.worker = worker
            result = True
        else:
            raise SettingInvalidException(
                "[RedisOutputWorker] Fatal error: "
                "Some configuration parameters are missing/invalid."
            )
        return result

    def set_worker_conf(self,
                        conf: dict
                        ) -> bool:
        """
        Set Worker configuration data.

        the conf dictionary must contain :
            - name: str: required
            - redis_node: str: required
            - redis_data_structure: str: optional
            - worker_key: str: required
            - enum_key: int: required
            - time_interval: Union[int, float]: required
            - columns: dict: required
            - cache_interval: Union[int, float]: optional
            - ref_cols: list: optional

        """
        result = False
        if Ut.is_dict(conf)\
                and self.set_name(conf.get('name'))\
                and self.set_worker_key(conf.get('worker_key'))\
                and self.set_enum_key(conf.get('enum_key'))\
                and self.set_time_interval(conf.get('time_interval'))\
                and self.set_columns(conf.get('columns'))\
                and self.set_redis_node(conf.get('redis_node')):
            self.set_redis_data_structure(conf.get('redis_data_structure'))
            self.set_ref_cols(conf.get('ref_cols'))
            result = True
        return result

    def set_conf(self, conf: dict) -> bool:
        """Set Configuration data."""
        result = False
        connector = RedisWorkerHelper.prepare_connector_data(conf)
        if RedisWorkerHelper.is_worker_connector(connector)\
                and self.set_worker_conf(
                    RedisWorkerHelper.get_worker_conf_from_dict(conf)
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
        """Get input data from Redis controller."""
        if self.is_ready()\
                and self.has_columns():
            self.worker.api.get_set_members('inputs_cache')


class RedisOutputWorker(OutputWorker, RedisCommonWorker):
    """Redis Output Worker Helper"""
    def __init__(self, conf: dict):
        RedisCommonWorker.__init__(self)
        OutputWorker.__init__(self)
        self.cache_interval = 5
        self.set_min_req_interval(1)
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

    def set_worker(self, worker: dict) -> bool:
        """Set redis worker"""
        result = False
        if RedisWorkerHelper.is_connector(worker):
            if Ut.is_dict(worker, not_null=True)\
                    and worker.get('active'):
                worker.pop('active')
            self.worker = HmapTimeSeriesApp(worker)
            result = True
        elif isinstance(worker, RedisApp):
            self.worker = worker
            result = True
        else:
            raise SettingInvalidException(
                "[RedisOutputWorker] Fatal error: "
                "Some configuration parameters are missing/invalid."
            )
        return result

    def set_worker_conf(self,
                        conf: dict
                        ) -> bool:
        """
        Set Worker configuration data.

        the conf dictionary must contain :
            - name: str: optional
            - redis_node: str: required
            - redis_data_structure: str: optional
            - worker_key: str: required
            - enum_key: int: required
            - time_interval: Union[int, float]: required
            - columns: dict: required
            - cache_interval: Union[int, float]: optional
            - ref_cols: list: optional

        """
        result = False
        if Ut.is_dict(conf)\
                and self.set_worker_key(conf.get('worker_key'))\
                and self.set_enum_key(conf.get('enum_key'))\
                and self.set_time_interval(conf.get('time_interval'))\
                and self.set_columns(conf.get('columns'))\
                and self.set_redis_node(conf.get('redis_node')):
            self.set_name(conf.get('name'))
            self.set_redis_data_structure(conf.get('redis_data_structure'))
            self.set_cache_interval(conf.get('cache_interval'))
            self.set_ref_cols(conf.get('ref_cols'))
            result = True
        return result

    def set_conf(self, conf: dict) -> bool:
        """Set Configuration data."""
        result = False
        connector = RedisWorkerHelper.prepare_connector_data(conf)
        if RedisWorkerHelper.is_worker_connector(connector)\
                and self.set_worker_conf(
                    RedisWorkerHelper.get_worker_conf_from_dict(conf)
                ):
            self.set_worker(connector)
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
        result = False
        if self.is_ready():
            result = self.worker.send_data(
                redis_node=self.redis_node,
                data=data,
                input_structure=input_structure
            )
        return result
