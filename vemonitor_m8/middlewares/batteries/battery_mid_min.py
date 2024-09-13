#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Battery Middlware Base Helper"""
from abc import ABC
import logging
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.middlwares import Middleware

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class BatteryMidBase(Middleware, ABC):
    """
    Battery Middlware Iterface class.
    """
    def __init__(self):
        Middleware.__init__(self)

    def set_node_name(self):
        """Set middleware node name."""
        self.node = 'm8_bat_monit'


class InputKeys:
    """
    Inputs Keys used in middlware
    """
    BAT_VOLTAGE = 'bat_voltage'
    BAT_CURRENT = 'bat_current'


class BatteryMidMin(Middleware):
    """
    Battery Middlware Minimalist Helper
    Used if battery data settings is unreachable.
    Only basic battery monitoring as:
        - bat_status: int: Battery Charge status
          -2, -1, 0, 1 => 'undefined', 'discharge', 'sleep', 'charge'
        - sys_v: float: Sytem voltage
        - 
    """
    def __init__(self):
        Middleware.__init__(self)

    # -2, -1, 0, 1 => 'undefined', 'discharge', 'sleep', 'charge'
    (UNDEFINED, DISCHARGE, WAIT, CHARGE) = range(-2, 2, 1)

    def set_node_name(self):
        """Set middleware node name."""
        self.node = 'm8_bat_monit'

    def run_callback(self,
                     time_key: int,
                     data: dict):
        """Get connector by key item and source."""
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_int(time_key, positive=True):
            self.init_cache_data(time_key)
            if BatteryMidMin.is_bat_voltage(data):
                self.inputs_cache.update({
                    InputKeys.BAT_VOLTAGE: data.get(InputKeys.BAT_VOLTAGE)
                })
                self.cache.update({
                    'sys_v_calc': BatteryMidMin.calc_sys_voltage(
                        bat_voltage=data.get(InputKeys.BAT_VOLTAGE)
                    )
                })
            if BatteryMidMin.is_bat_current(data):
                self.inputs_cache.update({
                    InputKeys.BAT_CURRENT: data.get(InputKeys.BAT_CURRENT)
                })
                self.cache.update({
                    'charge_stat': BatteryMidMin.get_battery_status(
                        bat_current=data.get(InputKeys.BAT_CURRENT)
                    )
                })
        return self.get_formated_cache()

    @staticmethod
    def get_mid_inputs_keys():
        """Get connector by key item and source."""
        return [
            InputKeys.BAT_VOLTAGE, InputKeys.BAT_CURRENT
        ]

    @staticmethod
    def get_mid_outputs_keys():
        """Get connector by key item and source."""
        return [
            'sys_v_calc', 'charge_stat'
        ]


    @staticmethod
    def get_battery_status(bat_current: float) -> int:
        """Get battery monitor object."""
        result = BatteryMidMin.UNDEFINED
        if Ut.is_numeric(bat_current, positive=True):
            result = BatteryMidMin.CHARGE
        elif Ut.is_numeric(bat_current, negative=True):
            result = BatteryMidMin.DISCHARGE
        elif Ut.is_numeric(bat_current) and bat_current == 0:
            result = BatteryMidMin.WAIT
        return result

    @staticmethod
    def calc_sys_voltage(bat_voltage: float) -> float:
        """Get battery monitor object."""
        result = 0
        if Ut.is_numeric(bat_voltage, positive=True):
            if 1.7 <= bat_voltage <= 2.55:
                result = 2
            elif 4 <= bat_voltage <= 8:
                result = 6
            elif 10 <= bat_voltage <= 17:
                result = 12
            elif 20 <= bat_voltage <= 34:
                result = 24
            elif 40 <= bat_voltage <= 68:
                result = 48
        return result

    @staticmethod
    def calc_sys_bat_voltage(bat_voltage: float,
                             sys_v: float
                             ) -> float:
        """Get battery monitor object."""
        result = 0
        if Ut.is_numeric(sys_v, positive=True):
            if sys_v == 2:
                result = bat_voltage
            elif 2 < sys_v <= 48:
                div = sys_v / 2
                if 0 < div <= 24:
                    result = round(bat_voltage / div, 3)
        return result

    @staticmethod
    def is_data(data: dict) -> int:
        """Get battery monitor object."""
        return Ut.is_dict(data, not_null=True)

    @staticmethod
    def is_bat_voltage(data: dict) -> int:
        """Get battery monitor object."""
        return BatteryMidMin.is_data(data)\
            and Ut.is_numeric(data.get(InputKeys.BAT_VOLTAGE))

    @staticmethod
    def is_bat_current(data: dict) -> int:
        """Get battery monitor object."""
        return BatteryMidMin.is_data(data)\
            and Ut.is_numeric(data.get(InputKeys.BAT_CURRENT))
