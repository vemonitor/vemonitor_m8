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


class EChargeStep(BaseFlag):
    """Standard voltages Enum"""
    ABSORPTION='absorption'
    FLOAT='float'
    STORAGE='storage'
    EQUALIZATION='equalization'

    @classmethod
    def is_member(cls, value) -> float:
        """Test if value is an member of ChargeCols enum."""
        return isinstance(value, EChargeStep)

    @classmethod
    def get_ordered_list(cls) -> list:
        """Get ordered charge settings list from lower to highter."""
        return [
            cls.STORAGE,
            cls.FLOAT,
            cls.ABSORPTION,
            cls.EQUALIZATION
        ]


class ChargeCols(BaseFlag):
    """External props names reference enum."""
    ABS_U='absorption_u'
    FLOAT_U='float_u'
    STORAGE_U='storage_u'
    EQ_U='equalization_u'
    T_COEF_U='coef_temp'

    @classmethod
    def is_member(cls, value) -> float:
        """Test if value is an member of ChargeCols enum."""
        return isinstance(value, ChargeCols)

    @classmethod
    def get_ordered_list(cls) -> list:
        """Get ordered charge settings list from lower to highter."""
        return [
            cls.STORAGE_U,
            cls.FLOAT_U,
            cls.ABS_U,
            cls.EQ_U
        ]


class BaseVolt(BaseFlag):
    """Standard voltages Enum"""
    U_2V=2
    U_4V=4
    U_6V=6
    U_12V=12
    U_24V=24
    U_48V=48

    @classmethod
    def is_member(cls, value) -> float:
        """Test if value is an instance of BaseVolt enum."""
        return isinstance(value, BaseVolt)

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


class ElecEnums:
    """Elec Enums Helper"""
    @staticmethod
    def get_related_charge_cols(member: EChargeStep) -> list:
        """Translate values from EChargeStep to ChargeCols Enums."""
        result = None
        if member == EChargeStep.ABSORPTION:
            result = ChargeCols.ABS_U
        elif member == EChargeStep.FLOAT:
            result = ChargeCols.FLOAT_U
        elif member == EChargeStep.STORAGE:
            result = ChargeCols.STORAGE_U
        elif member == EChargeStep.EQUALIZATION:
            result = ChargeCols.EQ_U
        return result

    @staticmethod
    def get_related_charge_step(member: ChargeCols) -> list:
        """Translate values from ChargeCols to EChargeStep Enums."""
        result = None
        if member == ChargeCols.ABS_U:
            result = EChargeStep.ABSORPTION
        elif member == ChargeCols.FLOAT_U:
            result = EChargeStep.FLOAT
        elif member == ChargeCols.STORAGE_U:
            result = EChargeStep.STORAGE
        elif member == ChargeCols.EQ_U:
            result = EChargeStep.EQUALIZATION
        return result
