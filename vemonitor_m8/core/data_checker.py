#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
PvMonitor CalcStats module. Calculate stats from numeric values
"""
from typing import Optional
from ve_utils.utype import UType as Ut


class DataChecker:
    """
        PvMonitor CalcStats module. Calculate stats from numeric values
    """
    @classmethod
    def is_valid_checker(cls, checker):
        """Test if is valid checker data"""
        return Ut.is_dict(checker)\
            and Ut.is_str(checker.get('input_type'))\
            and Ut.is_str(checker.get('output_type'))

    @classmethod
    def check_item(cls, key, value, checker):
        """Check item value with checker conditions"""
        if cls.is_valid_checker(checker):
            val = Ut.format_by_type(value, checker.get('output_type'), 3)
            float_point = checker.get('floatpoint')
            if Ut.is_float(float_point) and float_point != 0:
                val = round(val * float_point, 3)
            return val
        return None

    @classmethod
    def check_columns(cls,
                      columns: dict,
                      checkers: dict,
                      local_checkers: Optional[dict] = None
                      ) -> dict:
        """Check columns with checker conditions"""
        res = None
        if Ut.is_dict(columns, not_null=True)\
                and Ut.is_dict(checkers, not_null=True):
            res = {}
            for key, value in columns.items():
                if Ut.is_str(key):
                    if Ut.is_dict(local_checkers) and key in local_checkers:
                        res[key] = cls.check_item(key, value, local_checkers.get(key))
                    else:
                        res[key] = cls.check_item(key, value, checkers.get(key))
        return res
