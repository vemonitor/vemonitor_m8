#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Battery Bank model
"""
import logging
from typing import Optional, TypedDict, Union
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.battery import BatteryModel
from vemonitor_m8.models.battery import BatteryFloodedModel
from vemonitor_m8.models.battery_data import ChargeSettingsType

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class BankStructureType(TypedDict):
    """Battery Bank Structure Type"""
    system_voltage: float=0.0
    in_series: int=1
    in_parallel: int=1

class BatteryBankType(TypedDict):
    """Battery Bank Charge Settings Type"""
    name: Optional[str] = None
    battery_key: Optional[str] = None
    battery: Optional[Union[BatteryModel, BatteryFloodedModel, dict]] = None
    bank_structure: BankStructureType = None
    charge_settings: BankStructureType = None

class BankBatteryHelper:
    """
    Battery Bank Battery model
    """
    def __init__(self,
                 **kwargs: BatteryBankType
                 )->None:
        self.battery: Optional[BatteryModel] = None
        if Ut.is_dict(kwargs, not_null=True):
            self.set_battery(kwargs.get('battery'))

    def has_battery(self) -> bool:
        """Test if instance has battery object"""
        return isinstance(self.battery, BatteryModel)

    def is_valid_battery(self) -> bool:
        """Test if instance has valid battery"""
        return self.has_battery()\
            and self.battery.is_valid()

    def set_battery(self,
                    battery: Optional[Union[BatteryModel, dict]]
                    ) -> bool:
        """Set battery model"""
        self.battery = None
        if isinstance(battery, BatteryFloodedModel):
            self.battery = battery
        elif isinstance(battery, BatteryModel):
            self.battery = battery
        elif self.is_battery_data(battery):
            battery_type = battery.get('battery')
            if battery_type == 'flooded':
                self.battery = BatteryFloodedModel(**battery)
            else:
                self.battery = BatteryModel(**battery)

        return self.is_valid_battery()

    def set_charge_settings(self, data: dict) -> bool:
        """Set Battery Bank Name."""
        result = False
        if self.has_battery():
            self.battery.set_charge_settings(data)
            result = True
        return result

    @staticmethod
    def is_battery_data(data: str) -> float:
        """Test if charge setting is set."""
        return Ut.is_dict(data, not_null=True)\
            and BatteryBank.is_battery_type(
                data.get('battery_type')
            )

class BatteryBankStructure(BankBatteryHelper):
    """
    Battery Bank Structure model
    """
    def __init__(self,
                 **kwargs: BatteryBankType
                 )->None:
        BankBatteryHelper.__init__(self, **kwargs)
        self.bank_structure: Optional[dict] = None
        if Ut.is_dict(kwargs, not_null=True):
            self.set_bank_structure(kwargs.get('bank_structure'))

    def has_bank_structure(self) -> bool:
        """Test if instance has battery object"""
        return Ut.is_dict(self.bank_structure, not_null=True)

    def init_bank_structure(self) -> bool:
        """Test if instance has battery object"""
        if not self.has_bank_structure():
            self.bank_structure = {
                'in_series': 1,
                'in_parallel': 1
            }

    def set_in_series(self, value: int=1) -> int:
        """Set how many batteries are in series."""
        result = False
        self.init_bank_structure()
        if Ut.is_int(value, positive=True):
            self.bank_structure.update({
                'in_series': Ut.get_int(value, default=0)
            })
            result = True
        return result

    def get_in_series(self) -> int:
        """Get how many batteries are in series."""
        result = 0
        if self.has_bank_structure():
            result = Ut.get_int(
                self.bank_structure.get('in_series'),
                default=0
            )
        return result

    def set_in_parallel(self, value: int=1) -> int:
        """Set how many batteries are in parallel."""
        result = False
        self.init_bank_structure()
        if Ut.is_int(value, positive=True):
            self.bank_structure.update({
                'in_parallel': Ut.get_int(value, default=0)
            })
            result = True
        return result

    def get_in_parallel(self) -> int:
        """Get how many batteries are in parallel."""
        result = 0
        if self.has_bank_structure():
            result = Ut.get_int(
                self.bank_structure.get('in_series'),
                default=0
            )
        return result

    def set_system_voltage(self, system_voltage: float=0.0) -> float:
        """Set the system voltage."""
        result = False
        self.init_bank_structure()
        in_series = self.get_in_series()
        if Ut.is_int(system_voltage, positive=True):
            self.bank_structure.update({
                'system_voltage': system_voltage
            })
            result = True
        elif isinstance(self.battery, BatteryModel)\
                and Ut.is_int(in_series, positive=True)\
                and self.battery.bat_voltage > 0:
            self.bank_structure.update({
                'system_voltage': self.battery.bat_voltage * in_series
            })
            result = True
        return result

    def get_system_voltage(self) -> int:
        """Get Battery Bank system voltage."""
        result = 0
        if self.has_bank_structure():
            result = Ut.get_int(
                self.bank_structure.get('system_voltage'),
                default=0
            )
        return result

    def set_bank_structure(self, data: dict) -> bool:
        """Set Bank structure settings"""
        result = False
        if Ut.is_dict(data, not_null=True):
            self.init_bank_structure()

            self.set_in_series(data.get('in_series'))
            self.set_in_parallel(data.get('in_parallel'))
            self.set_system_voltage(data.get('system_voltage'))
            result = True
        return result

    def serialize(self):
        """
        Used to return a dictionary of the model's
        attributes. This is needed because we are using JSON as our data transfer
        format, and it requires that the data being transferred be in a dictionary.
        
        :param self: Used to Access variables that belongs to the class.
        :return: A dictionary of the in_series attributes.
        
        :doc-author: Trelent
        """
        return {
            'battery': self.battery.serialize(),
            'bank_structure': {
                'system_voltage': self.get_system_voltage(),
                'in_parallel': self.get_in_parallel(),
                'in_series': self.get_in_series()
            }
        }


class BatteryBankSettings(BatteryBankStructure):
    """
    Battery Bank model
    """
    def __init__(self,
                 **kwargs: BatteryBankType
                 )->None:
        BatteryBankStructure.__init__(self, **kwargs)
        self.name: Optional[str] = None
        self.bank_env: Optional[dict] = None
        self.installation_date = 0
        self.real_capacity = 0
        self.bank_capacity = 0
        self.init_battery_bank(**kwargs)

    def init_battery_bank(self,
                          **kwargs: BatteryBankType
                          ) -> bool:
        """Init battery bank data"""
        result = False
        if Ut.is_dict(kwargs, not_null=True):
            self.set_name(kwargs.get('name'))
            self.set_charge_settings(kwargs.get('charge_settings'))
            result = True
        return result

    def set_name(self, value: str) -> bool:
        """Set Battery Bank Name."""
        result = False
        if Ut.is_str(value, not_null=True):
            self.name = value
            result = True
        return result

    def get_nb_cells(self) -> int:
        """Get nb cells per battery."""
        if isinstance(self.battery, BatteryModel):
            return self.battery.nb_cells * self.get_in_series()
        return 0

    def serialize(self):
        """
        Used to return a dictionary of the model's
        attributes. This is needed because we are using JSON as our data transfer
        format, and it requires that the data being transferred be in a dictionary.
        
        :param self: Used to Access variables that belongs to the class.
        :return: A dictionary of the in_series attributes.
        
        :doc-author: Trelent
        """
        return {
            'name': self.name,
            'battery': self.battery.serialize(),
            'bank_structure': {
                'system_voltage': self.get_system_voltage(),
                'in_parallel': self.get_in_parallel(),
                'in_series': self.get_in_series()
            }
        }

    def __str__(self)->dict:
        """
        Called when the object is printed. 
        It returns a string representation of the object, which can be anything you want it to be. 
        In this case, we are returning a dictionary
        that contains all of the information about our class.
        :return: A dictionary of the attributes and values of the object.
        
        :doc-author: Trelent
        """
        return str(self.serialize())


class BatteryBank:
    """
    Battery Bank model
    """
    def __init__(self,
                 **kwargs: BatteryBankType
                 )->None:
        self.bank: BatteryBankSettings = BatteryBankSettings(**kwargs)

    def is_valid(self) -> bool:
        """
        Checks to make sure that the parameters are valid.
        """
        return isinstance(self.bank, BatteryBankSettings)

    def serialize(self):
        """
        Used to return a dictionary of the model's
        attributes. This is needed because we are using JSON as our data transfer
        format, and it requires that the data being transferred be in a dictionary.
        
        :param self: Used to Access variables that belongs to the class.
        :return: A dictionary of the in_series attributes.
        
        :doc-author: Trelent
        """
        return {
            'battery_bank': str(self.bank.serialize())
        }

    def __str__(self)->dict:
        """
        Called when the object is printed. 
        It returns a string representation of the object, which can be anything you want it to be. 
        In this case, we are returning a dictionary
        that contains all of the information about our class.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: A dictionary of the attributes and values of the object.
        
        :doc-author: Trelent
        """
        return str(self.serialize())

    def __eq__(self, other):
        """
        Used to determine whether two objects are equal.
        It is called by the == operator. It should return a Boolean value.
        
        :param self: Used to Refer to the instance of the class.
        :param other: Used to Compare the object with another object.
        :return: A boolean value.
        
        :doc-author: Trelent
        """
        return self.__dict__ == other.__dict__

    @staticmethod
    def get_battery_types() -> float:
        """Test if charge setting is set."""
        return ["flooded", "gel", "agm", "li"]

    @staticmethod
    def get_bank_structure_item(key: str, data: dict) -> float:
        """Test if charge setting is set."""
        result = None
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_str(key, not_null=True)\
                and key in data:
            result = data.get(key)
        return result

    @staticmethod
    def is_battery_type(value: str) -> float:
        """Test if charge setting is set."""
        return Ut.is_str(value, not_null=True)\
            and value in ["flooded", "gel", "agm", "li"]

    @staticmethod
    def is_charge_settings(data: ChargeSettingsType) -> float:
        """Test if charge setting is set."""
        return Ut.is_dict(data, not_null=True)\
            and (Ut.is_numeric(data.get('charge_float_u'), positive=True)\
                or Ut.is_numeric(data.get('charge_absorption_u'), positive=True)\
                or Ut.is_numeric(data.get('charge_float_u'), positive=True)\
                or Ut.is_numeric(data.get('storage_v'), positive=True)\
                or Ut.is_numeric(data.get('charge_equalization_u'), positive=True)
            )
