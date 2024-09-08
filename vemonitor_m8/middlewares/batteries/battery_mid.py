#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Battery Middlware Base Helper"""
import logging
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.battery_bank import BatteryBank
from vemonitor_m8.middlewares.batteries.battery_mid_min import BatteryMidMin
from vemonitor_m8.models.middlwares import Middleware

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class BatteryMid(BatteryMidMin):
    """
    Default Battery Middlware Helper
    Used if battery data settings contain only base settings.
    Only basic battery monitoring as:
        - bat_status: int: Battery Charge status
          -1, 0, 1 => 'discharge', 'sleep', 'charge'
        - sys_v: float: Sytem voltage
        - 
    """
    def __init__(self,
                 battery_bank: dict
                 ):
        BatteryMidMin.__init__(self)
        self. battery_bank = None
        self.set_battery_bank(battery_bank)

    (BULK, ABSORBTION, FLOAT, EGALISATION, TRANSITION) = range(10, 60, 10)

    def set_node_name(self):
        """Set middleware node name."""
        self.node = 'm8_bat_monit'

    def set_battery_bank(self,
                         battery_bank: dict
                         ):
        """Set BatteryBank object."""
        self.battery_bank = None
        if Ut.is_dict(battery_bank, not_null=True):
            settings = {
                'name': battery_bank.get('name'),
                'battery_key': battery_bank.get('battery_key'),
                'battery': battery_bank.get('battery'),
                'bank_structure': {
                    'system_voltage': battery_bank.get('system_voltage'),
                    'in_series': battery_bank.get('in_series'),
                    'in_parallel': battery_bank.get('in_parallel')
                },
                'charge_settings': {
                    'charge_t_coef': battery_bank.get('charge_t_coef'),
                    'charge_absorption_u': battery_bank.get('charge_absorption_u'),
                    'charge_float_u': battery_bank.get('charge_float_u'),
                    'charge_egalization_u': battery_bank.get('charge_egalization_u')
                }
            }
            self. battery_bank = BatteryBank(**settings)

    def run_callback(self,
                     time_key: int,
                     data: dict):
        """Get connector by key item and source."""
        BatteryMidMin.run_callback(
            self=self,
            time_key=time_key,
            data=data
        )
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_int(time_key, positive=True):
            self.init_cache_data(time_key)
            if BatteryMidMin.is_bat_voltage(data):
                self.inputs_cache.update({
                    'bat_voltage': data.get('bat_voltage')
                })
                self.cache.update({
                    'sys_v_calc': BatteryMidMin.calc_sys_voltage(
                        bat_voltage=data.get('bat_voltage')
                    )
                })
            if BatteryMidMin.is_bat_current(data):
                self.inputs_cache.update({
                    'bat_current': data.get('bat_current')
                })
                self.cache.update({
                    'charge_stat': BatteryMidMin.get_battery_status(
                        bat_current=data.get('bat_current')
                    )
                })
        return self.get_formated_cache()

    @staticmethod
    def get_mid_inputs_keys():
        """Get connector by key item and source."""
        return [
            'bat_voltage', 'bat_current', 't_bat', 't_loc'
        ]

    @staticmethod
    def get_mid_outputs_keys():
        """Get connector by key item and source."""
        return [
            'sys_v_calc', 'charge_stat', 't_bat', 't_loc'
        ]

    @staticmethod
    def calc_charge_step(bat_voltage: float,
                         bat_stat: int,
                         cell_v: float
                         ) -> float:
        """Get battery monitor object."""
        result = 0
        if Ut.is_numeric(bat_voltage, positive=True)\
            and Ut.is_numeric(cell_v, positive=True)\
            and bat_stat == BatteryMid.CHARGE:
            if 2.31 <= cell_v <= 2.9:
                result = BatteryMid.FLOAT
            elif 2.44 <= cell_v <= 2.62:
                result = BatteryMid.ABSORBTION
            elif 2.3 <= cell_v <= 2.8:
                result = BatteryMid.ABSORBTION
            elif 2.166 <= cell_v <= 2.8:
                result = BatteryMid.BULK
        else:
            result = BatteryMid.TRANSITION
        return result
