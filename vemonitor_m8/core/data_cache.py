#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Inputs data cache Helper"""
import logging
from typing import Optional
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.inputs_cache import InputsCache

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
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

    def has_data(self) -> bool:
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

    def get_cache_keys_by_node(self,
                               node: str
                               ) -> list:
        """Get formatted hmap keys."""
        result = None
        if self.has_data():
            result = [
                time_key
                for time_key in self.data
                if self.has_node_data(time_key, node)
            ]
        return result

    def control_node_data_len(self, node: str):
        """Control inputs data cache length"""
        time_keys = self.get_cache_keys_by_node(node)
        if Ut.is_list(time_keys, not_null=True):
            nb_items = len(time_keys)
            if nb_items > self._max_rows:
                nb_del = nb_items - self._max_rows
                # register invalid keys to delete
                to_del = time_keys[0: nb_del]
                for time_key in to_del:
                    nb_nodes = len(self.data.get(time_key))
                    if nb_nodes > 1:
                        self.data[time_key].pop(node, None)
                    else:
                        self.data.pop(time_key, None)

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

    def _update_or_set_data_node_key(self,
                                     formatted_node: str,
                                     time_key: int,
                                     data: dict
                                     ) -> tuple:
        """Update or set data key."""
        result = None
        if self.has_data()\
                and Ut.is_int(time_key, positive=True)\
                and Ut.is_str(formatted_node, not_null=True)\
                and Ut.is_dict(data, not_null=True):
            result = self.get_node_data(time_key, formatted_node)
            if Ut.is_dict(result, not_null=True):
                result.update(data)
            else:
                result = data
        return result

    def add_data_cache(self, time_key, node, data):
        """Set inputs data cache key"""
        result = False
        time_key = Ut.get_int(time_key, 0)
        if Ut.is_int(time_key, positive=True)\
                and Ut.is_str(node, not_null=True)\
                and Ut.is_dict(data, not_null=True):
            self.init_data_key(time_key)
            data = self._update_or_set_data_node_key(
                formatted_node=node,
                time_key=time_key,
                data=data
            )
            if Ut.is_dict(data, not_null=True):
                self.data[time_key].update({node: data})
                result = True
            self.control_node_data_len(node=node)
        return result

    def get_cache_data_by_structure(self,
                                    time_key: int,
                                    structure: Optional[dict] = None
                                    ):
        """Get data cache key by structure"""
        result = None
        if Ut.is_int(time_key, positive=True)\
                and Ut.is_dict(structure, not_null=True):
            nodes = list(structure.keys())
            result = {}
            for node in nodes:
                if Ut.is_list(structure.get(node)):
                    data_node = self.get_node_data(
                        time_key=time_key,
                        node=node
                    )
                    if Ut.is_dict(data_node, not_null=True):
                        result[node] = Ut.get_items_from_dict(
                            data=data_node,
                            list_keys=structure.get(node)
                        )

        return result

    def get_cache_keys(self,
                       from_time: int = 0,
                       structure: Optional[dict] = None
                       ):
        """Get data cache key"""
        result = None
        if self.has_data():
            time_keys = list(self.data.keys())
            time_keys.sort()

            if from_time > 0:
                result = [
                    time_key
                    for time_key in time_keys
                    if Ut.is_from_time(
                        item_time=time_key,
                        from_time=from_time
                    )
                ]
            else:
                result = time_keys
        return result

    def get_data_from_cache(self,
                            from_time: int = 0,
                            nb_items: int = 0,
                            structure: Optional[dict] = None
                            ):
        """Get data cache extract."""
        result, last_time, max_time = None, 0, 0
        if self.has_data():
            result = {}
            time_keys = self.get_cache_keys(from_time=from_time)
            if Ut.is_list(time_keys, not_null=True):
                for time_key in time_keys:
                    if nb_items > 0\
                            and len(result) >= nb_items:
                        break
                    if Ut.is_dict(structure, not_null=True):
                        data = self.get_cache_data_by_structure(
                            time_key=time_key,
                            structure=structure
                        )
                        if Ut.is_dict(data, not_null=True):
                            result.update({
                                time_key: data
                            })
                    else:
                        result.update({time_key: self.data.get(time_key)})

            if Ut.is_dict(result, not_null=True):
                max_time = max(result)
                last_time = max_time + 1
        return result, last_time, max_time
