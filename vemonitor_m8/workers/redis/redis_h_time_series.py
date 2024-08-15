#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Redis vemonitor Helper"""
import logging
from operator import itemgetter
from typing import Optional, Union
from ve_utils.ujson import UJson
from vemonitor_m8.core.exceptions import RedisAppException
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.workers.redis.redis_app import RedisApp

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class HmapTimeSeriesApp(RedisApp):
    """Redis Hmap Time Series Helper"""
    def __init__(self,
                 credentials: dict,
                 max_rows: int = 3600
                 ):
        RedisApp.__init__(self, credentials=credentials)
        self._nodes = []
        self._max_rows = 3600
        self.node_base = 'n'
        self.set_max_rows(max_rows)

    def set_max_rows(self, value: int) -> bool:
        """Set interval_min property."""
        result = False
        if Ut.is_int(value, positive=True):
            self._max_rows = value
            result = True
        return result

    def get_nodes_keys_list(self,
                            node_name: str,
                            nodes: Optional[list] = None
                            ) -> list:
        """
        Get list of inputs nodes keys from redis set cache data.
        ToDo:
            - if self.api.get_set_members(node_name) return None
              list() may throw an exception.
              May caused by redis error (can be unreachable server).
        """
        result = list(
            self.api.get_set_members(node_name)
        )
        if Ut.is_list(nodes, not_null=True):
            formated_nodes = [
                HmapTimeSeriesApp.get_map_key(
                    x,
                    node_base=self.node_base
                )
                for x in nodes
                if HmapTimeSeriesApp.get_map_key(
                    x,
                    node_base=self.node_base
                ) is not None
            ]
            result = [
                x
                for x in result
                if x in formated_nodes
            ]
        return result

    def get_keys_by_node(self,
                         formatted_node: str,
                         from_time: int = 0
                         ) -> list:
        """Get formatted hmap keys."""
        result = None
        keys = self.api.get_hmap_keys(formatted_node)
        if Ut.is_list(keys, not_null=True):
            keys.sort()
            if Ut.is_int(from_time, positive=True):
                result = [
                    Ut.get_int(x, 0)
                    for x in keys
                    if Ut.is_from_time(
                            item_time=Ut.get_int(x),
                            from_time=from_time
                        )
                ]
            else:
                result = [Ut.get_int(x, 0) for x in keys]
        return result

    def get_keys_structure(self,
                           node_keys: list,
                           nb_items: int,
                           from_time: int = 0
                           ) -> Optional[Union[list, dict]]:
        """Get time interval from hmap keys."""
        structure = None
        if Ut.is_list(node_keys, not_null=True):
            structure = []
            for node in node_keys:
                keys = self.get_keys_by_node(
                    formatted_node=node,
                    from_time=from_time
                )
                if Ut.is_list(keys, not_null=True):
                    interval = HmapTimeSeriesApp.get_interval_keys(keys)
                    for cache_key in keys:
                        structure.append((node, interval, cache_key))
            if Ut.is_list(structure, not_null=True):
                structure = sorted(structure, key=itemgetter(2))
                structure = HmapTimeSeriesApp.get_keys_section(
                    structure=structure,
                    nb_items=nb_items
                )
        return structure

    def enum_node_keys(self,
                       node_name: str,
                       nodes: Optional[list] = None,
                       nb_items: int = 0,
                       from_time: int = 0
                       ):
        """Get list of inputs nodes keys from redis cache data."""
        if self.is_ready():
            node_keys = self.get_nodes_keys_list(
                node_name=node_name,
                nodes=nodes
                )
            if Ut.is_list(node_keys, not_null=True):
                if nb_items > 0:
                    structure = self.get_keys_structure(
                        node_keys=node_keys,
                        nb_items=nb_items,
                        from_time=from_time,
                    )
                    if Ut.is_dict(structure, not_null=True):
                        for node, cache_keys in structure.items():
                            yield node, cache_keys
                    elif Ut.is_list(structure, not_null=True):
                        for node, cache_keys in structure:
                            yield node, cache_keys
                else:
                    for node in node_keys:
                        yield node, self.get_keys_by_node(
                            formatted_node=node,
                            from_time=from_time
                        )

    def reset_node_data(self, node_name: str) -> list:
        """Reset data cache for all nodes."""
        result = None
        if self.api.set_pipeline():
            try:
                # Remove data cache
                for node, keys in self.enum_node_keys(
                        node_name=node_name):
                    if Ut.is_list(keys, not_null=True):
                        self.api.del_hmap_keys(
                            name=node,
                            keys=keys,
                            client=self.api.pipe
                        )
                # Remove Nodes list set
                node_keys = self.get_nodes_keys_list(
                    node_name=node_name
                )
                if Ut.is_list(node_keys, not_null=True):
                    self.api.remove_set_members(
                        name=node_name,
                        values=node_keys,
                        client=self.api.pipe
                    )
                # execute pipe
                result = self.api.pipe.execute()
            except BaseException as ex:
                logger.error(
                    "[HmapTimeSeriesApp::reset_node_data] "
                    "Unable to reset all node data. "
                    "ex : %s",
                    ex
                )
                raise RedisAppException(
                    "[HmapTimeSeriesApp:reset_node_data] "
                    "Fatal Error : Unable to set pipeline."
                ) from ex
        return result

    def update_or_set_data_node_key(self,
                                    formatted_node: str,
                                    time_key: int,
                                    data: dict
                                    ) -> tuple:
        """Update or set data key."""
        result, is_updated = None, False
        if self.is_ready()\
                and Ut.is_int(time_key, positive=True)\
                and Ut.is_str(formatted_node, not_null=True)\
                and Ut.is_dict(data, not_null=True):
            data_in = self.api.get_hmap_data(
                formatted_node,
                str(time_key)
            )
            if Ut.is_str(data_in, not_null=True):
                result = UJson.loads_json(data_in)
                if Ut.is_dict(result, not_null=True):
                    result.update(data)
                    is_updated = True
                else:
                    result = data
            else:
                result = data
        return result, is_updated

    def control_node_data_len(self,
                              formatted_node: str):
        """Control inputs data cache length"""
        time_keys = self.get_keys_by_node(
            formatted_node=formatted_node
        )
        if Ut.is_list(time_keys, not_null=True):
            nb_items = len(time_keys)
            if nb_items > self._max_rows:
                nb_del = nb_items - self._max_rows
                # register invalid keys to delete
                to_del = [
                    time_key
                    for time_key in time_keys
                    if not Ut.is_int(time_key, positive=True)
                ]

                if nb_del > 0:
                    to_del = to_del + time_keys[0: nb_del]

                if Ut.is_list(to_del, not_null=True):
                    self.api.del_hmap_keys(
                        formatted_node,
                        to_del
                    )

    def register_node(self,
                      node_name: str,
                      node: str):
        """Register node and save on redis."""
        result = False
        node = HmapTimeSeriesApp.get_map_key(
            key=node,
            node_base=self.node_base
        )
        if Ut.is_str(node, not_null=True)\
                and node not in self._nodes:
            if self.api.add_set_members(
                        node_name,
                        [node]
                    ) == 1:
                self._nodes.append(node)
                result = True
        return result

    def add_time_serie_to_node(self,
                               time_key: int,
                               node: str,
                               data: dict
                               ):
        """Set inputs data cache key on redis."""
        result = False
        time_key = Ut.get_int(time_key, 0)
        if self.is_ready():
            formatted_node = HmapTimeSeriesApp.get_map_key(
                key=node,
                node_base=self.node_base
            )
            data, is_updated = self.update_or_set_data_node_key(
                formatted_node=formatted_node,
                time_key=time_key,
                data=data
            )
            if Ut.is_dict(data, not_null=True):
                data_in = UJson.dumps_json(data)
                nb_added = self.api.set_hmap_data(
                    formatted_node,
                    Ut.get_str(time_key),
                    values=data_in
                )
                # nb_added
                if nb_added == 1\
                        or (is_updated is True and nb_added == 0):
                    result = True
            self.control_node_data_len(
                formatted_node=formatted_node
            )
        return result

    def enum_node_data_interval(self,
                                formatted_node: str,
                                keys: list
                                ):
        """Enumerate data cache interval."""
        if Ut.is_str(formatted_node, not_null=True)\
                and Ut.is_list(keys, not_null=True):

            data = self.api.get_hmap_data(
                formatted_node,
                keys
            )
            if Ut.is_list(data, not_null=True) \
                    and len(data) == len(keys):
                for i, item in enumerate(data):
                    if Ut.is_str(item, not_null=True):
                        values = UJson.loads_json(item)
                        key = keys[i]
                        if Ut.is_int(key, positive=True)\
                                and Ut.is_dict(values, not_null=True):
                            yield key, values

    def get_redis_time_series(self,
                              node_name: str,
                              from_time: int = 0,
                              nb_items: int = 0,
                              structure: Optional[dict] = None
                              ) -> tuple:
        """
        Get time series data to extract.
        ToDo: This method must be simplified and improved
        """
        result, max_time = None, 0
        # ToDo: Remove is_ready test and play with redis_api exceptions
        if self.is_ready():
            result = {}
            nodes = None

            is_structure = Ut.is_dict(structure, not_null=True)
            if is_structure:
                nodes = list(structure.keys())

            for node, keys in self.enum_node_keys(
                    node_name=node_name,
                    nodes=nodes,
                    nb_items=nb_items,
                    from_time=from_time
            ):
                if Ut.is_list(keys, not_null=True):
                    node_name = HmapTimeSeriesApp.get_node_from_map_key(
                        key=node,
                        node_base=self.node_base
                    )

                    max_time = Ut.get_max_in_loop(
                        value=max_time,
                        max_val=max(keys)
                    )

                    for key, values in self.enum_node_data_interval(
                            formatted_node=node,
                            keys=keys):
                        Ut.init_dict_key(result, key, {})

                        if is_structure:
                            result[key].update({
                                node_name: Ut.get_items_from_dict(
                                    values,
                                    structure.get(node_name)
                                )
                            })
                        else:
                            result[key].update({
                                node_name: values
                            })
            if Ut.is_dict(result, not_null=True):
                result = dict(sorted(result.items()))
        return result, max_time

    def get_data_time_series(self,
                             node_name: str,
                             from_time: int = 0,
                             nb_items: int = 0,
                             structure: Optional[dict] = None
                             ) -> tuple:
        """
        Get data cache extract.
        """
        last_time = 0
        result, max_time = self.get_redis_time_series(
            node_name=node_name,
            from_time=from_time,
            nb_items=nb_items,
            structure=structure
        )
        is_valid_data = Ut.is_dict(result, min_items=1)

        if is_valid_data:
            last_time = max(result) + 1

        return result, last_time, max_time

    @staticmethod
    def get_interval_keys(keys: list) -> int:
        """Get time interval from hmap keys."""
        result = 0
        if Ut.is_list(keys, not_null=True):
            i = 0
            tmp = 0
            rows = []
            for item_time in keys:
                if i > 0:
                    rows.append(item_time - tmp)
                tmp = item_time
                i += 1
            nb_rows = len(rows)
            if nb_rows > 1:
                result = min(rows)
            elif nb_rows == 1:
                result = rows[0]
        return result

    @staticmethod
    def get_keys_section(structure: list,
                         nb_items: int
                         ) -> int:
        """Get time interval from hmap keys."""
        result = None
        if Ut.is_list(structure, not_null=True)\
                and Ut.is_int(nb_items, positive=True):
            result = {}
            nb_in = 0
            last_cache_key = 0
            for node, interval, cache_key in structure:
                if nb_in < nb_items\
                        or last_cache_key == cache_key:
                    if node not in result:
                        result[node] = []
                    result[node].append(cache_key)
                    if cache_key > 0 and last_cache_key != cache_key:
                        nb_in += 1
                    last_cache_key = cache_key
                else:
                    break
        return result

    @staticmethod
    def get_map_key(key: str,
                    node_base: Optional[str] = None
                    ) -> Optional[str]:
        """Get formatted redis hmap key for input cache data"""
        result = None
        if Ut.is_str(key, not_null=True):
            if Ut.is_str(node_base, not_null=True):
                result = f"{node_base}_{key}"
            else:
                result = f"{key}"
        return result

    @staticmethod
    def get_node_from_map_key(key: str,
                              node_base: Optional[str] = None
                              ) -> Optional[str]:
        """Get formatted redis hmap key for input cache data"""
        result = None
        if Ut.is_str(key, not_null=True):
            if Ut.is_str(node_base, not_null=True):
                nb = len(node_base)+1
                result = key[nb:]
            else:
                result = key
        return result
