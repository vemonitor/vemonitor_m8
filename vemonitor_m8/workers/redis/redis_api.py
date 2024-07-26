# -*- coding: utf-8 -*-
"""Redis vemonitor Helper"""
import logging
from typing import Optional, Union
from redis.client import Redis
from redis.commands.timeseries import TimeSeries
from redis.exceptions import RedisError
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.core.exceptions import RedisConnectionException, RedisVeError

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class RedisCli:
    """Redis Cli Helper"""
    def __init__(self,
                 host: str = None,
                 port: int = None,
                 db: int = 3,
                 password: str = None):
        self.cli = None
        self.pipe = None
        self._credentials = {
            'host': host,
            'port': port,
            'db': db,
            'password': password,
            'decode_responses': True
        }
        self.connect_to_redis()

    def is_ready(self) -> bool:
        """Test if cli is redis client instance and if redis ping return True"""
        return RedisCli.is_redis_client(self.cli)

    def has_timeseries(self) -> bool:
        """Test if timeseries is available"""
        return isinstance(self.cli.ts(), TimeSeries)

    def is_connected(self) -> bool:
        """Test if cli is redis client instance and if redis ping return True"""
        return RedisCli.is_redis_client_connected(self.cli)

    def get_redis_client(self, client: Redis) -> Redis:
        """Return Redis client"""
        if RedisCli.is_redis_client(client):
            return client
        return self.cli

    def connect_to_redis(self,
                         credentials: Optional[dict] = None
                         ) -> bool:
        """
        Connect to redis server.

        Use credentials parameter if is set or self._credentials property if not.
        Credentials must be a dictionary with :
            - host: str: The redis server host
            - port: int: The redis server port
            - db: int: The redis server db (0 by default)
            - password: str: The redis server password if any
            - decode_responses: bool: The redis server decode_responses option
        :Example :
            >>> self.connect_to_redis()
            >>> True
        :param credentials: dict: Dictionary with host, port, db and password data
        :return: bool: Return True if conexion to redis server success.
        """
        result = False
        try:
            if not RedisCli.is_redis_credentials(credentials):
                credentials = self._credentials
            self.cli = Redis(**credentials)

            if not self.is_ready() or not self.is_connected():
                logger.error(
                    "[RedisCli::connect_to_redis] "
                    "Failed to connect to redis server. host: %s",
                    credentials.get("host")
                )
                raise RedisConnectionException(
                    "[RedisCli::connect_to_redis] "
                    "Failed to connect to redis server. "
                    f"host: {credentials.get('host')}"
                )

            logger.info(
                "[RedisCli::connect_to_redis] "
                "Redis Server ready and connection started on host: %s",
                credentials.get("host")
            )
            result = True
        except (RedisError, TypeError) as ex:
            logger.error(
                "[RedisCli::connect_to_redis] "
                "Failed to connect to redis server, ex : %s",
                ex
            )
            raise RedisConnectionException(
                "[RedisCli::connect_to_redis] "
                "Failed to connect to redis server."
            ) from ex
        return result

    def set_pipeline(self) -> bool:
        """
        Set redis pipeline
        """
        result = False
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi:set_pipeline] Fatal Error : Unable to set pipeline, "
                    "Redis connection is down, try to reconnect."
                )
            self.pipe = self.cli.pipeline()
            result = True
        except RedisError as ex:
            logger.debug(
                "[RedisApi:set_pipeline] Fatal Error : Unable to set pipeline. ex : %s",
                ex
            )
            raise RedisVeError(
                "[RedisApi:set_pipeline] Fatal Error : Unable to set pipeline."
            ) from ex

        return result

    def flush(self) -> bool:
        """
        Delete all data on actual db.
        """
        result = False
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi:flush] "
                    "Fatal Error : Unable to flush redis db, "
                    "Redis connection is down, try to reconnect."
                )
            self.cli.flushdb()
            result = True
        except RedisError as ex:
            logger.debug(
                "[RedisCli:flush] "
                "Fatal Error : Unable to flush redis db. ex : %s",
                ex
            )
            raise RedisVeError(
                "[RedisCli:flush] "
                "Fatal Error : Unable to flush redis db."
            ) from ex

        return result

    @staticmethod
    def is_redis_credentials(credentials) -> bool:
        """Test if client is redis client instance"""
        return Ut.is_dict(credentials, not_null=True)\
            and Ut.is_valid_host(credentials.get("host")) \
            and Ut.is_valid_port(credentials.get("port"))

    @staticmethod
    def is_redis_client(client: Redis) -> bool:
        """Test if client is redis client instance"""
        return isinstance(client, Redis)

    @staticmethod
    def is_redis_client_connected(client: Redis) -> bool:
        """Test if client is redis client instance and if redis ping return True"""
        result = False
        try:
            result = RedisCli.is_redis_client(client) and client.ping()
        except RedisError as ex:
            logger.debug(
                "[RedisCli:is_redis_client_connected] Ping failed from redis server, ex : %s",
                ex
            )
        return result


class RedisBase(RedisCli):
    """Redis Cli Helper"""
    def __init__(self, credentials: dict):
        RedisCli.__init__(self, **credentials)

    def get_key_type(self, key: str, client: Redis = None):
        """
        Returns the string representation of the type of the value stored at key.

        The different types that can be returned are:
        string, list, set, zset, hash and stream.

        @keyspace, @read, @fast
        """
        result = None
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi:get_key_type] "
                    "Fatal Error : Unable to get key type, "
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            result = client.type(key)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisBase::get_key_type] "
                "Failed to get key type. "
                "(key: %s) ex : %s",
                key, ex
            )
            raise RedisVeError(
                "[RedisBase::get_key_type] "
                "Failed to get key type. "
                f"key: {key}."
            ) from ex
        return result

    def save_redis_data_on_disk(self) -> bool:
        """
        Save the DB in background.

        Normally the OK code is immediately returned.
        Redis forks, the parent continues to serve the clients,
        the child saves the DB on disk then exits.

        An error is returned if there is already a background save running
        or if there is another non-background-save process running,
        specifically an in-progress AOF rewrite.

        If BGSAVE SCHEDULE is used, the command will immediately return OK
        when an AOF rewrite is in progress
        and schedule the background save to run at the next opportunity.

        A client may be able to check if the operation succeeded
        using the LASTSAVE command.

        @admin, @slow, @dangerous
        """
        result = False
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisBase::save_redis_data_on_disk] "
                    "Fatal Error : Failed to save redis data on disk."
                    "Redis connection is down, try to reconnect."
                )
            result = self.cli.bgsave()
        except RedisError as ex:
            logger.debug(
                "[RedisBase::save_redis_data_on_disk] "
                "Fatal Error : Failed to save redis data on disk."
                " ex : %s",
                ex
            )
            raise RedisVeError(
                "[RedisBase::save_redis_data_on_disk] "
                "Fatal Error : Failed to save redis data on disk."
            ) from ex
        return result

    def get_redis_info_usage(self,
                             section: Optional[str] = None,
                             keys: Optional[list] = None,
                             full: bool = False
                             ) -> Optional[dict]:
        """
        The INFO command returns information and statistics about the server.

        In a format that is simple to parse by computers
        and easy to read by humans.

        The optional parameter can be used
        to select a specific section of information:

            - server: General information about the Redis server
            - clients: Client connections section
            - memory: Memory consumption related information
            - persistence: RDB and AOF related information
            - stats: General statistics
            - replication: Master/replica replication information
            - cpu: CPU consumption statistics
            - commandstats: Redis command statistics
            - latencystats: Redis command latency percentile distribution statistics
            - cluster: Redis Cluster section
            - modules: Modules section
            - keyspace: Database related statistics
            - modules: Module related sections
            - errorstats: Redis error statistics
        @slow, @dangerous
        """
        result = None
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisBase::get_redis_info_usage] "
                    "Fatal Error : Unable to get redis info."
                    "Redis connection is down, try to reconnect."
                )
            if Ut.is_str(section, not_null=True):
                info = self.cli.info(section)
            else:
                info = self.cli.info()

            if full is False:
                if Ut.is_dict(info, not_null=True):
                    default_keys = RedisBase.get_info_default_keys()
                    if Ut.is_list(keys, not_null=True):
                        result = Ut.get_items_from_dict(info, keys)
                    else:
                        result = Ut.get_items_from_dict(info, default_keys)
            else:
                result = info
        except RedisError as ex:
            logger.debug(
                "[RedisBase::get_redis_info_usage] "
                "Fatal Error : Unable to get redis info."
                "ex : %s",
                ex
            )
            raise RedisVeError(
                "[RedisBase::get_redis_info_usage] "
                "Fatal Error : Unable to get redis info."
            ) from ex
        return result

    @staticmethod
    def get_info_default_keys() -> list:
        """Return the default keys to return from info command."""
        return [
            'redis_version', 'arch_bits', 'os', 'uptime_in_seconds',
            'uptime_in_days', 'connected_clients', 'rdb_changes_since_last_save',
            'used_memory_human', 'used_memory_rss_human', 'used_memory_peak_human',
            'used_memory_peak_perc', 'total_system_memory_human',
            'rdb_changes_since_last_save', 'rdb_last_save_time',
            'total_connections_received', 'total_commands_processed',
            'instantaneous_ops_per_sec', 'total_net_input_bytes',
            'total_net_output_bytes'
        ]


class RedisApi(RedisBase):
    """Redis Cli Helper"""
    def __init__(self, credentials: dict):
        RedisBase.__init__(self, credentials)

    def get_hmap_len(self,
                     key: str,
                     client: Redis = None
                     ) -> int:
        """
        Returns the number of fields contained in the hash stored at key.

        @read, @hash, @fast
        """
        result = None
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::get_hmap_len] "
                    "Fatal Error : Failed to get hmap length."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            result = client.hlen(key)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::get_hmap_len] "
                "Failed to get hmap length. "
                "(key: %s) ex : %s",
                key, ex
            )
            raise RedisVeError(
                "[RedisApi::get_hmap_len] "
                "Failed to get hmap length. "
                f"(key: {key})."
            ) from ex
        return result

    def is_hmap_key(self,
                    name: str,
                    key: str,
                    client: Redis = None
                    ) -> Optional[bool]:
        """
        Returns if field is an existing field in the hash stored at key.

        @read, @hash, @fast
        """
        result = None
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::is_hmap_key] "
                    "Fatal Error : Failed to test if redis hmap key exist."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            result = client.hexists(name, key)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::is_hmap_key] "
                "Failed to test if redis hmap key exist. "
                f"(name: %s, key: %s) ex : %s",
                name, key, ex
            )
            raise RedisVeError(
                "[RedisApi::is_hmap_key] "
                "Failed to test if redis hmap key exist. "
                f"(name: {name}, key: {key})."
            ) from ex
        return result

    def get_hmap_keys(self,
                      name: str,
                      client: Redis = None
                      ) -> Optional[list]:
        """
        Returns all field names in the hash stored at key.

        @read, @hash, @slow
        """
        result = None
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::get_hmap_keys] "
                    "Fatal Error : Failed to get redis hmap keys."
                    "Redis connection is down, try to reconnect."
                )

            client = self.get_redis_client(client)
            result = client.hkeys(name)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::get_hmap_keys] "
                "Failed to get redis hmap keys. "
                "(name: %s) ex : %s",
                name, ex
            )
            raise RedisVeError(
                "[RedisApi::get_hmap_keys] "
                "Failed to get redis hmap keys. "
                f"(name: {name})."
            ) from ex
        return result

    def del_hmap_keys(self,
                      name: str,
                      keys: list,
                      client: Redis = None
                      ) -> int:
        """
        Removes the specified fields from the hash stored at key.

        Specified fields that do not exist within this hash are ignored.
        If key does not exist, it is treated as an empty hash
        and this command returns 0.

        @write, @hash, @fast
        """
        result = 0
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::del_hmap_keys] "
                    "Fatal Error : Failed to delete redis hmap keys."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            # Todo: Hdel ever return 0
            result = client.hdel(name, *keys)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::del_hmap_keys] "
                "Failed to delete redis hmap keys. "
                "(name: %s) ex : %s",
                name, ex
            )
            raise RedisVeError(
                "[RedisApi::del_hmap_keys] "
                "Failed to deleteget redis hmap keys. "
                f"(name: {name})."
            ) from ex
        return result

    def get_hmap_data(self,
                      name: str,
                      keys: Optional[Union[list, str]]=None,
                      client: Redis = None,
                      default=None
                      ) -> Union[list, str, dict]:
        """
        Get hmap data from redis server.

        Depending on keys type return:
            - keys: None: Run hgetall and return a dict.
            - keys: list: Run hmget and return a list
            - str: list: Run hget and return an str
        @read, @hash, @fast
        """
        result = default
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::get_hmap_data] "
                    "Fatal Error : Failed to get redis hmap data."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            if Ut.is_str(keys, not_null=True)\
                    or Ut.is_list(keys, not_null=True):
                result = client.hget(name, keys)
            else:
                result = client.hgetall(name)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::get_hmap_data] "
                "Failed to get redis hmap data"
                "(name: %s, keys: %s) ex : %s",
                name, keys, ex
            )
            raise RedisVeError(
                "[RedisApi::get_hmap_data] "
                "Failed to get redis hmap data"
                f"(name: {name}, keys: {keys})."
            ) from ex
        return result

    def set_hmap_data(self,
                      name: str,
                      key: Optional[str] = None,
                      values: Optional[str] = None,
                      client: Redis = None
                      )-> int:
        """
        Set hmap data on redis server.

        """
        result = 0
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::set_hmap_data] "
                    "Fatal Error : Failed to set redis hmap data."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            if Ut.is_str(key, not_null=True)\
                    and Ut.is_str(values, not_null=True):
                result = client.hset(
                    name=name,
                    key=key,
                    value=values
                )
            elif Ut.is_dict(values, not_null=True):
                result = client.hset(
                    name=name,
                    mapping=values
                )
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::set_hmap_data] "
                "Failed to set redis hmap data. "
                "(name: %s, key: %s) ex : %s",
                name, key, ex
            )
            raise RedisVeError(
                "[RedisApi::set_hmap_data] "
                "Failed to set redis hmap data. "
                f"(name: {name}, key: {key})."
            ) from ex
        return result

    def add_set_members(self,
                        name: str,
                        values: list,
                        client: Redis = None
                        )-> int:
        """
        Add members to set key.

        """
        result = 0
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::add_set_members] "
                    "Fatal Error : Failed to Add members to set key."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            result = client.sadd(name, *values)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::add_set_members] "
                "Failed to Add members to set key"
                "(name: %s, values: %s) ex : %s",
                name, values, ex
            )
            raise RedisVeError(
                "[RedisApi::add_set_members] "
                "Failed to Add members to set key"
                f"(name: {name}, values: {values})."
            ) from ex
        return result

    def remove_set_members(self,
                           name: str,
                           values: Union[list, tuple, bytes, memoryview, str, int, float],
                           client: Redis = None
                           ):
        """
        Remove members from set key.

        """
        result = 0
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::remove_set_members] "
                    "Fatal Error : Failed to Remove members from set key."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            result = client.srem(name, *values)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::remove_set_members] "
                "Failed to Remove members from set key"
                "(name: %s, values: %s) ex : %s",
                name, values, ex
            )
            raise RedisVeError(
                "[RedisApi::remove_set_members] "
                "Failed to Remove members from set key. "
                f"(name: {name}, values: {values})."
            ) from ex
        return result

    def get_set_members(self,
                        name: str,
                        client: Redis = None
                        ) -> list:
        """
        Add members to set key.

        """
        result = None
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::get_set_members] "
                    "Fatal Error : Failed to Get members from set key."
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            result = client.smembers(name=name)
        except (RedisError, TypeError) as ex:
            logger.debug(
                "[RedisApi::get_set_members] "
                "Failed to Get members from set key"
                "(name: %s) ex : %s",
                name, ex
            )
            raise RedisVeError(
                "[RedisApi::get_set_members] "
                "Failed to Get members from set key. "
                f"(name: {name})."
            ) from ex
        return result

    def add_time_series(self,
                        key,
                        timestamp,
                        value,
                        client: Redis = None,
                        **kwargs
                        ):
        """
        Get hmap data from redis server
        """
        result = False
        try:
            if not self.is_ready():
                raise RedisConnectionException(
                    "[RedisApi::add_time_series] "
                    "Fatal error: Failed to add time series to redis. "
                    "Redis connection is down, try to reconnect."
                )
            client = self.get_redis_client(client)
            self.cli.ts().add(key, timestamp, value, **kwargs)
            result = True
        except (RedisError, TypeError) as ex:
            logger.error(
                "[RedisApi::add_time_series] "
                "Failed to add time series to redis. "
                "(key: %s, timestamp: %s, value: %s) ex : %s",
                key, timestamp, value, ex
            )
            raise RedisVeError(
                "[RedisApi::add_time_series] "
                "Fatal error: Failed to add time series to redis. "
                f"(key: {key}, key: {timestamp}, value: {value})."
            ) from ex
        return result
