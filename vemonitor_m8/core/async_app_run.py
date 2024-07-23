#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Async App block run Helper"""
import logging
import time
import signal
import sys
import threading
from typing import Optional
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.core.threads_controller import ThreadsController
from vemonitor_m8.events.app_block_events import AppBlockEvents
from vemonitor_m8.core.data_cache import DataCache
from vemonitor_m8.workers.redis.redis_cache import RedisCache
from vemonitor_m8.models.inputs_cache import InputsCache
from vemonitor_m8.core.data_checker import DataChecker
from vemonitor_m8.models.config import Config
from vemonitor_m8.models.workers import WorkersHelper
from vemonitor_m8.workers.workers_manager import WorkersManager
from vemonitor_m8.core.exceptions import DeviceInputValueError
from vemonitor_m8.core.exceptions import RedisConnectionException
from vemonitor_m8.core.exceptions import SettingInvalidException, WorkerException
from vemonitor_m8.core.exceptions import DeviceDataConfError

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AppBlockRun:
    """Async App block run Helper"""
    def __init__(self, conf: Config):
        self._run = False
        self.conf = None
        self.events = AppBlockEvents()
        self.inputs_data = None
        self._threads = ThreadsController()
        self.workers = WorkersManager()
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        if self.set_conf(conf)\
                and self.init_data_cache():
            self._run = True

    def sig_handler(self, signum, frame):
        """Signal handler"""
        logger.critical(
            "[AppBlockRun:sig_handler] handling signal: %s\n",
            signum
        )
        self._run = False
        self.cancel_all_timers()
        sys.exit(1)

    def is_ready(self) -> bool:
        """Test if class instance have valid battery_bank property."""
        return self.is_conf_ready()\
            and self.is_cache_ready()\
            and self._run is True

    def is_conf_ready(self) -> bool:
        """Test if class instance have valid battery_bank property."""
        return isinstance(self.conf, Config)

    def is_cache_ready(self) -> bool:
        """Test if class instance have valid battery_bank property."""
        return isinstance(self.inputs_data, InputsCache)

    def init_redis_cache(self) -> bool:
        """Init redis cache object."""
        result = False
        if AppBlockRun.is_conf(self.conf):
            redis_cache = self.conf.app_blocks[0].get('redis_cache')
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
        """Init dataCache object."""
        result = False
        if AppBlockRun.is_conf(self.conf):
            if self.init_redis_cache() is True:
                result = True
            else:
                logger.info(
                    "Start Memory Data Cache..."
                )
                self.inputs_data = DataCache(max_rows=15)
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

    def cancel_all_timers(self) -> bool:
        """Set Cancell all Thread timers."""
        self._threads.cancel_all_timers()
        time.sleep(3)

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
                self.cancel_all_timers()
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
        if len(self.inputs_data.data) >= 5:
            self.events.on_worker_data_ready()

    def read_worker_data(self,
                         worker_key: str
                         ):
        """Read input data from worker"""
        test = False

        start = time.perf_counter()
        current_thread = threading.current_thread()
        worker = self.workers.get_input_worker(worker_key)
        interval = current_thread.interval
        if WorkersHelper.is_worker(worker):
            try:
                interval = worker.time_interval
                with self._threads.lock:
                    time_key = time.time()
                    data = worker.read_data()
                    if Ut.is_dict(data, not_null=True):
                        data = self.format_input_data(data, worker.columns)
                        if Ut.is_dict(data, not_null=True):
                            data.update({'time': time_key})
                            data.update({
                                    'time_ref': Ut.get_rounded_float(
                                        time_key - int(time_key/1000) * 1000, 3
                                    )
                            })

                            self.inputs_data.add_data_cache(
                                time_key=time_key,
                                key=worker.get_name(),
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
        else:
            logger.debug(
                "[AppBlockRun::read_worker_data] "
                "Worker is down."
            )
        new_interval = interval - (time.perf_counter() - start)
        if new_interval > 0:
            current_thread.interval = new_interval

        if not test:
            logger.debug(
                "[AppBlockRun::read_worker_data] "
                "New Interval thread interval : %s.",
                new_interval
            )
        current_thread.interval = interval - (time.perf_counter() - start)

    def loop_inputs(self):
        """Run block inputs."""
        if Ut.is_dict(self.conf.app_blocks[0].get('inputs'), not_null=True):
            for key, items in self.conf.app_blocks[0].get('inputs').items():
                if Ut.is_str(key, not_null=True)\
                        and Ut.is_list(items, not_null=True):
                    for i, item in enumerate(items):
                        yield key, i, item

    def add_input_items_timer(self) -> bool:
        """Read and get data from inputs workers."""
        result = True
        min_interval = 0
        for key, i, item in self.loop_inputs():
            if Ut.is_dict(item, not_null=True):
                # if valid item
                worker = self.workers.init_input_worker(
                    connector=self.get_app_connector_by_key_item(
                        key,
                        item.get('source')
                    ),
                    worker_key=key,
                    enum_key=i,
                    item=item
                )
                if WorkersHelper.is_worker(worker):
                    min_interval = Ut.get_min_in_loop(
                        value=min_interval,
                        min_val=worker.time_interval
                    )
                    timer_key = f"{key}_{item.get('name')}_{i}"
                    worker_key = WorkersHelper.get_worker_name(key, item)
                    item.get('columns').sort()
                    if self._threads.add_timer_key(
                                key=timer_key,
                                interval=worker.time_interval,
                                callback=self.read_worker_data,
                                kwargs={
                                    'worker_key': worker_key
                                }
                            ):
                        # init nodes in cache data
                        self.inputs_data.register_node(
                            node=worker.get_name()
                        )
                    else:
                        result = False
                else:
                    result = False

                time.sleep(0.5)
            else:
                result = False
        if not self.workers.get_workers_status():
            raise WorkerException(
                "Fatal Error: Some Input workers fails. "
                "Unable to open a connexion with some input connectors. "
                f"Workers Status : {self.workers.get_input_workers_status()}"
            )

        self.inputs_data.set_interval_min(min_interval)
        self._threads.start_timers()
        return result

    def loop_outputs_items(self):
        """Run block inputs."""
        if Ut.is_dict(self.conf.app_blocks[0].get('outputs'), not_null=True):
            for key, items in self.conf.app_blocks[0].get('outputs').items():
                if Ut.is_str(key, not_null=True)\
                        and Ut.is_list(items, not_null=True):
                    for i, item in enumerate(items):
                        if Ut.is_dict(item, not_null=True):
                            yield key, i, item

    def setup_outputs_workers(self) -> bool:
        """Setup block outputs."""
        result = False
        if self.is_ready():
            result = True
            for key, i, item in self.loop_outputs_items():
                self.workers.init_output_worker(
                    connector=self.get_app_connector_by_key_item(
                        key,
                        item.get('source')
                    ),
                    worker_key=key,
                    enum_key=i,
                    item=item
                )
                result = True
        return result

    def run_output_workers(self) -> bool:
        """Run block outputs."""
        result = False
        if self.inputs_data.has_data()\
                and self.workers.has_output_workers():
            result = True
            for key, worker in self.workers.loop_on_output_workers():

                data, last_time, max_time = self.inputs_data.get_data_from_cache(
                    from_time=worker.get_last_saved_time(),
                    nb_items=worker.get_cache_interval(),
                    structure=worker.columns
                )
                interval = max_time - worker.last_saved_time
                is_time_interval = (worker.last_saved_time == 0
                               or interval >= (worker.time_interval * worker.cache_interval))
                is_interval = Ut.is_dict(data, not_null=True)\
                    and len(data) == worker.cache_interval\
                    and is_time_interval
                if is_interval:
                    is_data_send = worker.send_data(
                        data=data,
                        input_structure=worker.columns
                    )
                    if not is_data_send:
                        result = False
                    else:
                        worker.set_last_saved_time(last_time)
        return result

    def run_block(self):
        """Run Block inputs and outputs."""
        if AppBlockRun.is_conf(self.conf):
            # self.events.subscribe_worker_data_ready(self.run_output_item)
            # inputs workers blocks run on background (Threads), executed by a timer
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
                    "Unable to open a connexion with some output connectors. "
                    f"Workers Status : {self.workers.get_output_workers_status()}"
                )
            time.sleep(1)
            while self._run:
                self.run_output_workers()

                time.sleep(0.1)

    @staticmethod
    def is_conf(conf: Config) -> bool:
        """Test if valid conf"""
        return isinstance(conf, Config) and conf.is_valid() and len(conf.app_blocks) == 1
