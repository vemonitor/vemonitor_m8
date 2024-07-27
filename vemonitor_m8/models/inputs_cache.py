"""Inputs data cache Model"""
from abc import ABC, abstractmethod
from typing import Optional, Union
from ve_utils.utype import UType as Ut


class InputsCache(ABC):
    """Inputs data cache Model"""

    def __init__(self,
                 max_rows: int = 10
                 ):
        self._max_rows = 10
        self._interval_min = 0
        self.set_max_rows(max_rows)

    def has_interval_min(self):
        """Test if instance has interval_min"""
        return Ut.is_int(self._interval_min, positive=True)

    def get_interval_min(self):
        """Get interval_min property"""
        return self._interval_min

    def set_interval_min(self, value: Union[int, float]) -> bool:
        """Set interval_min property."""
        result = False
        if Ut.is_numeric(value, positive=True):
            self._interval_min = value
            result = True
        return result

    def set_max_rows(self, value: int) -> bool:
        """Set interval_min property."""
        result = False
        if Ut.is_int(value, positive=True):
            self._max_rows = value
            result = True
        return result

    @staticmethod
    def is_from_time(item_time: int, from_time: int = 0):
        """Test if item must be returned."""
        return from_time == 0 \
            or (0 < from_time <= item_time)

    @abstractmethod
    def has_data(self):
        """Test if instance has data cache."""
        return True

    @abstractmethod
    def add_data_cache(self,
                       time_key: int,
                       key: str,
                       data: dict
                       ):
        """Add inputs data cache."""

    @abstractmethod
    def register_node(self, node: str):
        """Register node in cache."""

    @abstractmethod
    def get_data_from_cache(self,
                            from_time: int = 0,
                            nb_items: int = 0,
                            structure: Optional[dict] = None
                            ) -> tuple:
        """
        Get data from cache.
        """
