# -*- coding: utf-8 -*-
"""Inputs data cache Helper"""
import logging
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.models.inputs_cache import InputsCache

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class DataCache(InputsCache):
    """Inputs data cache Helper"""
    def __init__(self,
                 max_rows: int = 10
                 ):
        InputsCache.__init__(self,
                             max_rows=max_rows)
        self.data = None

    def has_data(self):
        """Test if instance has data cache"""
        return Ut.is_dict(self.data, not_null=True)

    def init_data(self):
        """Init inputs data cache"""
        if not Ut.is_dict(self.data):
            self.data = {}

    def init_data_key(self, key):
        """Init inputs data cache key"""
        self.init_data()
        if not Ut.is_dict(self.data.get(key)):
            self.data[key] = {}

    def control_data_len(self):
        """Control inputs data cache length"""
        nb_items = len(self.data)
        if nb_items > self._max_rows:
            min_key = min(list(self.data.keys()))
            del self.data[min_key]

    def register_node(self, node: str):
        """Register node in cache."""

    def add_data_cache(self, time_key, key, data):
        """Set inputs data cache key"""
        time_key = Ut.get_int(time_key, 0)
        if Ut.is_int(time_key, positive=True):
            # \
            # and Ut.is_dict(data, not_null=True)
            self.init_data_key(time_key)
            self.data[time_key].update({key: data})
            self.control_data_len()

    def get_data_from_cache(self,
                            from_time: int = 0,
                            nb_items: int = 0,
                            structure: Optional[dict] = None
                            ):
        """Get data cache extract."""
        result, last_time, max_time = None, 0, 0
        if self.has_data():
            result = {}
            keys = list(self.data.keys())
            keys.sort()
            max_time = max(keys)
            for key in keys:
                if Ut.is_dict(self.data.get(key), not_null=True) \
                        and InputsCache.is_from_time(
                            item_time=key,
                            from_time=from_time
                        ):
                    if len(result) < nb_items:
                        result.update({key: self.data.get(key)})
                        last_time = key
                    else:
                        break
        return result, last_time, max_time
