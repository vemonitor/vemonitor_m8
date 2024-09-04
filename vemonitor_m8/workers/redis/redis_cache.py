#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Redis vemonitor Helper.
"""
import logging
from typing import Optional, Union
from vemonitor_m8.core.exceptions import DataCacheError
from vemonitor_m8.core.exceptions import RedisAppException
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.inputs_cache import InputsCache
from vemonitor_m8.workers.redis.redis_h_time_series\
    import HmapTimeSeriesApp

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class RedisConnector:
    """
       vemonitor Redis Cache Outputs Helper
    """
    def __init__(self,
                 connector: Union[dict, HmapTimeSeriesApp],
                 max_rows: int = 3600
                 ):
        self.app = None
        self.set_redis_app(
            connector=connector,
            max_rows=max_rows
        )
        self.cache_temp = None

    def is_ready(self):
        """Test if redis connection is ready"""
        return RedisConnector.is_app_ready(self.app)

    def set_redis_app(self,
                      connector: Union[dict, HmapTimeSeriesApp],
                      max_rows: int = 3600
                      ) -> bool:
        """Set up HmapTimeSeriesApp"""
        result = False
        if RedisConnector.is_redis_app(connector):
            self.app = connector
            result = self.is_ready()
        elif Ut.is_dict(connector, not_null=True):
            if 'active' in connector:
                connector.pop('active')
            self.app = HmapTimeSeriesApp(
                credentials=connector,
                max_rows=max_rows
                )
            result = self.is_ready()
        return result

    @staticmethod
    def is_redis_app(app: HmapTimeSeriesApp) -> bool:
        """Test if redis connection is ready"""
        return isinstance(app, HmapTimeSeriesApp)

    @staticmethod
    def is_app_ready(app: HmapTimeSeriesApp) -> bool:
        """Test if redis connection is ready"""
        return RedisConnector.is_redis_app(app) and app.is_ready()


class RedisCache(RedisConnector, InputsCache):
    """
       vemonitor Redis Cache by node Outputs Helper
    """
    def __init__(self,
                 max_rows: int = 10,
                 connector: Optional[Union[dict, HmapTimeSeriesApp]] = None,
                 reset_at_start: bool = True
                 ):
        RedisConnector.__init__(self,
                                connector=connector,
                                max_rows=max_rows
                                )
        InputsCache.__init__(self,
                             max_rows=max_rows
                             )
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

    def set_max_rows(self, value: int) -> bool:
        """Set interval_min property."""
        result = False
        if Ut.is_int(value, positive=True):
            self._max_rows = value
            self.app.set_max_rows(value)
            result = True
        return result

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
        return self.app.get_nodes_keys_list(
            node_name=self.cache_name,
            nodes=nodes
        )

    def get_cache_keys_by_node(self,
                               formatted_node: str,
                               from_time: int = 0
                               ) -> list:
        """Get formatted hmap keys."""
        return self.app.get_keys_by_node(
            formatted_node=formatted_node,
            from_time=from_time
        )

    def get_cache_keys_structure(self,
                                 node_keys: list,
                                 nb_items: int,
                                 from_time: int = 0
                                 ) -> int:
        """Get time interval from hmap keys."""
        return self.app.get_keys_structure(
            node_keys=node_keys,
            nb_items=nb_items,
            from_time=from_time
        )

    def enum_cache_keys(self,
                        nodes: Optional[list] = None,
                        nb_items: int = 0,
                        from_time: int = 0
                        ):
        """Get list of inputs nodes keys from redis cache data."""
        if self.is_ready():
            for node, cache_keys in self.app.enum_node_keys(
                    node_name=self.cache_name,
                    nodes=nodes,
                    nb_items=nb_items,
                    from_time=from_time):
                yield node, cache_keys

    def reset_data_cache(self) -> list:
        """Reset data cache for all nodes."""
        result = None
        try:
            result = self.app.reset_node_data(
                node_name=self.cache_name
            )
        except RedisAppException as ex:
            logger.error(
                "[InputRedisCache::reset_data_cache] "
                "Unable to reset all cache data. "
                "ex : %s",
                ex
            )
            raise DataCacheError(
                "[InputRedisCache:reset_data_cache] "
                "Fatal Error : Unable to set pipeline."
            ) from ex
        return result

    def _update_or_set_data_node_key(self,
                                     formatted_node: str,
                                     time_key: int,
                                     data: dict
                                     ) -> tuple:
        """Update or set data key."""
        return self.app.update_or_set_data_node_key(
            formatted_node=formatted_node,
            time_key=time_key,
            data=data
        )

    def control_node_data_len(self, formatted_node: str):
        """Control inputs data cache length"""
        self.app.control_node_data_len(
            formatted_node=formatted_node
        )

    def register_node(self, node: str):
        """Register node and save on redis."""
        return self.app.register_node(
            node_name=self.cache_name,
            node=node
        )

    def add_data_cache(self,
                       time_key: int,
                       node: str,
                       data: dict
                       ):
        """Set inputs data cache key on redis."""
        isvalid_structure = self.app.control_server_structure(
            redis_node=self.cache_name
        )

        is_added = self.app.add_time_serie_to_node(
            time_key=time_key,
            node=node,
            data=data
        )
        return is_added and isvalid_structure

    def enum_node_data_cache_interval(self,
                                      formatted_node: str,
                                      keys: list
                                      ):
        """Enumerate data cache interval."""
        for key, values in self.app.enum_node_data_interval(
                    formatted_node=formatted_node,
                    keys=keys
                ):
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
        return self.app.get_redis_time_series(
            node_name=self.cache_name,
            from_time=from_time,
            nb_items=nb_items,
            structure=structure
        )

    def get_data_from_cache(self,
                            from_time: int = 0,
                            nb_items: int = 0,
                            structure: Optional[dict] = None
                            ) -> tuple:
        """
        Get data cache extract.
        """
        return self.app.get_data_time_series(
            node_name=self.cache_name,
            from_time=from_time,
            nb_items=nb_items,
            structure=structure
        )
