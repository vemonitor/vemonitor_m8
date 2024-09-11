#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Battery model
"""
import logging
from vemonitor_m8.models.battery_data import BatteryChargeSettings
from vemonitor_m8.models.battery_data import BatteryModelType
from vemonitor_m8.models.battery_data import BatteryTypes
__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class BatteryModel(BatteryChargeSettings):
    """
    Battery model
    """
    def __init__(self,
                 **kwargs: BatteryModelType
                 ):
        BatteryChargeSettings.__init__(self, **kwargs)
        # self.voltage_temperature_correction = Ut.get_float(voltage_temperature_correction)
        # self.bat_voltage = Ut.get_float(bat_voltage)
        # self.charge_current = Ut.get_float(charge_current)
        self.set_defaults()

    def set_defaults(self) -> None:
        """
        Sets the default values.
        """


class BatteryFloodedModel(BatteryModel):
    """
    Battery Flooded model
    """
    def __init__(self,
                 **kwargs: BatteryModelType
                 ):
        BatteryModel.__init__(self, **kwargs)
        self.set_defaults()

    BATTERY_TYPE = BatteryTypes.FLOODED

    def set_defaults(self) -> None:
        """
        Sets the default values.
        """
        charge_settings = {
            'charge_absorption_u': 14.1,
            'charge_float_u': 13.8,
            'charge_storage_u': 13.2,
            'charge_equalization_u': 15.9,
            'charge_t_coef': -16.2
        }
        self.set_defaults_charge_settings(
            data=charge_settings
        )

class BatteryGelModel(BatteryModel):
    """
    Battery Gel model
    """
    def __init__(self,
                 **kwargs: BatteryModelType
                 ):
        BatteryModel.__init__(self, **kwargs)
        self.set_defaults()

    BATTERY_TYPE = BatteryTypes.GEL

    def set_defaults(self) -> None:
        """
        Sets the default values.
        """
        charge_settings = {
            'charge_absorption_u': 14.1,
            'charge_float_u': 13.8,
            'charge_storage_u': 13.2,
            'charge_egalization_u': 15.9,
            'charge_t_coef': -16.2
        }
        self.set_defaults_charge_settings(
            data=charge_settings
        )


class BatteryAGMModel(BatteryModel):
    """
    Battery AGM model
    """
    def __init__(self,
                 **kwargs: BatteryModelType
                 ):
        BatteryModel.__init__(self, **kwargs)
        self.set_defaults()

    BATTERY_TYPE = BatteryTypes.AGM

    def set_defaults(self) -> None:
        """
        Sets the default values.
        """
        charge_settings = {
            'charge_absorption_u': 14.7,
            'charge_float_u': 13.8,
            'charge_storage_u': 13.2,
            'charge_egalization_u': 15.9,
            'charge_t_coef': -16.2
        }
        self.set_defaults_charge_settings(
            data=charge_settings
        )


class BatteryLi(BatteryModel):
    """
    Battery LiFePo4 model
    """
    def __init__(self,
                 **kwargs: BatteryModelType
                 ):
        BatteryModel.__init__(self, **kwargs)
        self.set_defaults()

    BATTERY_TYPE = BatteryTypes.LI

    def set_defaults(self) -> None:
        """
        Sets the default values.
        """
        charge_settings = {
            'charge_absorption_u': 14.2,
            'charge_float_u': 0,
            'charge_storage_u': 13.5,
            'charge_egalization_u': 0,
            'charge_t_coef': 0
        }
        self.set_defaults_charge_settings(
            data=charge_settings
        )


class BatteryLiFePo4Model(BatteryModel):
    """
    Battery LiFePo4 model
    """
    def __init__(self,
                 **kwargs: BatteryModelType
                 ):
        BatteryModel.__init__(self, **kwargs)
        self.set_defaults()

    BATTERY_TYPE = BatteryTypes.LIFEPO4

    def set_defaults(self) -> None:
        """
        Sets the default values.
        """
        charge_settings = {
            'charge_absorption_u': 14.2,
            'charge_float_u': 0,
            'charge_storage_u': 13.5,
            'charge_egalization_u': 0,
            'charge_t_coef': 0
        }
        self.set_defaults_charge_settings(
            data=charge_settings
        )
