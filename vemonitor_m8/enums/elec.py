#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Battery model
"""
from typing import Union
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.elec_helper import ElecHelper
from vemonitor_m8.enums.core import BaseEnum, BaseFlag


class BatteryTypes(BaseEnum):
    """Standard bettery types Enum"""
    FLOODED="flooded"
    GEL="gel"
    AGM="agm"
    LI="li"
    LIFEPO4="LiFePo4"


class BaseVolt(BaseFlag):
    """Standard voltages Enum"""
    U_2V=2
    U_4V=4
    U_6V=6
    U_12V=12
    U_24V=24
    U_48V=48

    @classmethod
    def get_default(cls) -> Union[int, float]:
        """Get default Standard voltage"""
        return cls.U_2V

    @classmethod
    def get_default_value(cls) -> Union[int, float]:
        """Get default Standard voltage"""
        return cls.U_2V.value

    @staticmethod
    def get_base_voltage_values() -> bool:
        """Get list of Battery Base voltages values."""
        return [
            (member, member.value)
            for name, member in BaseVolt.__members__.items()
            if ElecHelper.is_charge_voltage(member.value)
        ]

    @staticmethod
    def get_base_voltage_by_value(value: Union[int, float]) -> list:
        """Get list of Battery Base voltages values."""
        result = 0
        base_u_list = BaseVolt.get_base_voltage_values()
        if Ut.is_numeric(value, positive=True):
            for member, base_u in base_u_list:
                if value == base_u:
                    result = member
                    break
        return result

    @staticmethod
    def get_base_voltage_by_u_value(charge_voltage: float
                                    ) -> Union[int, BaseFlag]:
        """
        Get Battery Base voltage from charge voltage value.
        - 2v: 2v < charge_voltage <= 2.8v
        - 4v: 4v < charge_voltage <= 5.6v
        - 6v: 6v < charge_voltage <= 8.4v
        - 12v: 12v < charge_voltage <= 16.8v
        - 24v: 24v < charge_voltage <= 33.6v
        - 48v: 48v < charge_voltage <= 67.2v
        """
        result = 0
        base_u_list = BaseVolt.get_base_voltage_values()

        if ElecHelper.is_charge_voltage(charge_voltage)\
            and Ut.is_list(base_u_list, not_null=True):

            for member, base_u in base_u_list:
                diff_percent = charge_voltage * 100 / base_u
                if charge_voltage > base_u\
                        and diff_percent <= 140:
                    result = member

        return result
