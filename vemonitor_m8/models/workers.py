#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Workers models helper.
This module contain worker models and helpers.
    - Worker(ABC) Worker base class
    - InputWorker(Worker) Input Worker base class
    - OutputWorker(Worker) Output Worker base class
    - WorkersDict Workers items container class
    - Workers controller class
    - WorkersHelper helper class
"""
import time
from abc import ABC, abstractmethod
from typing import Optional, Union
from ve_utils.utype import UType as Ut

from vemonitor_m8.models.item_dict import DictOfObject

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"


class Worker(ABC):
    """Worker model helper"""

    def __init__(self):
        self._info = {
            'name': "",
            'worker_key': "",
            'enum_key': -1
        }
        self.time_interval = None
        self.columns = None
        self.ref_cols = None
        self.worker = None
        self._status = False

    def get_worker_status(self) -> bool:
        """Test if instance has name property."""
        return self._status is True

    def has_info(self) -> bool:
        """Test if instance has _info properties."""
        return self.has_name()\
            and self.has_worker_key()\
            and self.has_enum_key()

    def has_name(self) -> bool:
        """Test if instance has name property."""
        return Ut.is_str(self._info.get('name'), not_null=True)

    def get_name(self) -> str:
        """Get name property."""
        return self._info.get('name')

    def set_name(self, value: str) -> bool:
        """Set name property."""
        result = False
        if Ut.is_str(value, not_null=True):
            self._info['name'] = value
            result = True
        return result

    def has_worker_key(self) -> bool:
        """Test if instance has worker_key property."""
        return Ut.is_str(self._info.get('worker_key'), not_null=True)

    def get_worker_key(self) -> str:
        """Get worker_key property."""
        return self._info.get('worker_key')

    def set_worker_key(self, value: str) -> bool:
        """Set worker_key property."""
        result = False
        if Ut.is_str(value, not_null=True):
            self._info['worker_key'] = value
            result = True
        return result

    def has_enum_key(self) -> bool:
        """Test if instance has enum_key property."""
        return Ut.is_int(self._info.get('enum_key'), mini=0)

    def get_enum_key(self) -> int:
        """Get enum_key property."""
        return self._info.get('enum_key')

    def set_enum_key(self, value: int) -> bool:
        """Set enum_key property."""
        result = False
        if Ut.is_int(value, mini=0):
            self._info['enum_key'] = value
            result = True
        return result

    def has_time_interval(self) -> bool:
        """Test if instance has time_interval property."""
        return Ut.is_numeric(self.time_interval, mini=0)

    def set_time_interval(self, value: Union[int, float]) -> bool:
        """Set time_interval property."""
        result = False
        if Ut.is_numeric(value, positive=True):
            self.time_interval = value
            result = True
        return result

    def has_ref_cols(self) -> bool:
        """Test if instance has ref_cols property."""
        return Ut.is_list(self.ref_cols, not_null=True)

    def set_ref_cols(self, value: list) -> bool:
        """Set ref_cols property."""
        result = False
        if Ut.is_list(value, not_null=True):
            self.ref_cols = value
            result = True
        return result

    def has_worker_conf(self) -> bool:
        """Test if instance has worker_conf properties."""
        return self.has_info() and self.has_time_interval()

    def set_worker_conf(self,
                        conf: dict
                        ) -> bool:
        """
        Set Worker configuration data.

        the conf dictionary must contain :
            - name: str: required
            - worker_key: str: required
            - enum_key: int: required
            - time_interval: Union[int, float]: required
            - columns: any: optional (see set_columns extended method)
            - ref_cols: list: optional

        """
        result = False
        if Ut.is_dict(conf)\
                and self.set_name(conf.get('name'))\
                and self.set_worker_key(conf.get('worker_key'))\
                and self.set_enum_key(conf.get('enum_key'))\
                and self.set_time_interval(conf.get('time_interval')):
            self.set_columns(conf.get('columns'))
            self.set_ref_cols(conf.get('ref_cols'))
            result = True
        return result

    @abstractmethod
    def is_ready(self) -> bool:
        """Test if Worker is ready."""

    @abstractmethod
    def set_worker_status(self) -> bool:
        """Test if Worker status is ready."""

    @abstractmethod
    def set_worker(self, worker: dict) -> bool:
        """Set Worker class instance."""

    @abstractmethod
    def has_columns(self) -> bool:
        """Test if instance has columns property."""

    @abstractmethod
    def set_columns(self, value) -> bool:
        """Set columns property."""


class InputWorker(Worker):
    """
    Input Worker model helper.
    Used by simple inputs workers
    """

    def __init__(self):
        Worker.__init__(self)

    def has_columns(self) -> bool:
        """Test if instance has columns property."""
        return Ut.is_list(self.columns, not_null=True)

    def set_columns(self, value: list) -> bool:
        """Set time_interval property."""
        result = False
        if Ut.is_list(value, not_null=True):
            self.columns = value
            result = True
        return result

    @abstractmethod
    def read_data(self,
                  timeout: int = 2
                  ) -> dict:
        """Get input data from Worker class instance."""


class InputDictWorker(InputWorker):
    """
    Input Worker model helper.
    Used by simple inputs workers
    """

    def __init__(self):
        InputWorker.__init__(self)

    def has_columns(self) -> bool:
        """Test if instance has columns property."""
        return Ut.is_dict(self.columns, not_null=True)

    def set_columns(self, value: dict) -> bool:
        """Set time_interval property."""
        result = False
        if Ut.is_dict(value, not_null=True):
            self.columns = value
            result = True
        return result


class OutputWorker(Worker):
    """Output Worker model helper"""

    def __init__(self):
        Worker.__init__(self)
        self.last_saved_time = 0
        self.cache_interval = 0
        self.min_req_interval = 0
        self.last_req = 0

    def has_columns(self) -> bool:
        """Test if instance has columns property."""
        return Ut.is_dict(self.columns, not_null=True)

    def set_columns(self, value: dict) -> bool:
        """Set time_interval property."""
        result = False
        if Ut.is_dict(value, not_null=True):
            self.columns = value
            result = True
        return result

    def has_last_saved_time(self) -> bool:
        """Test if instance has last_saved_time property."""
        return Ut.is_int(self.last_saved_time, positive=True)

    def get_last_saved_time(self) -> int:
        """Get last_saved_time property."""
        return Ut.get_int(self.last_saved_time, 0)

    def set_last_saved_time(self, value: Union[int, float]) -> bool:
        """Set last_saved_time property."""
        value = Ut.get_int(value, -1)
        result = False
        if Ut.is_int(value, mini=0):
            self.last_saved_time = value
            result = True
        return result

    def has_cache_interval(self) -> bool:
        """Test if instance has cache_interval property."""
        return Ut.is_int(self.cache_interval, positive=True)

    def get_cache_interval(self) -> int:
        """Test if instance has cache_interval property."""
        return Ut.get_int(self.cache_interval, 0)

    def set_cache_interval(self, value: int) -> bool:
        """Test if instance has cache_interval property."""
        result = False
        if Ut.is_int(value, mini=0):
            self.cache_interval = value
            result = True
        return result

    def has_min_req_interval(self) -> bool:
        """Test if instance has min_req_interval property."""
        return Ut.is_numeric(self.min_req_interval, positive=True)

    def get_min_req_interval(self) -> float:
        """Test if instance has min_req_interval property."""
        return Ut.get_float(self.min_req_interval, 0)

    def set_min_req_interval(self, value: Union[int, float]) -> bool:
        """Test if instance has min_req_interval property."""
        result = False
        if Ut.is_numeric(value, positive=True):
            self.min_req_interval = value
            result = True
        return result

    def update_req_time(self):
        """Update request time."""
        self.last_req = time.time()

    def respect_req_interval(self):
        """Update request time."""
        if self.has_min_req_interval()\
                and Ut.is_numeric(self.last_req, positive=True):
            interval = time.time() - self.last_req
            if interval < self.min_req_interval:
                time.sleep(self.min_req_interval - interval)

    def set_worker_conf(self,
                        conf: dict
                        ) -> bool:
        """
        Set Worker configuration data.

        the conf dictionary must contain :
            - name: str: required
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
                and self.set_columns(conf.get('columns')):
            self.set_name(conf.get('name'))
            self.set_cache_interval(conf.get('cache_interval'))
            self.set_ref_cols(conf.get('ref_cols'))
            result = True
        return result

    @abstractmethod
    def send_data(self,
                  data: dict,
                  input_structure: dict
                  ) -> bool:
        """Send data to worker."""


class WorkersDict(DictOfObject):
    """Workers model helper"""
    def __init__(self):
        DictOfObject.__init__(self)

    def has_workers(self) -> bool:
        """Test if workers items defined."""
        return self.has_items()

    def has_worker_key(self, key: str) -> bool:
        """Test if instance has worker key defined."""
        return self.has_item_key(key=key)

    def init_worker(self, reset: bool = False):
        """Initialise worker items."""
        self.init_item(reset=reset)

    def add_worker(self,
                   key: str,
                   worker: Worker
                   ) -> bool:
        """Add worker item."""
        return self.add_item(
            key=key,
            value=worker
        )

    def get_worker(self, key: str) -> Optional[Worker]:
        """Get worker key."""
        return self.get_item(key=key)

    def loop_on_workers(self):
        """Get worker key."""
        if self.has_workers():
            for key, worker in self.items.items():
                if WorkersHelper.is_worker(worker):
                    yield key, worker

    def get_workers(self) -> Optional[dict]:
        """Get worker key."""
        return self.get_items()

    @staticmethod
    def is_valid_item_key(key: tuple):
        """Test if is valid item type"""
        return Ut.is_str(key)

    @staticmethod
    def is_valid_item_value(value: tuple):
        """Test if is valid item type"""
        return WorkersHelper.is_worker(value)


class Workers:
    """Workers model helper"""
    def __init__(self):
        self.inputs = WorkersDict()
        self.outputs = WorkersDict()

    def has_input_workers(self) -> bool:
        """Test if instance has worker items defined."""
        return WorkersHelper.is_workers_items(self.inputs)\
            and self.inputs.has_workers()

    def has_input_worker_key(self, key: str) -> bool:
        """Test if instance has input worker key defined."""
        return WorkersHelper.is_workers_items(self.inputs)\
            and self.inputs.has_worker_key(key)

    def add_input_worker(self,
                         key: str,
                         worker: InputWorker
                         ) -> bool:
        """Add input worker item."""
        result = False
        if WorkersHelper.is_workers_items(self.inputs)\
                and WorkersHelper.is_input_worker(worker)\
                and self.inputs.add_worker(key=key, worker=worker):
            result = True
        return result

    def get_input_worker(self, key: str) -> Optional[InputWorker]:
        """Get input worker by key."""
        result = None
        if WorkersHelper.is_workers_items(self.inputs):
            result = self.inputs.get_worker(key)
        return result

    def get_input_workers(self) -> Optional[dict]:
        """Get input workers."""
        result = None
        if self.has_output_workers():
            result = self.outputs.get_workers()
        return result

    def loop_on_input_workers(self):
        """Get input workers."""
        if self.has_input_workers():
            for key, worker in self.inputs.loop_on_workers():
                if WorkersHelper.is_input_worker(worker):
                    yield key, worker

    def has_output_workers(self) -> bool:
        """Test if instance has output worker items defined."""
        return WorkersHelper.is_workers_items(self.outputs)\
            and self.outputs.has_workers()

    def has_output_worker_key(self, key: str) -> bool:
        """Test if instance has output worker key defined."""
        return WorkersHelper.is_workers_items(self.outputs)\
            and self.outputs.has_worker_key(key)

    def add_output_worker(self,
                          key: str,
                          worker: OutputWorker
                          ) -> bool:
        """Add output worker item."""
        result = False
        if WorkersHelper.is_workers_items(self.outputs)\
                and WorkersHelper.is_output_worker(worker)\
                and self.outputs.add_worker(key=key, worker=worker):
            result = True
        return result

    def get_output_worker(self, key: str) -> Optional[OutputWorker]:
        """Get output worker by key."""
        result = None
        if WorkersHelper.is_workers_items(self.outputs):
            result = self.outputs.get_worker(key)
        return result

    def get_output_workers(self) -> Optional[dict]:
        """Get output workers."""
        result = None
        if self.has_output_workers():
            result = self.outputs.get_workers()
        return result

    def loop_on_output_workers(self):
        """Get output workers."""
        if self.has_output_workers():
            for key, worker in self.outputs.loop_on_workers():
                if WorkersHelper.is_output_worker(worker):
                    yield key, worker


class WorkersHelper:
    """WorkersHelper model helper"""

    @staticmethod
    def is_worker(worker: Worker) -> bool:
        """Test if is a worker instance."""
        return isinstance(worker, Worker)

    @staticmethod
    def format_worker_conf(connector: Union[dict, object],
                           worker_key: str,
                           enum_key: int,
                           item: dict,
                           ) -> Optional[dict]:
        """Get formatted worker configuration data."""
        result = None
        if Ut.is_str(worker_key) \
                and Ut.is_int(enum_key) \
                and connector is not None \
                and Ut.is_dict(item, not_null=True):
            result = {
                'connector': connector,
                'worker_key': worker_key,
                'enum_key': enum_key,
                'item': item
            }
        return result

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
                "columns": conf['item'].get('columns'),
                "ref_cols": conf['item'].get('ref_cols')
            }
        return result

    @staticmethod
    def is_worker_ready(worker: Worker) -> bool:
        """Test if the controller is ready"""
        return WorkersHelper.is_worker(worker) and worker.is_ready()

    @staticmethod
    def is_input_worker(worker: InputWorker) -> bool:
        """Test if is a worker instance."""
        return isinstance(worker, InputWorker)

    @staticmethod
    def is_output_worker(worker: OutputWorker) -> bool:
        """Test if is a worker instance."""
        return isinstance(worker, OutputWorker)

    @staticmethod
    def is_workers_items(items) -> bool:
        """Test if workers items defined."""
        return isinstance(items, WorkersDict)

    @staticmethod
    def get_worker_name(key: str, item: dict) -> str:
        """Get worker formatted key."""
        return f"{key}_{item.get('source')}_{item.get('name')}"
