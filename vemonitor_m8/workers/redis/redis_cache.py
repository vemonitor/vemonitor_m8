#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Redis vemonitor Helper"""
import logging
from typing import Optional, Union
from ve_utils.ujson import UJson
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
                 connector: Optional[Union[dict, RedisApp]] = None
                 ):
        self.app = None
        self.set_redis_app(connector=connector)
        self.cache_temp = None

    def is_ready(self):
        """Test if redis connection is ready"""
        return RedisConnector.is_app_ready(self.app)

    def set_redis_app(self,
                      connector: Optional[Union[dict, RedisApp]] = None
                      ) -> bool:
        """Test if redis connection is ready"""
        if RedisConnector.is_redis_app(connector):
            self.app = connector
        elif Ut.is_dict(connector, not_null=True):
            connector.pop('active')
            self.app = RedisApp(credentials=connector)
        return self.is_ready()

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

    def get_cache_nodes_keys_list(self, nodes: Optional[list] = None) -> list:
        """
        Get list of inputs nodes keys from redis set cache data.
        ToDo:
            - if self.app.api.get_set_members(self.cache_name) return None
              list() may throw an exception.
              May caused by redis error (can be unreachable server).
        """
        result = None
        if self.is_ready():
            result = list(
                self.app.api.get_set_members(self.cache_name)
            )
            if Ut.is_list(nodes, not_null=True):
                result = [x
                          for x in result
                          if x in RedisCache.get_cache_map_key(x)]
        return result

    def get_cache_keys_by_node(self,
                               node: str,
                               from_time: int = 0
                               ) -> list:
        """Get formatted hmap keys."""
        result = None
        if self.is_ready():
            keys = self.app.api.get_hmap_keys(node)
            if Ut.is_list(keys, not_null=True):
                keys.sort()
                if Ut.is_int(from_time, positive=True):
                    result = [Ut.get_int(x, 0)
                              for x in keys
                              if InputsCache.is_from_time(
                                item_time=Ut.get_int(x),
                                from_time=from_time
                              )]
                else:
                    result = [Ut.get_int(x, 0) for x in keys]
        return result

    def enum_cache_keys(self,
                        nodes: Optional[list] = None,
                        from_time: int = 0
                        ):
        """Get list of inputs nodes keys from redis cache data."""
        if self.is_ready():
            node_keys = self.get_cache_nodes_keys_list(nodes)
            if Ut.is_list(node_keys, not_null=True):
                for node in node_keys:
                    yield node, self.get_cache_keys_by_node(
                        node=node,
                        from_time=from_time
                    )

    def reset_data_cache(self) -> list:
        """Reset data cache for all nodes."""
        result = None
        if self.app.api.set_pipeline():
            for node, keys in self.enum_cache_keys():
                if Ut.is_list(keys, not_null=True):
                    self.app.api.del_hmap_keys(
                        name=node,
                        keys=keys,
                        client=self.app.api.pipe
                    )
            try:
                result = self.app.api.pipe.execute()
            except Exception as ex:
                logger.error(
                    "[InputRedisCache::reset_all_data_cache] "
                    "Unable to reset all cache data. "
                    "ex : %s",
                    ex
                )
        return result

    def _update_or_set_data_node_key(self,
                                     node: str,
                                     time_key: int,
                                     data: dict
                                     ) -> Optional[dict]:
        """Update or set data key."""
        result = None
        if self.is_ready()\
                and Ut.is_int(time_key, positive=True)\
                and Ut.is_str(node, not_null=True)\
                and Ut.is_dict(data, not_null=True):
            data_in = self.app.api.get_hmap_data(
                node,
                str(time_key)
            )
            if Ut.is_str(data_in, not_null=True):
                result = UJson.loads_json(data_in)
                if Ut.is_dict(result, not_null=True):
                    result.update(data)
                else:
                    result = data
            else:
                result = data
        return result

    def control_node_data_len(self, node: str):
        """Control inputs data cache length"""
        keys = self.get_cache_keys_by_node(node=node)
        if Ut.is_list(keys, not_null=True):
            nb_items = len(keys)
            if nb_items > self._max_rows:
                nb_del = nb_items - self._max_rows
                # register invalid keys to delete
                to_del = [x for x in keys if not Ut.is_int(x, positive=True)]

                if nb_del > 0:
                    to_del = to_del + keys[0: nb_del]

                if Ut.is_list(to_del, not_null=True):
                    self.app.api.del_hmap_keys(node, to_del)

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
                       key: str,
                       data: dict
                       ):
        """Set inputs data cache key on redis."""
        result = False
        time_key = Ut.get_int(time_key, 0)
        if self.is_ready():
            node = RedisCache.get_cache_map_key(key=key)
            data = self._update_or_set_data_node_key(
                node=node,
                time_key=time_key,
                data=data
            )
            if Ut.is_dict(data, not_null=True):
                data_in = UJson.dumps_json(data)

                if self.app.api.set_hmap_data(
                            node,
                            time_key,
                            values=data_in
                        ) == 1:

                    result = True
            self.control_node_data_len(node=node)
        return result

    def enum_node_data_cache_interval(self,
                                      node: str,
                                      keys: list
                                      ):
        """Enumerate data cache interval."""
        if Ut.is_str(node, not_null=True)\
                and Ut.is_list(keys, not_null=True):

            data = self.app.api.get_hmap_data(
                node,
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
        """
        result, max_time = None, 0
        if self.is_ready() \
                and Ut.is_dict(structure, not_null=True):
            result = dict()

            for node, keys in self.enum_cache_keys(
                    nodes=list(structure.keys()),
                    from_time=from_time
            ):
                if Ut.is_list(keys, not_null=True)\
                        and 0 < nb_items <= len(keys):
                    node_name = node[4:]
                    max_time = Ut.get_max_in_loop(
                        value=max_time,
                        max_val=max(keys) - 1
                    )
                    if nb_items > 0:
                        keys = keys[0: nb_items]

                    for key, values in self.enum_node_data_cache_interval(
                            node=node,
                            keys=keys):
                        Ut.init_dict_key(result, key, dict())

                        result[key].update({
                            node_name: Ut.get_items_from_dict(
                                values,
                                structure.get(node_name)
                            )
                        })
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
        if Ut.is_dict(result, min_items=nb_items):

            start_time, end_time = self.get_time_interval(
                from_time=from_time,
                nb_items=nb_items,
                start_time=min(result),
            )

            result, last_time = RedisCache.get_cache_by_start_time(
                start_time=start_time,
                end_time=end_time,
                nb_items=nb_items,
                data=result
            )

        return result, last_time, max_time

    def get_time_interval(self,
                          from_time: int,
                          nb_items: int,
                          start_time: int
                          ):
        """Register node and save on redis."""
        if from_time > 0:
            start_time = from_time
        end_time = start_time + (nb_items * self._interval_min)
        return start_time, end_time

    @staticmethod
    def get_cache_by_start_time(start_time: int,
                                end_time: int,
                                nb_items: int,
                                data: dict
                                ) -> tuple:
        """Get cache data by start time."""
        result, last_time = None, 0
        if Ut.is_dict(data, not_null=True) \
                and Ut.is_int(start_time, positive=True) \
                and Ut.is_int(nb_items, positive=True):
            keys = list(data.keys())
            keys.sort()
            keys = [x for x in keys if x >= start_time]
            keys = keys[:nb_items]
            if Ut.is_dict(data, not_null=True) \
                    and Ut.is_list(keys, not_null=True):
                result = {}
                for key, value in data.items():
                    if key in keys:
                        keys.pop(keys.index(key))
                        result.update({key: value})
                if Ut.is_dict(result, not_null=True):
                    last_time = max(result) + 1
            return result, last_time

    @staticmethod
    def get_cache_from_time_interval(start_time: int,
                                     end_time: int,
                                     nb_items: int,
                                     data: dict
                                     ) -> tuple:
        """
        Get cache data from time interval and nb of results.
        """
        result, last_time = None, 0
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_int(end_time, positive=True)\
                and 0 < start_time < end_time:
            result = {key: value
                      for key, value in data.items()
                      if start_time <= key < end_time}
            if Ut.is_dict(result, not_null=True):
                last_time = max(result) + 1
            else:
                result = {}
                nb_get = 0
                for key, value in data.items():
                    if start_time <= key and nb_get < 10:
                        result.update({key:value})
                        nb_get += 1

                if Ut.is_dict(result, not_null=True):
                    last_time = max(result) + 1

        return result, last_time

    @staticmethod
    def get_cache_map_key(key: str) -> str:
        """Get formatted redis hmap key for input cache data"""
        return f"ric_{key}"
