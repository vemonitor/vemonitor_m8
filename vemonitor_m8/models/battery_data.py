#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Battery model
"""
import logging
from typing import Optional, TypedDict, Union
from vemonitor_m8.core.utils import Utils as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"

logging.basicConfig()
logger = logging.getLogger("vemonitor")

class ChargeSettingsType(TypedDict):
    """Battery Bank Charge Settings Type"""
    charge_t_coef: float=0.0
    charge_absorption_u: float=0.0
    charge_float_u: float=0.0
    charge_egalization_u: float=0.0


class BatteryModelType(TypedDict):
    """Battery Bank Charge Settings Type"""
    name:Optional[str] = None
    manufacturer:Optional[str] = None
    model:Optional[str] = None
    battery_type:Optional[str] = None
    charge_settings: Optional[ChargeSettingsType] = None
    nb_cells: int = 0
    capacity: Optional[list] = None


class BatteryTypes:
    """Bettery types"""
    UNDEFINED="flooded"
    FLOODED="flooded"
    GEL="gel"
    AGM="agm"
    LI="li"
    LIFEPO4="LiFePo4"

class BatteryDataModel:
    """
    Battery Data model
    """
    def __init__(self, **kwargs: BatteryModelType):
        self.name = None
        self.model = None

        self.init_battery_bank(**kwargs)

    BATTERY_TYPE = BatteryTypes.UNDEFINED

    def has_name(self) -> bool:
        """Has Battery Name."""
        return Ut.is_key_pattern(self.name)

    def get_name(self) -> Optional[str]:
        """Get Battery Name."""
        result = None
        if self.has_name():
            result = self.name
        return result

    def set_name(self,
                 value: Optional[str] = None
                 ) -> bool:
        """Set Battery Name."""
        result = False
        if Ut.is_key_pattern(value):
            self.name = value
            result = True
        return result

    def has_model_data(self) -> bool:
        """Has Battery Model."""
        return Ut.is_dict(self.model, not_null=True)

    def has_manufacturer(self) -> bool:
        """Has Battery Model manufacturer."""
        return self.has_model_data()\
            and Ut.is_text_pattern(
                self.model.get('manufacturer')
            )

    def get_manufacturer(self) -> Optional[str]:
        """Get Battery Model manufacturer."""
        result = 0
        if self.has_manufacturer():
            result = self.model.get('manufacturer')
        return result

    def set_manufacturer(self,
                         value: Optional[str] = None
                         ) -> bool:
        """Set Battery Bank model."""
        result = False
        if Ut.is_text_pattern(value):
            self.model.update({
                'manufacturer': value
            })
            result = True
        return result

    def has_model_name(self) -> bool:
        """Has Battery Model model."""
        return self.has_model_data()\
            and Ut.is_text_pattern(
                self.model.get('model')
            )

    def get_model_name(self) -> Optional[str]:
        """Get Battery Model name."""
        result = None
        if self.has_model_name():
            result = self.model.get('model')
        return result

    def set_model_name(self, value: Optional[str] = None) -> bool:
        """Set Battery Bank model."""
        result = False
        if Ut.is_text_pattern(value):
            self.model.update({
                'model': value
            })
            result = True
        return result

    def set_model_data(self, data: Optional[dict] = None) -> bool:
        """Set Battery Bank model."""
        result = False
        if Ut.is_dict(data, not_null=True):
            self.model = {}
            is_set_man = self.set_manufacturer(data.get('manufacturer'))
            is_set_mod = self.set_model_name(data.get('model'))
            result = is_set_man and is_set_mod
        return result

    def init_battery_bank(self,
                          **kwargs: BatteryModelType
                          ) -> bool:
        """Init battery bank data"""
        result = False
        if Ut.is_dict(kwargs, not_null=True):
            is_set_name = self.set_name(kwargs.get('name'))
            is_set_model_data = self.set_model_data(
                Ut.get_items_from_dict(kwargs, ['manufacturer', 'model'])
            )
            result = is_set_name and is_set_model_data
        return result

    def is_valid(self) -> bool:
        """
        Checks to make sure that the parameters are valid.
        
        :param self: Used to Refer to the object that is calling the method.
        :return: A boolean value.
        
        :doc-author: Trelent
        """
        return self.has_name()

    def serialize(self):
        """
        Used to return a dictionary of the model's attributes.
        
        :return: A dictionary of the model attributes.
        """
        return {
            'name': self.name,
            'model': self.model
        }

    def __str__(self)->dict:
        """
        Called when the object is printed.
        :return: A dictionary of the attributes and values of the object.
        
        :doc-author: Trelent
        """
        return str(self.serialize())


class BatteryStructureModel(BatteryDataModel):
    """
    Battery Data Structure model
    """
    def __init__(self, **kwargs: BatteryModelType):
        BatteryDataModel.__init__(self, **kwargs)
        self.cell_voltage = 0
        self.bat_voltage = 0
        self.nb_cells = 0

        self.init_battery_bank(**kwargs)

    def has_battery_structure(self) -> bool:
        """
        Test if Battery has:
        cell_voltage, bat_voltage and nb_cells.
        """
        return self.has_nb_cells()\
            and self.has_cell_voltage()\
            and self.has_bat_voltage()

    def reset_battery_structure(self) -> bool:
        """
        Reset Battery Structure
        """
        self.cell_voltage = 0
        self.bat_voltage = 0
        self.nb_cells = 0

    def validate_bat_voltage(self) -> bool:
        """Get Battery Voltage."""
        result = False
        if self.has_battery_structure():
            bat_voltage = self.nb_cells * self.cell_voltage
            is_valid = self.bat_voltage == bat_voltage
            is_standard = self.bat_voltage in self.get_standard_voltages()
            if is_valid\
                    or is_standard:
                result = True

                if not is_valid\
                        and is_standard:
                    logger.warning(
                        "[BatteryModel::validate_bat_voltage] "
                        "Baterry Structure seems to be invalid. "
                        "Please control BatteryBank keys "
                        "['nb_cells', 'cell_voltage', 'bat_voltage']"
                    )
            else:
                logger.warning(
                        "[BatteryModel::validate_bat_voltage] "
                        "Baterry Structure seems to be invalid. "
                        "Please control values BatteryBank keys "
                        "['nb_cells', 'cell_voltage', 'bat_voltage']"
                    )
                self.reset_battery_structure()
        elif self.has_bat_voltage():
            result = True
        return result

    def validate_battery_structure(self) -> bool:
        """Get Battery Voltage."""
        result = False
        if self.validate_bat_voltage():
            result = True
        return result

    def calc_missing(self) -> bool:
        """Get Battery Voltage."""
        result = False
        if not self.has_battery_structure():
            if self.has_nb_cells()\
                    and self.has_cell_voltage():
                self.bat_voltage = self.nb_cells * self.cell_voltage
                result = True
            elif self.has_nb_cells()\
                    and self.has_bat_voltage():
                self.cell_voltage = self.bat_voltage / self.nb_cells
                result = True
            elif self.has_cell_voltage()\
                    and self.has_bat_voltage():
                nb_cells = Ut.get_int(
                    self.bat_voltage / self.cell_voltage
                )
                if nb_cells % 2 == 0:
                    self.nb_cells = nb_cells
                else:
                    self.nb_cells = nb_cells + 1
                result = True
        return result

    def has_bat_voltage(self) -> bool:
        """Get Battery Voltage."""
        return self.is_valid_bat_voltage(
            self.bat_voltage
        )

    def get_bat_voltage(self) -> Union[int, float]:
        """Get Battery Voltage."""
        result = 0
        if self.has_bat_voltage():
            result = self.bat_voltage
        return result

    def set_bat_voltage(self,
                        value: Optional[Union[int, float]] = None
                        ) -> bool:
        """Set Battery Voltage."""
        result = False
        if self.is_valid_bat_voltage(value):
            self.bat_voltage = value
            result = True
        return result

    def has_cell_voltage(self) -> bool:
        """Get Battery Voltage."""
        return self.is_valid_cell_voltage(
            self.cell_voltage
        )

    def get_cell_voltage(self) -> Union[int, float]:
        """Get Battery Voltage."""
        result = 0
        if self.has_cell_voltage():
            result = self.cell_voltage
        return result

    def set_cell_voltage(self,
                        value: Optional[Union[int, float]] = None
                        ) -> bool:
        """Set Battery Voltage."""
        result = False
        if self.is_valid_cell_voltage(value):
            self.cell_voltage = value
            result = True
        return result

    def has_nb_cells(self) -> bool:
        """Get Battery Voltage."""
        return Ut.is_numeric(self.nb_cells, positive=True)

    def get_nb_cells(self) -> int:
        """Get Battery Voltage."""
        result = 0
        if self.has_nb_cells():
            result = self.nb_cells
        return result

    def set_nb_cells(self, value: Optional[int] = None) -> bool:
        """Set Battery nb cells."""
        result = False
        if Ut.is_int(value, positive=True):
            self.nb_cells = value
            result = True
        return result

    def set_battery_structure(self,
                              **kwargs: BatteryModelType
                              ) -> bool:
        """Set battery Structure data"""
        result = False
        self.reset_battery_structure()
        if Ut.is_dict(kwargs, not_null=True):
            self.set_nb_cells(kwargs.get('nb_cells'))
            self.set_cell_voltage(kwargs.get('cell_voltage'))
            self.set_bat_voltage(kwargs.get('bat_voltage'))
            self.calc_missing()
            result = self.validate_battery_structure()
        return result

    def init_battery_bank(self,
                          **kwargs: BatteryModelType
                          ) -> bool:
        """Init battery bank data"""
        result = BatteryDataModel.init_battery_bank(
                self,
                **kwargs)
        is_set = self.set_battery_structure(**kwargs)
        return result is True\
            and is_set is True

    def serialize(self):
        """
        Used to return a dictionary of the model'sattributes.

        :return: A dictionary of the model attributes.
        """
        result = BatteryDataModel.serialize(self)
        result.update({
            'bat_voltage': self.bat_voltage,
            'cell_voltage': self.cell_voltage,
            'nb_cells': self.nb_cells
        })
        return result

    @staticmethod
    def get_standard_voltages():
        """Get list of standardized battery voltages"""
        return [2, 6, 12, 24, 36, 48]

    @staticmethod
    def is_valid_cell_voltage(value: Optional[Union[int, float]] = None
                              ) -> bool:
        """Test if value is valid battery voltage"""
        return Ut.is_numeric(value, positive=True)

    @staticmethod
    def is_valid_bat_voltage(value: Optional[Union[int, float]] = None
                              ) -> bool:
        """Test if value is valid battery voltage"""
        return Ut.is_numeric(value, positive=True)


class BatteryCapacityModel(BatteryStructureModel):
    """
    Battery Data Structure model
    """
    def __init__(self, **kwargs: BatteryModelType):
        BatteryStructureModel.__init__(self, **kwargs)
        self.capacity = None
        self.temp_capacity = None
        self.temp_cycle_life = None
        self.capacity_voltage = None
        self.init_battery_bank(**kwargs)

    def has_capacity(self) -> bool:
        """Get Battery Capacity properties."""
        return Ut.is_list(self.capacity, not_null=True)

    def get_capacity(self) -> Optional[list]:
        """Get Battery Capacity properties."""
        result = None
        if self.has_capacity():
            result = self.capacity
        return result

    def set_capacity(self, value: Optional[list] = None) -> bool:
        """Set Battery Capacity properties."""
        result = False
        if self.is_valid_capacity(value):
            self.capacity = value
            result = True
        return result

    def init_battery_bank(self,
                          **kwargs: BatteryModelType
                          ) -> bool:
        """Init battery bank data"""
        result = BatteryStructureModel.init_battery_bank(self, **kwargs)
        if Ut.is_dict(kwargs, not_null=True):
            is_set = self.set_capacity(kwargs.get('capacity'))
            result = result is True\
                and is_set
        return result

    def serialize(self):
        """
        Used to return a dictionary of the model'sattributes.

        :return: A dictionary of the model attributes.
        """
        result = BatteryStructureModel.serialize(self)
        result.update({
            'capacity': self.capacity
        })
        return result

    @staticmethod
    def is_valid_capacity(capacity: Optional[list]) -> bool:
        """
        Test if capacity of the battery is valid.
        
        :param self: Used to Refer to the object that is calling the function.
        :param capacity:listorNone: Used to Set the capacity of the battery.
        :return: None.
        
        :doc-author: Trelent
        """
        result = False
        if Ut.is_list(capacity, not_null=True):
            result = True
            for item in capacity:
                is_valid = Ut.is_list(item, eq=3)\
                    and BatteryCapacityModel.is_valid_capacity_item(
                        *item)
                if not is_valid:
                    result = False
                    break
        return result

    @staticmethod
    def get_capacity_diff_err(hr: float,
                              cap: float,
                              cur: float
                              ):
        """
        Returns the difference from theorical and calculated discharge capacity values
        of a battery at a given hour rate, capacity, and current.
        The function takes three parameters: hr (hour rate), cap (capacity), 
        and cur (current).
        If all three parameters are positive numbers,
        then the function returns a tuple containing the diff values.
        Otherwise it returns default value (None).
        
        :param hr:float: Used to Specify the hour of the cycle.
        :param cap:float: Used to Specify the capacity.
        :param cur:float: 
            Used to Specify the current used to calculate the capacity.
        :param default=None:
            Used to Set a default value for the parameter
            if it is not specified.
        :return: 
            The difference between the actual discharge capacity
            and the theoretical discharge capacity,
            which is calculated using the equation:.
        :doc-author: Trelent
        """
        result = None
        if Ut.is_numeric(hr, mini=0)\
                and Ut.is_numeric(cap, mini=0)\
                and Ut.is_numeric(cur, mini=0):
            dif_hr = round(hr - (cap / cur), 3)
            dif_cap = round(cap - (hr * cur), 3)
            dif_cur = round(cur - (cap / hr), 3)
            if dif_hr == dif_cap == dif_cur == 0:
                result = 0
            else:
                result = (dif_hr, dif_cap, dif_cur)
        return result

    @staticmethod
    def is_valid_capacity_item(hr: float,
                               cap: float,
                               cur: float
                               ):
        """
        Checks if the discharge capacity is within a certain range of the 
        discharge capacity at a given hour. The function returns True if it is, and False otherwise.
        
        :param self: Used to Access the class attributes.
        :param hr:float: Used to Specify the hour of the day.
        :param cap:float: Used to Specify the capacity of the battery.
        :param cur:float: Used to Specify the current capacity of the battery.
        :return: A boolean value.
        :doc-author: Trelent
        """
        result = False
        difs = BatteryCapacityModel.get_capacity_diff_err(hr, cap, cur)
        if difs == 0:
            result = True
        return result

    @staticmethod
    def get_discharge_capacity_column() -> list:
        """Get capacity columns titles"""
        return ['hour_rate', 'capacity', 'current']

    @staticmethod
    def get_temp_capacity_column() -> list:
        """Get temperature capacity columns titles"""
        return ['temperature', 'capacity']

    @staticmethod
    def get_temp_cycle_life_column() -> list:
        """Get temperature cycle columns titles"""
        return ['temperature', 'capacity']

    @staticmethod
    def get_capacity_voltage_column() -> list:
        """Get capacity voltage columns titles"""
        return ['hour_rate', 'capacity_voltage']

    @staticmethod
    def get_capacity_voltage_by_hour_rate_column() -> list:
        """Get capacity voltage by hour rate columns titles"""
        return ['percent_capacity', 'voltage']

class BatteryChargeSettings(BatteryCapacityModel):
    """
    Battery model
    """
    def __init__(self, **kwargs:BatteryModelType):
        self.charge_settings = {}
        BatteryCapacityModel.__init__(self, **kwargs)
        self.init_battery_bank(**kwargs)

    def has_charge_settings(self) -> bool:
        """Test if instance has battery object"""
        return Ut.is_dict(self.charge_settings, not_null=True)

    def is_charge_settings(self) -> bool:
        """Test if instance has battery object"""
        return Ut.is_dict(self.charge_settings)

    def init_charge_settings(self, reset: bool = False) -> bool:
        """Test if instance has battery object"""
        if not self.is_charge_settings()\
                or reset is True:
            self.charge_settings = {}

    def has_charge_t_coef(self) -> int:
        """Has Battery charge temperrature correction coeficient."""
        return self.is_charge_settings()\
            and self.is_charge_t_coef(
                self.charge_settings.get('charge_t_coef')
            )

    def get_charge_t_coef(self) -> int:
        """Get Battery charge temperrature correction coeficient."""
        result = 0
        if self.has_charge_t_coef():
            result = self.charge_settings.get('charge_t_coef')
        return result

    def set_charge_t_coef(self, value: float=0.0) -> float:
        """Set Battery charge temperrature correction coeficient.."""
        result = False
        if self.is_charge_settings()\
                and self.is_charge_t_coef(value):
            self.charge_settings.update({
                'charge_t_coef': value
            })
            result = True
        return result

    def has_charge_absorption_u(self) -> int:
        """Has Battery charge bulk voltage."""
        return self.is_charge_settings()\
            and self.is_charge_voltage(
                self.charge_settings.get('charge_absorption_u')
            )

    def get_charge_absorption_u(self) -> int:
        """Get Battery charge bulk voltage."""
        result = 0
        if self.has_charge_absorption_u():
            result = self.charge_settings.get('charge_absorption_u')
        return result

    def set_charge_absorption_u(self, value: float=0.0) -> float:
        """Set Battery charge bulk voltage."""
        result = False
        if self.is_charge_settings()\
                and Ut.is_numeric(value, positive=True):
            self.charge_settings.update({
                'charge_absorption_u': value
            })
            result = True
        return result

    def has_charge_float_u(self) -> int:
        """Has Battery charge float voltage."""
        return self.is_charge_settings()\
            and self.is_charge_voltage(
                self.charge_settings.get('charge_float_u')
            )

    def get_charge_float_u(self) -> int:
        """Get Battery charge float voltage."""
        result = 0
        if self.has_charge_float_u():
            result = self.charge_settings.get('charge_float_u')
        return result

    def set_charge_float_u(self, value: float=0.0) -> float:
        """Set Battery charge float voltage."""
        result = False
        if self.is_charge_settings()\
                and Ut.is_numeric(value, positive=True):
            self.charge_settings.update({
                'charge_float_u': value
            })
            result = True
        return result

    def has_charge_storage_u(self) -> int:
        """Has Battery charge float voltage."""
        return self.is_charge_settings()\
            and self.is_charge_voltage(
                self.charge_settings.get('charge_storage_u')
            )

    def get_charge_storage_u(self) -> int:
        """Get Battery charge float voltage."""
        result = 0
        if self.has_charge_storage_u():
            result = self.charge_settings.get('charge_storage_u')
        return result

    def set_charge_storage_u(self, value: float=0.0) -> float:
        """Set Battery charge float voltage."""
        result = False
        if self.is_charge_settings()\
                and Ut.is_numeric(value, positive=True):
            self.charge_settings.update({
                'charge_storage_u': value
            })
            result = True
        return result

    def has_charge_egalization_u(self) -> int:
        """Has Battery charge egalization voltage."""
        return self.is_charge_settings()\
            and self.is_charge_voltage(
                self.charge_settings.get('charge_egalization_u')
            )

    def get_charge_egalization_u(self) -> int:
        """Get Battery charge egalization voltage."""
        result = 0
        if self.has_charge_egalization_u():
            result = self.charge_settings.get('charge_egalization_u')
        return result

    def set_charge_egalization_u(self, value: float=0.0) -> float:
        """Set charge egalization voltage."""
        result = False
        if self.is_charge_settings()\
                and Ut.is_numeric(value, positive=True):
            self.charge_settings.update({
                'charge_egalization_u': value
            })
            result = True
        return result

    def set_charge_settings(self, data: dict) -> bool:
        """Set Battery Bank Name."""
        result = False
        self.init_charge_settings(reset=True)
        if Ut.is_dict(data, not_null=True):
            self.set_charge_t_coef(data.get('charge_t_coef'))
            self.set_charge_absorption_u(data.get('charge_absorption_u'))
            self.set_charge_float_u(data.get('charge_float_u'))
            self.set_charge_storage_u(data.get('charge_storage_u'))
            self.set_charge_egalization_u(data.get('charge_egalization_u'))
            result = True
        return result

    def set_defaults_charge_settings(self, data: dict) -> None:
        """
        Sets the default values.
        """
        self.init_charge_settings()

        if Ut.is_dict(data, not_null=True):
            if not self.has_charge_absorption_u()\
                and self.is_charge_voltage(data.get('charge_absorption_u')):
                self.set_charge_absorption_u(data.get('charge_absorption_u'))

            if not self.has_charge_float_u()\
                and self.is_charge_voltage(data.get('charge_float_u')):
                self.set_charge_float_u(data.get('charge_float_u'))

            if not self.has_charge_storage_u()\
                and self.is_charge_voltage(data.get('charge_storage_u')):
                self.set_charge_storage_u(data.get('charge_storage_u'))

            if not self.has_charge_egalization_u()\
                and self.is_charge_voltage(data.get('charge_egalization_u')):
                self.set_charge_egalization_u(data.get('charge_egalization_u'))

            if not self.has_charge_t_coef()\
                and self.is_charge_t_coef(data.get('charge_t_coef')):
                self.set_charge_t_coef(data.get('charge_t_coef'))

    def init_battery_bank(self,
                          **kwargs: BatteryModelType
                          ) -> bool:
        """Init battery bank data"""
        result = BatteryCapacityModel.init_battery_bank(self, **kwargs)
        if Ut.is_dict(kwargs, not_null=True):
            is_set = self.set_charge_settings(kwargs.get('charge_settings'))
            result = result is True\
                and is_set
        return result

    def serialize(self):
        """
        Used to return a dictionary of the model'sattributes.

        :return: A dictionary of the model attributes.
        """
        result = BatteryCapacityModel.serialize(self)
        result.update({
            'charge_settings': self.charge_settings
        })
        return result

    @staticmethod
    def is_charge_t_coef(value: float) -> bool:
        """Get Battery Capacity properties."""
        return Ut.is_numeric(
            value,
            not_null=True)

    @staticmethod
    def is_charge_voltage(value: float) -> bool:
        """Get Battery Capacity properties."""
        return Ut.is_numeric(
            value,
            positive=True)
