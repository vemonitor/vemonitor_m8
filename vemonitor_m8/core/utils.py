# -*- coding: utf-8 -*-
"""vemonitor utils Helper"""
from itertools import groupby
from typing import Union
from ve_utils.utype import UType


class Utils(UType):
    """vemonitor utils Helper"""

    @staticmethod
    def get_min_in_loop(value: Union[int, float],
                        min_val: Union[int, float]):
        """Get the min value different from zero."""
        if value == 0:
            value = min_val
        elif 0 < min_val < value:
            value = min_val
        return value

    @staticmethod
    def get_max_in_loop(value: Union[int, float],
                        max_val: Union[int, float]):
        """Get the max value different from zero."""
        if value == 0:
            value = max_val
        elif value < max_val:
            value = max_val
        return value

    @staticmethod
    def all_equal(iterable):
        """Compare if all iterable values are equal."""
        grouped = groupby(iterable)
        return next(grouped, True) and not next(grouped, False)
