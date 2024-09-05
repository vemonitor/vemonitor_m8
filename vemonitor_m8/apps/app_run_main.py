#!/usr/bin/python
# -*- coding: utf-8 -*-
"""App block run Helper"""
import logging
import time
from typing import Optional
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.events.app_block_events import AppBlockEvents
from vemonitor_m8.core.data_cache import DataCache
from vemonitor_m8.models.workers import WorkersHelper
from vemonitor_m8.workers.redis.redis_cache import RedisCache
from vemonitor_m8.models.inputs_cache import InputsCache
from vemonitor_m8.core.data_checker import DataChecker
from vemonitor_m8.models.config import Config
from vemonitor_m8.workers.workers_manager import WorkersManager
from vemonitor_m8.core.exceptions import DeviceInputValueError, VeMonitorError
from vemonitor_m8.core.exceptions import RedisConnectionException
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.core.exceptions import DeviceDataConfError

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AppBlockRun:
    """Async App block run Helper"""

    def __init__(self, conf: Config):
        self._run = False
        self.conf: Optional[Config] = None
        self.events = AppBlockEvents()
        self.inputs_data: Optional[InputsCache] = None
        self.workers = WorkersManager()
        if self.set_conf(conf)\
                and self.init_data_cache():
            self._run = True

    def is_ready(self) -> bool:
        """Test if class instance have valid battery_bank property."""
        return self.is_conf_ready()\
            and self.is_cache_ready()\
            and self._run is True

    def is_conf_ready(self) -> bool:
        """Test if class instance have valid battery_bank property."""
        return AppBlockRun.is_conf(self.conf)

    def is_cache_ready(self) -> bool:
        """Test if class instance have valid battery_bank property."""
        return isinstance(self.inputs_data, InputsCache)

    def init_redis_cache(self) -> bool:
        """Init redis cache object."""
        result = False
        if self.is_conf_ready():
            redis_cache = self.conf.get_redis_cache_by_key(  # type: ignore
                index=0
            )
            if Ut.is_dict(redis_cache, not_null=True):
                try:
                    self.inputs_data = RedisCache(
                        max_rows=redis_cache.get("max_data_points"),
                        connector=self.get_app_connector_by_key_item(
                            item_key="redis",
                            source=redis_cache.get("source")
                        )
                    )
                    result = True
                    logger.info(
                        "Redis Cache is enabled and active"
                    )
                except RedisConnectionException as ex:
                    result = False
                    logger.error(
                        "Error Redis Cache is enabled, "
                        "but we are unable to connect to Redis server."
                        "Please check Redis App Connectors Configuration."
                        "Exception: {%s}",
                        ex
                    )
        return result

    def init_data_cache(self) -> bool:
        """
        Init dataCache object.
        ToDo: Redis cache is only needed for worker outputs who send bulk data
        """
        result = False
        if self.is_conf_ready():
            if self.init_redis_cache() is True:
                result = True
            else:
                logger.info(
                    "Start Memory Data Cache..."
                )
                self.inputs_data = DataCache(max_rows=120)
                result = True
        return result

    def set_conf(self, conf) -> bool:
        """Set Configuration data."""
        result = False
        if AppBlockRun.is_conf(conf):
            self.conf = conf
            result = True
        else:
            raise SettingInvalidException(
                "[veMonitor] Fatal error: "
                "Config is not valid."
            )
        return result

    def format_input_data(self,
                          data: dict,
                          columns: Optional[list] = None
                          ) -> dict:
        """Format input data."""
        result = None
        data = Ut.get_items_from_dict(data, columns)
        if Ut.is_dict(data, not_null=True):
            try:
                result = DataChecker.check_input_columns(
                    data,
                    self.conf.data_structures.get('points')
                )
            except (
                DeviceDataConfError,
                DeviceInputValueError
            ) as ex:
                raise DeviceDataConfError(
                    "Fatal Error: Device Data Error. "
                    "See Your device data configuration. "
                    "Or some ipnut value is bad type"
                    f"data checked: {data}"
                ) from ex

        return result

    def get_app_connector_by_key_item(self, item_key: str, source: str):
        """Get connector by key item and source."""
        return self.conf.get_app_connector_by_key_item(
            item_key,
            source
        )

    def is_worker_data_ready(self):
        """On worker data ready event"""
        if Ut.is_dict(self.inputs_data.data, not_null=True)\
                and len(self.inputs_data.data) >= 5:
            self.events.on_worker_data_ready()

    def read_worker_data(self,
                         worker_key: str
                         ):
        """Read input data from worker"""
        test = False
        worker = self.workers.get_input_worker(worker_key)
        if WorkersHelper.is_worker(worker):
            try:
                time_key = time.time()
                data = worker.read_data()
                if Ut.is_dict(data, not_null=True):
                    data = self.format_input_data(data, worker.columns)
                    if Ut.is_dict(data, not_null=True):
                        data.update({
                            'time': time_key,
                            'time_ref': Ut.get_rounded_float(
                                time_key - int(time_key/1000) * 1000, 3
                            )
                        })
                        data = Ut.rename_keys_from_dict(
                            data=data,
                            ref_keys=worker.ref_cols
                        )
                        self.inputs_data.add_data_cache(
                            time_key=time_key,
                            node=worker.get_name(),
                            data=data
                        )
                        test = True
                    else:
                        logger.debug(
                            "[AppBlockRun::read_worker_data] "
                            "Unable to format data from serial port."
                        )
                else:
                    logger.debug(
                        "[AppBlockRun::read_worker_data] "
                        "Unable to read data from serial port."
                    )
            except Exception as ex:
                logger.error(
                    "[AppBlockRun::read_worker_data] "
                    "Worker exception, ex : %s .",
                    str(ex)
                )
                raise VeMonitorError(
                    "Fatal Error: "
                    "Ann error occured while running VeMonitor"
                ) from ex
        else:
            logger.debug(
                "[AppBlockRun::read_worker_data] "
                "Worker is down."
            )
        if not test:
            logger.debug(
                "[AppBlockRun::read_worker_data] "
                "Worker data readed with errors."
            )
        return test

    @staticmethod
    def is_conf(conf: Optional[Config]) -> bool:
        """Test if valid conf"""
        return isinstance(conf, Config)\
            and conf.is_valid()\
            and len(conf.app_blocks) == 1  # type: ignore
