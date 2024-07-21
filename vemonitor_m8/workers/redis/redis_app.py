#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Redis vemonitor Helper"""
import logging
from vemonitor_m8.workers.redis.redis_api import RedisApi

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class RedisApp:
    """Redis App Helper"""
    def __init__(self, credentials: dict):
        self.api = RedisApi(credentials)

    def is_ready(self) -> bool:
        """Test if cli is redis client instance and if redis ping return True"""
        return self.api.is_ready()

    def ping(self) -> bool:
        """Test if cli is redis client instance and if redis ping return True"""
        return self.api.is_ready() and self.api.is_connected()
