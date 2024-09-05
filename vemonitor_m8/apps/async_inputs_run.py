#!/usr/bin/python
# -*- coding: utf-8 -*-
"""AsyncInputsRun Helper"""
import logging
import time
import threading
from typing import Optional
from vemonitor_m8.apps.app_run_main import AppBlockRun
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.core.threads_controller import ThreadsController
from vemonitor_m8.models.config import Config
from vemonitor_m8.models.workers import WorkersHelper
from vemonitor_m8.core.exceptions import VeMonitorError, WorkerException
from vemonitor_m8.core.exceptions import DeviceDataConfError

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AsyncInputsRun(AppBlockRun):
    """AsyncInputsRun Helper"""

    def __init__(self, conf: Config):
        AppBlockRun.__init__(self, conf=conf)
        self._threads = ThreadsController()
        self.init_events()

    G_INPUT_TIMER = "input_timers"
    E_INPUT_TIMER_START = "on_start"
    E_INPUT_TIMER_STOP = "on_start"
    E_INPUT_DATA_READ = "on_data_read"

    def init_events(self):
        """Init AppBlock run events"""
        self.events.add_events(
            group=self.G_INPUT_TIMER,
            events=[
                self.E_INPUT_TIMER_START,
                self.E_INPUT_TIMER_STOP,
                self.E_INPUT_DATA_READ]
        )

    def close_input_workers(self) -> bool:
        """Read and get data from inputs workers."""
        result = False
        for key, worker in self.workers.loop_on_input_workers():
            try:
                worker.close()
                result = True
            except BaseException:
                pass

        return result

    def cancel_all_timers(self):
        """Cancell all Thread timers."""
        self._run = False
        self._threads.cancel_all_timers()
        time.sleep(0.2)
        self.close_input_workers()

    def format_input_data(self,
                          data: dict,
                          columns: Optional[list] = None
                          ) -> dict:
        """Format input data."""
        result = None
        try:
            result = AppBlockRun.format_input_data(
                self,
                data=data,
                columns=columns
            )
        except DeviceDataConfError as ex:
            self.cancel_all_timers()
            raise DeviceDataConfError(
                "Fatal Error: Device Data Error. "
                "See Your device data configuration. "
                "Or some ipnut value is bad type"
                f"data checked: {data}"
            ) from ex
        return result

    def read_worker_data(self,
                         worker_key: str
                         ):
        """Read input data from worker"""
        test = False
        try:
            start = time.perf_counter()
            current_thread = threading.current_thread()
            worker = self.workers.get_input_worker(worker_key)
            if WorkersHelper.is_worker(worker):
                interval = worker.time_interval
                with self._threads.lock:
                    diff = current_thread.set_exec_time()
                    test = AppBlockRun.read_worker_data(
                        self,
                        worker_key=worker_key
                    )
                    if current_thread.has_events():
                        current_thread.events.trigger_event(
                            key=AsyncInputsRun.E_INPUT_DATA_READ
                        )
                new_interval = AsyncInputsRun.get_thread_interval(
                    diff=diff,
                    interval=interval,
                    start=start
                )
                logger.debug(
                    "[AsyncAppBlockRun::read_worker_data] "
                    "New interval for input worker %s "
                    "set to : %s s.",
                    worker.get_name(),
                    new_interval
                )
                if new_interval <= interval:
                    current_thread.interval = new_interval

                
        except VeMonitorError as ex:
            logger.error(
                "[AsyncAppBlockRun::read_worker_data] "
                "Worker exception, ex : %s .",
                str(ex)
            )
            self.cancel_all_timers()
            raise VeMonitorError(
                "Fatal Error: "
                "Ann error occured while running VeMonitor"
            ) from ex

        return test

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
                        events=self.events.get_group_events(
                            group=self.G_INPUT_TIMER
                        ),
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

    @staticmethod
    def get_thread_interval(diff: float,
                            interval: int,
                            start: float) -> int:
        """Get new thread interval"""
        result = interval
        now = time.perf_counter()
        if Ut.is_int(interval, positive=True)\
                and Ut.is_float(start, positive=True)\
                and Ut.is_float(diff, positive=True):
            exact_time = round(abs(diff - 1), 6)
            if 0 < exact_time <= 1:
                now_int = Ut.get_int(now, 0)
                next_exec = round(abs(now_int + interval + exact_time), 6)
                result = round(abs(now - next_exec), 6)
        return result

