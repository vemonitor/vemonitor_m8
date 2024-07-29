#!/usr/bin/python
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
        self._nodes = []

    def has_data(self):
        """Test if instance has data cache"""
        return Ut.is_dict(self.data, not_null=True)

    def has_key_data(self, time_key: int) -> bool:
        """Test if instance has data cache"""
        return self.has_data()\
            and Ut.is_dict(self.data.get(time_key), not_null=True)

    def has_node_data(self, time_key: int, node: str) -> bool:
        """Test if instance has data cache"""
        return self.has_key_data(time_key)\
            and Ut.is_dict(self.data[time_key].get(node), not_null=True)

    def get_node_data(self, time_key: int, node: str) -> bool:
        """Test if instance has data cache"""
        result = None
        if self.has_node_data(time_key, node):
            result = self.data[time_key].get(node)
        return result

    def get_cache_nodes_keys_list(self,
                                  nodes: Optional[list] = None
                                  ) -> list:
        """
        Get list of inputs nodes keys from redis set cache data.
        """
        result = self._nodes
        if Ut.is_list(nodes, not_null=True):
            result = [
                x
                for x in result
                if x in nodes
            ]
        return result

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
        result = False
        if Ut.is_str(node, not_null=True)\
                and node not in self._nodes:
            self._nodes.append(node)
            result = True
        return result

    def reset_data_cache(self) -> bool:
        """Reset data cache for all nodes."""
        self._nodes = []
        self.data = None
        return True
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
