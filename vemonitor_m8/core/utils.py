# -*- coding: utf-8 -*-
"""vemonitor utils Helper"""
import re
from itertools import groupby
from typing import Union
from ve_utils.utype import UType as Ut


class Utils(Ut):
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

    @staticmethod
    def is_valid_port(value: int):
        """Compare if all iterable values are equal."""
        return Ut.is_int(value) and 0 < value <= 65535

    @staticmethod
    def is_valid_host(value: str):
        """Compare if all iterable values are equal."""
        regex = re.compile(
            "^((?:(?:[0-1]?[0-9]?[0-9])|(?:[0-2][0-4][0-9])|(?:25[0-5]))"
            "[.](?:(?:[0-1]?[0-9]?[0-9])|(?:[0-2][0-4][0-9])|(?:25[0-5]))"
            "[.](?:(?:[0-1]?[0-9]?[0-9])|(?:[0-2][0-4][0-9])|(?:25[0-5]))"
            "[.](?:(?:[0-1]?[0-9]?[0-9])|(?:[0-2][0-4][0-9])|(?:25[0-5])))$"
        )
        return Ut.is_str(value) and Ut.is_list(regex.findall(value), eq=1)
