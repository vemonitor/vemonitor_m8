#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Async App block run Helper"""
import logging
import time
import sys
import signal
import threading
from typing import Optional
from vemonitor_m8.core.app_run_main import AppBlockRun
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.core.threads_controller import RepeatTimer, ThreadsController
from vemonitor_m8.models.config import Config
from vemonitor_m8.models.workers import WorkersHelper
from vemonitor_m8.core.exceptions import VeMonitorError, WorkerException
from vemonitor_m8.core.exceptions import DeviceDataConfError

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AsyncAppBlockRun(AppBlockRun):
    """Async App block run Helper"""

    def __init__(self, conf: Config):
        AppBlockRun.__init__(self, conf=conf)
        self._threads = ThreadsController()
        signal.signal(signal.SIGINT, self.signal_handler)

    def exit_handler(self):
        """Exit handler"""
        self.cancel_all_timers()
        sys.exit(1)

    def signal_handler(self, sig, frame):
        """Sig handler"""
        self.exit_handler()

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

    def close_output_workers(self) -> bool:
        """Read and get data from inputs workers."""
        result = True
        for key, worker in self.workers.loop_on_output_workers():
            try:
                worker.close()
            except BaseException:
                pass

        return result

    def cancel_all_timers(self):
        """Cancell all Thread timers."""
        self._run = False
        self._threads.cancel_all_timers()
        time.sleep(0.2)
        self.close_input_workers()
        self.close_output_workers()

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
                new_interval = AsyncAppBlockRun.get_thread_interval(
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

                data_cache = self.inputs_data.get_data_from_cache(
                    from_time=worker.get_last_saved_time(),
                    nb_items=worker.get_cache_interval(),
                    structure=worker.columns
                )
                data, last_time, max_time = data_cache
                data = Ut.rename_keys_from_sub_sub_dict(
                    data=data,
                    ref_keys=worker.ref_cols
                )
                interval = abs(last_time - worker.last_saved_time)
                is_time_interval = (
                    worker.last_saved_time == 0
                    or interval >= (
                        worker.time_interval * worker.cache_interval
                    )
                )
                is_interval = Ut.is_dict(data, not_null=True)\
                    and len(data) == worker.cache_interval\
                    and is_time_interval
                if is_interval:
                    new_cols = Ut.rename_keys_from_dict_of_lists(
                        data=worker.columns,
                        ref_keys=worker.ref_cols
                    )
                    is_data_send = worker.send_data(
                        data=data,
                        input_structure=new_cols
                    )
                    if not is_data_send:
                        result = False
                    else:
                        worker.set_last_saved_time(last_time)
        return result

    def run_block(self):
        """Run Block inputs and outputs."""
        try:
            if AppBlockRun.is_conf(self.conf):
                # self.events.subscribe_worker_data_ready(self.run_output_item)
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
