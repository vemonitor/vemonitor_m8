# -*- coding: utf-8 -*-
"""DictOfObject model helper"""
from abc import ABC, abstractmethod
from typing import Optional
from ve_utils.utype import UType as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"


class DictOfObject(ABC):
    """DictOfObject model helper"""
    def __init__(self):
        self.items = None

    def has_items(self) -> bool:
        """Test if items defined."""
        return Ut.is_dict(self.items, not_null=True)

    def has_item_key(self, key: str) -> bool:
        """Test if instance has item key defined."""
        return self.has_items()\
            and self.is_valid_item_key(key)\
            and self.is_valid_item_value(self.items.get(key))

    def init_item(self, reset: bool = False):
        """Initialise item items."""
        if not self.has_items()\
                or reset is True:
            self.items = {}

    def add_item(self,
                 key: any,
                 value: any
                 ) -> bool:
        """Add item item."""
        result = False
        if self.is_valid_item_key(key)\
                and self.is_valid_item_value(value):
            self.init_item()
            self.items[key] = value
            result = True
        return result

    def get_item(self, key: any) -> Optional[object]:
        """Get item key."""
        result = None
        if self.has_item_key(key):
            result = self.items.get(key)
        return result

    def loop_on_items(self):
        """Get item key."""
        if self.has_items():
            for key, item in self.items.items():
                if self.is_valid_item_value(item):
                    yield key, item

    def get_items(self) -> Optional[dict]:
        """Get item key."""
        result = None
        if self.has_items():
            result = self.items
        return result

    @staticmethod
    @abstractmethod
    def is_valid_item_key(key: any):
        """Test if is valid item key"""

    @staticmethod
    @abstractmethod
    def is_valid_item_value(value: any):
        """Test if is valid item value"""
