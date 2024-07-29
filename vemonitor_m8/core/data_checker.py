#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Data Checker Module
"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.exceptions import DeviceDataConfError
from vemonitor_m8.core.exceptions import DeviceInputValueError
from vemonitor_m8.core.exceptions import DeviceOutputValueError


class DataChecker:
    """
        Data Checker Module
    """
    @staticmethod
    def is_valid_checker(checker):
        """Test if is valid checker data"""
        return Ut.is_dict(checker)\
            and Ut.is_str(checker.get('input_type'), not_null=True)\
            and Ut.is_str(checker.get('output_type'), not_null=True)

    @staticmethod
    def validate_checker(key: str, checker: dict):
        """Format data item value"""
        if not DataChecker.is_valid_checker(checker):
            raise DeviceDataConfError(
                "Error: Unable to check/format data value. "
                "Checker configuration is bad or null. "
                f"Please Check Device data point: {key}"
            )
        return True

    @staticmethod
    def validate_input_value(key: str, value, checker: dict):
        """Format data item value"""
        is_not_input_type = value is not None\
            and (
                not Ut.is_str(value)
                and not Ut.is_valid_format(
                    value=value,
                    data_type=checker.get('input_type')
                )
            )

        if is_not_input_type is True:

            raise DeviceInputValueError(
                "Error: Device Input Value Error. "
                "Float point value or device data is not valid. "
                f"Please Check Device data point: {key}"
            )
        return True

    @staticmethod
    def validate_output_value(key: str, value, checker: dict):
        """Format data item value"""
        is_not_output_type = value is not None\
            and not Ut.is_valid_format(
                    value=value,
                    data_type=checker.get('output_type')
            )

        if is_not_output_type is True:

            raise DeviceOutputValueError(
                "Error: Device Input Value Error. "
                "Float point value or device data is not valid. "
                f"Please Check Device data point: {key}"
            )
        return True

    @staticmethod
    def format_item(key, value, checker):
        """Format data item value"""
        DataChecker.validate_checker(key, checker)

        val = Ut.format_by_type(value, checker.get('output_type'), 3)
        float_point = checker.get('floatpoint')

        if float_point is not None\
                and not Ut.is_float(float_point, positive=True):
            raise DeviceDataConfError(
                "Error: Unable to check/format data value. "
                "Float point value or device data is not valid. "
                f"Please Check Device data point: {key}"
            )
        if Ut.is_float(float_point) and float_point != 0:
            val = round(val * float_point, 3)
        return val

    @staticmethod
    def check_input_item(key, value, checker):
        """Check item value with checker conditions"""
        DataChecker.validate_input_value(key, value, checker)
        # format the input value
        val = DataChecker.format_item(key, value, checker)
        return val

    @staticmethod
    def check_output_item(key, value, checker):
        """Check item value with checker conditions"""
        DataChecker.validate_output_value(key, value, checker)
        return value

    @staticmethod
    def check_columns(columns: dict,
                      checkers: dict,
                      callback,
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
                        res[key] = callback(
                            key,
                            value,
                            local_checkers.get(key)
                        )
                    else:
                        res[key] = callback(key, value, checkers.get(key))
        return res

    @staticmethod
    def check_input_columns(columns: dict,
                            checkers: dict,
                            local_checkers: Optional[dict] = None
                            ) -> dict:
        """Check columns with checker conditions"""
        return DataChecker.check_columns(
            columns=columns,
            checkers=checkers,
            callback=DataChecker.check_input_item,
            local_checkers=local_checkers
        )

    @staticmethod
    def check_output_columns(columns: dict,
                             checkers: dict,
                             local_checkers: Optional[dict] = None
                             ) -> dict:
        """Check columns with checker conditions"""
        return DataChecker.check_columns(
            columns=columns,
            checkers=checkers,
            callback=DataChecker.check_output_item,
            local_checkers=local_checkers
        )
