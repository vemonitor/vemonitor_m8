#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Middlewares models helper.
"""
import time
from abc import ABC, abstractmethod
from typing import Optional, Union
from ve_utils.utype import UType as Ut

from vemonitor_m8.models.item_dict import DictOfObject

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"


class Middleware(ABC):
    """Middleware model helper"""
    def __init__(self):
        self.node = None
        self.inputs_cache = {}
        self.cache = {}
        self.time_key = 0
        self.set_node_name()

    def get_formated_cache(self):
        """Get formatted cache data."""
        result = None
        if Ut.is_str(self.node, not_null=True)\
            and Ut.is_dict(self.cache, not_null=True):
            result = {
                self.node: self.cache
            }
        return result

    def init_cache_data(self, time_key: int):
        """Init Cache data."""
        result = False
        if Ut.is_int(time_key, positive=True):
            if (Ut.is_int(self.time_key, positive=True)\
                        and self.time_key < time_key) \
                    or not Ut.is_int(self.time_key, positive=True):
                self.time_key = time_key
                self.inputs_cache = {}
                self.cache = {}
            result = True
        return result

    @abstractmethod
    def set_node_name(self):
        """Set middleware node name."""
        self.node = 'mid_node'

    @abstractmethod
    def run_callback(self,
                     time_key: int,
                     data: dict):
        """Get connector by key item and source."""
        return data

    @staticmethod
    @abstractmethod
    def get_mid_inputs_keys():
        """Get connector by key item and source."""

    @staticmethod
    @abstractmethod
    def get_mid_outputs_keys():
        """Get connector by key item and source."""

class Middlewares(DictOfObject):
    """Middlewares model helper"""
    def __init__(self):
        DictOfObject.__init__(self)

    def has_middlewares(self) -> bool:
        """Test if middlewares items defined."""
        return self.has_items()

    def has_middleware_key(self, key: str) -> bool:
        """Test if instance has middleware key defined."""
        return self.has_item_key(key=key)

    def init_middleware(self, reset: bool = False):
        """Initialise middleware items."""
        self.init_item(reset=reset)

    def add_middleware(self,
                   key: str,
                   middleware: Middleware
                   ) -> bool:
        """Add worker item."""
        return self.add_item(
            key=key,
            value=middleware
        )

    def get_middleware(self, key: str) -> Optional[Middleware]:
        """Get middleware key."""
        return self.get_item(key=key)

    def get_middleware_node(self, key: str) -> Optional[str]:
        """Get middleware key."""
        result = None
        if self.has_middleware_key(key=key):
            middleware = self.get_item(key=key)
            result = middleware.node
        return result

    def loop_on_middlewares(self):
        """Loop on middlewares items."""
        if self.has_middlewares():
            for key, middleware in self.items.items():
                if Middlewares.is_middleware(middleware):
                    yield key, middleware

    def get_middlewares(self) -> Optional[dict]:
        """Get middlewares key."""
        return self.get_items()

    def get_nodes_list(self) -> Optional[list]:
        """Get middlewares nodes list."""
        result = []
        for key, middleware in self.loop_on_middlewares():
            result.append(middleware.node)
        return result

    def read_worker_data_callbacks(self,
                                   time_key: int,
                                   data: dict
                                   ):
        """Get connector by key item and source."""
        result = {}
        for key, middleware in self.loop_on_middlewares():
            result.update(middleware.run_callback(
                time_key=time_key,
                data=data
            ))
        return result

    @staticmethod
    def is_middleware(middleware: Middleware):
        """Test if is a middleware instance."""
        return isinstance(middleware, Middleware)

    @staticmethod
    def is_valid_item_key(key: tuple):
        """Test if is valid item type"""
        return Ut.is_str(key)

    @staticmethod
    def is_valid_item_value(value: tuple):
        """Test if is valid item type"""
        return Middlewares.is_middleware(value)
