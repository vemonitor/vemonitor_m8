#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Redis vemonitor Helper"""
import logging
from operator import itemgetter
from typing import Optional, Union
from ve_utils.ujson import UJson
from vemonitor_m8.core.exceptions import DataCacheError
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.inputs_cache import InputsCache
from vemonitor_m8.workers.redis.redis_app import RedisApp

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "GPLv3"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class RedisConnector:
    """
       vemonitor Redis Cache Outputs Helper
    """
    def __init__(self,
                 connector: Union[dict, RedisApp]
                 ):
        self.app = None
        self.set_redis_app(connector=connector)
        self.cache_temp = None

    def is_ready(self):
        """Test if redis connection is ready"""
        return RedisConnector.is_app_ready(self.app)

    def set_redis_app(self,
                      connector: Union[dict, RedisApp]
                      ) -> bool:
        """Set up RedisApp"""
        result = False
        if RedisConnector.is_redis_app(connector):
            self.app = connector
            result = self.is_ready()
        elif Ut.is_dict(connector, not_null=True):
            if 'active' in connector:
                connector.pop('active')
            self.app = RedisApp(credentials=connector)
            result = self.is_ready()
        return result

    @staticmethod
    def is_redis_app(app: RedisApp) -> bool:
        """Test if redis connection is ready"""
        return isinstance(app, RedisApp)

    @staticmethod
    def is_app_ready(app: RedisApp) -> bool:
        """Test if redis connection is ready"""
        return RedisConnector.is_redis_app(app) and app.is_ready()


class RedisCache(RedisConnector, InputsCache):
    """
       vemonitor Redis Cache by node Outputs Helper
    """
    def __init__(self,
                 max_rows: int = 10,
                 connector: Optional[Union[dict, RedisApp]] = None,
                 reset_at_start: bool = True
                 ):
        RedisConnector.__init__(self,
                                connector=connector)
        InputsCache.__init__(self,
                             max_rows=max_rows)
        self.cache_name = "inputs_cache"
        self._nodes = []
        if reset_at_start is True:
            self.reset_data_cache()

    def is_ready(self):
        """Init inputs data cache"""
        return self.app.ping() and self.app.is_ready()

    def has_data(self):
        """Init inputs data cache"""
        return True

    def get_cache_nodes_keys_list(self,
                                  nodes: Optional[list] = None
                                  ) -> list:
        """
        Get list of inputs nodes keys from redis set cache data.
        ToDo:
            - if self.app.api.get_set_members(self.cache_name) return None
              list() may throw an exception.
              May caused by redis error (can be unreachable server).
        """
        result = list(
            self.app.api.get_set_members(self.cache_name)
        )
        if Ut.is_list(nodes, not_null=True):
            formated_nodes = [
                RedisCache.get_cache_map_key(x)
                for x in nodes
            ]
            result = [
                x
                for x in result
                if x in formated_nodes
            ]
        return result

    def get_cache_keys_by_node(self,
                               formatted_node: str,
                               from_time: int = 0
                               ) -> list:
        """Get formatted hmap keys."""
        result = None
        keys = self.app.api.get_hmap_keys(formatted_node)
        if Ut.is_list(keys, not_null=True):
            keys.sort()
            if Ut.is_int(from_time, positive=True):
                result = [
                    Ut.get_int(x, 0)
                    for x in keys
                    if InputsCache.is_from_time(
                            item_time=Ut.get_int(x),
                            from_time=from_time
                        )
                ]
            else:
                result = [Ut.get_int(x, 0) for x in keys]
        return result

    def get_cache_keys_structure(self,
                                 node_keys: list,
                                 nb_items: int,
                                 from_time: int = 0
                                 ) -> int:
        """Get time interval from hmap keys."""
        structure = None
        if Ut.is_list(node_keys, not_null=True):
            structure = []
            for node in node_keys:
                keys = self.get_cache_keys_by_node(
                    formatted_node=node,
                    from_time=from_time
                )
                if Ut.is_list(keys, not_null=True):
                    interval = RedisCache.get_interval_keys(keys)
                    for cache_key in keys:
                        structure.append((node, interval, cache_key))
            if Ut.is_list(structure, not_null=True):
                structure = sorted(structure, key=itemgetter(2))
                structure = RedisCache.get_cache_keys_section(
                    structure=structure,
                    nb_items=nb_items
                )
        return structure

    def enum_cache_keys(self,
                        nodes: Optional[list] = None,
                        nb_items: int = 0,
                        from_time: int = 0
                        ):
        """Get list of inputs nodes keys from redis cache data."""
        if self.is_ready():
            node_keys = self.get_cache_nodes_keys_list(nodes)
            if Ut.is_list(node_keys, not_null=True):
                if nb_items > 0:
                    structure = self.get_cache_keys_structure(
                        node_keys=node_keys,
                        nb_items=nb_items,
                        from_time=from_time,
                    )

                    for node, cache_keys in structure.items():
                        yield node, cache_keys
                else:
                    for node in node_keys:
                        yield node, self.get_cache_keys_by_node(
                            formatted_node=node,
                            from_time=from_time
                        )

    def reset_data_cache(self) -> list:
        """Reset data cache for all nodes."""
        result = None
        if self.app.api.set_pipeline():
            try:
                # Remove data cache
                for node, keys in self.enum_cache_keys():
                    if Ut.is_list(keys, not_null=True):
                        self.app.api.del_hmap_keys(
                            name=node,
                            keys=keys,
                            client=self.app.api.pipe
                        )
                # Remove Nodes list set
                node_keys = self.get_cache_nodes_keys_list()
                if Ut.is_list(node_keys, not_null=True):
                    self.app.api.remove_set_members(
                        name=self.cache_name,
                        values=node_keys,
                        client=self.app.api.pipe
                    )
                # execute pipe
                result = self.app.api.pipe.execute()
            except BaseException as ex:
                logger.error(
                    "[InputRedisCache::reset_all_data_cache] "
                    "Unable to reset all cache data. "
                    "ex : %s",
                    ex
                )
                raise DataCacheError(
                    "[RedisApi:set_pipeline] "
                    "Fatal Error : Unable to set pipeline."
                ) from ex
        return result

    def _update_or_set_data_node_key(self,
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
            data_in = self.app.api.get_hmap_data(
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

    def control_node_data_len(self, formatted_node: str):
        """Control inputs data cache length"""
        time_keys = self.get_cache_keys_by_node(formatted_node=formatted_node)
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
                    self.app.api.del_hmap_keys(
                        formatted_node,
                        to_del
                    )

    def register_node(self, node: str):
        """Register node and save on redis."""
        result = False
        node = RedisCache.get_cache_map_key(key=node)
        if Ut.is_str(node, not_null=True)\
                and node not in self._nodes:
            if self.app.api.add_set_members(
                        self.cache_name,
                        [node]
                    ) == 1:
                self._nodes.append(node)
                result = True
        return result

    def add_data_cache(self,
                       time_key: int,
                       node: str,
                       data: dict
                       ):
        """Set inputs data cache key on redis."""
        result = False
        time_key = Ut.get_int(time_key, 0)
        if self.is_ready():
            formatted_node = RedisCache.get_cache_map_key(key=node)
            data, is_updated = self._update_or_set_data_node_key(
                formatted_node=formatted_node,
                time_key=time_key,
                data=data
            )
            if Ut.is_dict(data, not_null=True):
                data_in = UJson.dumps_json(data)
                nb_added = self.app.api.set_hmap_data(
                    formatted_node,
                    Ut.get_str(time_key),
                    values=data_in
                )
                # nb_added
                if nb_added == 1\
                        or (is_updated is True and nb_added == 0):
                    result = True
            self.control_node_data_len(formatted_node=formatted_node)
        return result

    def enum_node_data_cache_interval(self,
                                      formatted_node: str,
                                      keys: list
                                      ):
        """Enumerate data cache interval."""
        if Ut.is_str(formatted_node, not_null=True)\
                and Ut.is_list(keys, not_null=True):

            data = self.app.api.get_hmap_data(
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

    def get_data_from_redis(self,
                            from_time: int = 0,
                            nb_items: int = 0,
                            structure: Optional[dict] = None
                            ) -> tuple:
        """
        Get data cache extract.
        ToDo: This method must be simplified and improved
        """
        result, max_time = None, 0
        # ToDo: Remove is_ready test and play with redis_api exceptions
        if self.is_ready():
            result = dict()
            nodes = None

            is_structure = Ut.is_dict(structure, not_null=True)
            if is_structure:
                nodes = list(structure.keys())

            for node, keys in self.enum_cache_keys(
                    nodes=nodes,
                    nb_items=nb_items,
                    from_time=from_time
            ):
                if Ut.is_list(keys, not_null=True):
                    node_name = node[4:]

                    max_time = Ut.get_max_in_loop(
                        value=max_time,
                        max_val=max(keys)
                    )

                    for key, values in self.enum_node_data_cache_interval(
                            formatted_node=node,
                            keys=keys):
                        Ut.init_dict_key(result, key, dict())

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

    def get_data_from_cache(self,
                            from_time: int = 0,
                            nb_items: int = 0,
                            structure: Optional[dict] = None
                            ) -> tuple:
        """
        Get data cache extract.
        
        """
        last_time = 0
        result, max_time = self.get_data_from_redis(
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
            result = min(rows)
        return result

    @staticmethod
    def get_cache_keys_section(structure: list,
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
    def get_cache_map_key(key: str) -> str:
        """Get formatted redis hmap key for input cache data"""
        return f"ric_{key}"
