#!/usr/bin/python
# -*- coding: utf-8 -*-
"""AsyncOutputsRun Helper"""
import logging
from vemonitor_m8.apps.async_mid_run import AsyncMiddlewaresRun
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.config import Config

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AsyncOutputsRun(AsyncMiddlewaresRun):
    """AsyncOutputsRun Helper"""

    def __init__(self, conf: Config):
        AsyncMiddlewaresRun.__init__(self, conf=conf)

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
        AsyncMiddlewaresRun.cancel_all_timers(self)
        self.close_output_workers()

    def init_events(self):
        """Init AppBlock run events"""
        AsyncMiddlewaresRun.init_events(self)

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
