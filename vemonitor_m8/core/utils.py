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
    def is_key_pattern(data: str) -> bool:
        """Test if is valid key pattern."""
        return Utils.is_str(data)\
            and Utils.is_list(
                re.compile(
                    r"(?=\w{1,30}$)^([a-zA-Z\d]+(?:_[a-zA-Z\d]+)*)$"
                    ).findall(data),
                not_null=True
            )

    @staticmethod
    def is_attr_pattern(data: str) -> bool:
        """Test if is valid key pattern."""
        return Utils.is_str(data)\
            and Utils.is_list(
                re.compile(
                    r"(?=[a-zA-Z\d_-]{1,30}$)^([a-zA-Z\d]+(?:(?:_|-)[a-zA-Z\d]+)*)$"
                    ).findall(data),
                not_null=True
            )

    @staticmethod
    def is_text_pattern(data: str) -> bool:
        """Test if is valid key pattern."""
        return Utils.is_str(data)\
            and Utils.is_list(
                re.compile(
                    r"^([a-zA-Z\d_ ()-]{1,30})$"
                    ).findall(data),
                not_null=True
            )

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

    @staticmethod
    def is_from_time(item_time: int, from_time: int = 0):
        """Test if 0 < from_time <= item_time or from_time == 0."""
        is_valid_props = Ut.is_numeric(item_time, mini=0)\
            and Ut.is_numeric(from_time, mini=0)
        is_from_time_null = is_valid_props\
            and from_time == 0
        is_valid = is_valid_props\
            and 0 < from_time <= item_time
        return is_from_time_null \
            or is_valid

    @staticmethod
    def rename_keys_from_dict(data: dict,
                              ref_keys: list):
        """Rename keys from dict"""
        result = dict(data)
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_list(ref_keys, not_null=True):
            for keys in ref_keys:
                if Ut.is_list(keys, eq=2):
                    new, current = keys
                    if Ut.is_str(new, not_null=True)\
                            and Ut.is_str(current, not_null=True)\
                            and current in data:
                        result[new] = result.pop(current)
        return result

    @staticmethod
    def rename_keys_from_sub_dict(data: dict,
                                  ref_keys: list):
        """Rename keys from sub dict of dict"""
        result = dict(data)
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_list(ref_keys, not_null=True):
            for node, node_data in data.items():
                new_cols = Utils.rename_keys_from_dict(
                    data=node_data,
                    ref_keys=ref_keys
                )
                if Ut.is_dict(new_cols, not_null=True):
                    result[node] = new_cols
        return result

    @staticmethod
    def rename_keys_from_sub_sub_dict(data: dict,
                                       ref_keys: list):
        """Rename keys from sub sub dict of dict"""
        result = dict(data)
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_list(ref_keys, not_null=True):
            for time_key, cols_data in data.items():
                new_items = Utils.rename_keys_from_sub_dict(
                    data=cols_data,
                    ref_keys=ref_keys
                )
                if Ut.is_dict(new_items, not_null=True):
                    result[time_key] = new_items
        return result

    @staticmethod
    def rename_keys_from_list(data: list,
                              ref_keys: list
                              ) -> list:
        """Rename keys from dict"""
        result = list(data)
        if Ut.is_list(data, not_null=True)\
                and Ut.is_list(ref_keys, not_null=True):
            for keys in ref_keys:
                 if Ut.is_list(data, not_null=True):
                    for i, col in enumerate(data):
                        if Ut.is_list(keys, eq=2):
                            new, current = keys
                            if Ut.is_str(new, not_null=True)\
                                    and Ut.is_str(current, not_null=True):
                                if current == col:
                                    result[i] = new
        return result

    @staticmethod
    def rename_keys_from_dict_of_lists(data: dict,
                                       ref_keys: list):
        """Rename keys from dict"""
        result = dict(data)
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_list(ref_keys, not_null=True):
            for node, columns in data.items():
                new_cols = Utils.rename_keys_from_list(
                     data=columns,
                     ref_keys=ref_keys
                )
                if Ut.is_list(new_cols, not_null=True):
                    result[node] = new_cols
        return result
