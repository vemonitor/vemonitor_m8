#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Electricity Helper Methods
"""
import logging
from vemonitor_m8.core.utils import Utils as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"

logging.basicConfig()
logger = logging.getLogger("vemonitor")

class ElecHelper:
    """
    Electricity Helper Methods
    """
    @staticmethod
    def is_coef_temp(value: float) -> bool:
        """Get Battery Capacity properties."""
        return Ut.is_numeric(
            value,
            not_null=True,
            mini=-1000,
            maxi=1000)

    @staticmethod
    def get_coef_temp_format(value: float) -> bool:
        """Get Battery Capacity properties."""
        return round(value, 2)

    @staticmethod
    def get_coef_temp_value(value: float) -> bool:
        """Get Battery Capacity properties."""
        result = 0
        if ElecHelper.is_coef_temp(value):
            result = ElecHelper.get_coef_temp_format(value)
        return result

    @staticmethod
    def is_charge_voltage(value: float) -> bool:
        """Get Battery Capacity properties."""
        return Ut.is_numeric(
            value,
            positive=True,
            maxi=1000)

    @staticmethod
    def get_charge_voltage_format(value: float) -> bool:
        """Get Battery Capacity properties."""
        return round(value, 3)

    @staticmethod
    def get_charge_voltage_value(value: float) -> bool:
        """Get Battery Capacity properties."""
        result = 0
        if ElecHelper.is_charge_voltage(value):
            result = ElecHelper.get_charge_voltage_format(value)
        return result
