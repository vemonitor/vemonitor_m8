#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Battery model
"""
import logging
from typing import Optional, TypedDict, Union
from vemonitor_m8.core.elec_helper import ElecHelper
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.enums.elec import BaseVolt, ElecEnums
from vemonitor_m8.enums.elec import EChargeStep
from vemonitor_m8.enums.elec import ChargeCols
from vemonitor_m8.enums.core import BaseFlag
from vemonitor_m8.models.item_dict import DictOfObject

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class ChargeSettingsProps(TypedDict):
    """Battery Bank Charge Settings Type"""
    charge_t_coef: float=0.0
    charge_absorption_u: float=0.0
    charge_float_u: float=0.0
    charge_equalization_u: float=0.0


class RefCols(BaseFlag):
    """External props names reference enum."""
    ABS_U='charge_absorption_u'
    FLOAT_U='charge_float_u'
    STORAGE_U='charge_storage_u'
    EQ_U='charge_equalization_u'
    T_COEF_U='charge_t_coef'


class ChargeStepData:
    """
    Battery Charge step controller
    """
    def __init__(self,
                 charge_step: Optional[EChargeStep] = None,
                 index_step: int = None,
                 diff_value: Union[int, float] = None,
                 diff_percent: Union[int, float] = None
                 ):
        self.charge_step: Optional[EChargeStep] = charge_step
        self.index_step: int = index_step
        self.diff_value: Union[int, float] = diff_value
        self.diff_percent: Union[int, float] = diff_percent

    def serialize(self) -> dict:
        """Init Temperrature correction values"""
        charge_step = None
        if EChargeStep.is_member(self.charge_step):
            charge_step = self.charge_step.value
        return {
            'charge_step': charge_step,
            'index_step': self.index_step,
            'diff_value': self.diff_value,
            'diff_percent': self.diff_percent
        }


class ChargeData:
    """
    Battery Charge controller
    """
    def __init__(self):
        self.bat_voltage: Union[int, float] = None
        self.t_bat: Union[int, float] = None
        self.compensed_charge: Optional[dict] = None
        self.base_u: Optional[BaseVolt] = None
        self.is_temp_correction: bool = False
        self.temp_correction: Union[int, float] = None
        self.current_step: Optional[ChargeStepData] = ChargeStepData()
        self.lower_step: Optional[ChargeStepData] = ChargeStepData()

    @staticmethod
    def is_index_step(index_step: int) -> bool:
        """Init Temperrature correction values"""
        return index_step >= 0\
            and index_step -1 >= 0

    def serialize(self) -> dict:
        """Init Temperrature correction values"""
        base_u = None
        if BaseVolt.is_member(self.base_u):
            base_u = self.base_u.value
        return {
            'bat_voltage': self.bat_voltage,
            't_bat': self.t_bat,
            'base_u': base_u,
            'compensed_charge': self.compensed_charge,
            'is_temp_correction': self.is_temp_correction,
            'temp_correction': self.temp_correction,
            'current_step': self.current_step.serialize(),
            'lower_step': self.lower_step.serialize(),
        }


class ChargeSettingsModel(DictOfObject):
    """
    Battery Charge model
    """
    def __init__(self, **kwargs:ChargeSettingsProps):
        DictOfObject.__init__(self)
        self.init(**kwargs)

    def is_charge_settings(self) -> bool:
        """Test if instance has battery object"""
        return self.has_charge_setting(ChargeCols.ABS_U.value)

    def has_charge_setting(self, key: str) -> bool:
        """Test if instance has item key defined."""
        return self.has_item_key(key)

    def get_charge_setting(self, key: str) -> Optional[object]:
        """Get item key."""
        return self.get_item(key)

    def set_charge_setting(self, key: str, value: Union[int, float]) -> Optional[object]:
        """Get item key."""
        return self.add_item(
            key=key,
            value=value
        )

    def set_charge_settings(self, data: dict) -> bool:
        """Set Battery Bank Name."""
        result = False
        if self.is_charge_settings_props(data):
            s1, s2, s3, s4 = True, True, True, True
            if RefCols.ABS_U.value in data:
                s1 = self.set_charge_setting(
                    key=ChargeCols.ABS_U.value,
                    value=data.get(RefCols.ABS_U.value)
                )
            if RefCols.FLOAT_U.value in data:
                s2 = self.set_charge_setting(
                    key=ChargeCols.FLOAT_U.value,
                    value=data.get(RefCols.FLOAT_U.value)
                )
            if RefCols.STORAGE_U.value in data:
                s2 = self.set_charge_setting(
                key=ChargeCols.STORAGE_U.value,
                value=data.get(RefCols.STORAGE_U.value)
            )
            if RefCols.EQ_U.value in data:
                s2 = self.set_charge_setting(
                key=ChargeCols.EQ_U.value,
                value=data.get(RefCols.EQ_U.value)
            )
            result = s1 is True\
                and s2 is True\
                and s3 is True\
                and s4 is True
        return result

    def init(self,
             **kwargs: ChargeSettingsProps
             ) -> bool:
        """Init battery bank data"""
        result = False
        if Ut.is_dict(kwargs, not_null=True):
            result = self.set_charge_settings(kwargs)
        return result

    def serialize(self):
        """
        Used to return a dictionary of the model'sattributes.

        :return: A dictionary of the model attributes.
        """
        return {
            ChargeCols.ABS_U.value: self.get_charge_setting(
                ChargeCols.ABS_U.value),
            ChargeCols.FLOAT_U.value: self.get_charge_setting(
                ChargeCols.FLOAT_U.value),
            ChargeCols.STORAGE_U.value: self.get_charge_setting(
                ChargeCols.STORAGE_U.value),
            ChargeCols.EQ_U.value: self.get_charge_setting(
                ChargeCols.EQ_U.value)
        }

    @staticmethod
    def get_charge_setting_keys():
        """Test if is valid item key"""
        return [
            'absorption_u',
            'float_u',
            'storage_u',
            'equalization_u'
        ]

    @staticmethod
    def is_charge_settings_props(data: dict, props_flag: BaseFlag = RefCols) -> bool:
        """Test if is valid item key"""
        return Ut.is_dict(data, not_null=True)\
            and (
                props_flag.ABS_U.value in data
                or props_flag.FLOAT_U.value in data
                or props_flag.STORAGE_U.value in data
                or props_flag.EQ_U.value in data)

    @staticmethod
    def is_valid_item_key(key: str):
        """Test if is valid item key"""
        return Ut.is_str(key, not_null=True)\
            and key in ChargeSettingsModel.get_charge_setting_keys()

    @staticmethod
    def is_valid_item_value(value: Union[int, float]):
        """Test if is valid item value"""
        return ElecHelper.is_charge_voltage(
            value
        )


class BatteryChargeHelper:
    """
    Battery Charge Helper.
    """
    @staticmethod
    def get_base_u_from_charge_u(absorption_u: Union[int, float]=0,
                                 float_u: Union[int, float]=0,
                                 storage_u: Union[int, float]=0,
                                 equalization_u: Union[int, float]=0
                                 ) -> Union[int, float]:
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
        list_items = [
            absorption_u, float_u, storage_u, equalization_u
        ]
        base_u_items = [
            BaseVolt.get_base_voltage_by_u_value(
                x
            )
            for x in list_items
            if ElecHelper.is_charge_voltage(x)
        ]

        valids = [
            x.value
            for x in base_u_items
            if not Ut.is_numeric(x)\
                and x.value > 0]
        nb_diff = len(set(valids))
        if nb_diff == 1:
            result = base_u_items[0]

        return result

    @staticmethod
    def get_u_by_base(value: Union[int, float],
                      out_base_u: Union[int, float]
                      ) -> float:
        """Get translatted tension by base of standardized tension."""
        result = 0
        base_u = BaseVolt.get_base_voltage_by_u_value(
            charge_voltage=value
        )
        default = BaseVolt.get_default()
        if BaseVolt.is_member(base_u)\
            and BaseVolt.is_member(out_base_u)\
            and BaseVolt.is_member(default)\
            and default.value > 0:

            in_coef = base_u.value / default.value
            out_coef = out_base_u.value / default.value
            result = ElecHelper.get_charge_voltage_value((value / in_coef) * out_coef)

        return result


class BatteryChargeModel(BatteryChargeHelper):
    """
    Battery Charge model
    """
    def __init__(self, **kwargs:ChargeSettingsProps):
        BatteryChargeHelper.__init__(self)
        self.coef_temp = 0.0
        self.coef_base_u = None
        self.charge_settings = ChargeSettingsModel()

        self.init(**kwargs)

    def is_ready(self) -> bool:
        """Test if instance has battery object"""
        return self.has_coef_temp()\
            and self.is_charge_settings()

    def is_charge_settings(self) -> bool:
        """Test if instance has battery object"""
        return self.has_charge_settings()\
            and self.charge_settings.is_charge_settings()

    def has_coef_temp(self) -> bool:
        """Has Battery charge temperrature correction coeficient."""
        return ElecHelper.is_coef_temp(
                self.coef_temp
            )\
            and BaseVolt.is_member(self.coef_base_u)

    def get_coef_temp(self) -> int:
        """Get Battery charge temperrature correction coeficient."""
        return ElecHelper.get_coef_temp_value(self.coef_temp)

    def set_coef_temp(self,
                      value: float=0.0,
                      base_u: BaseVolt = BaseVolt.U_12V
                      ) -> float:
        """Set Battery charge temperrature correction coeficient.."""
        result = False
        if ElecHelper.is_coef_temp(value)\
                and BaseVolt.is_member(base_u):
            self.coef_temp = ElecHelper.format_coef_temp_value(value)
            self.coef_base_u = base_u
            result = True
        return result

    def has_charge_setting(self, key: str) -> bool:
        """Test if instance has item key defined."""
        return self.charge_settings.has_charge_setting(key)

    def get_charge_setting(self, key: str) -> Optional[object]:
        """Get item key."""
        return self.charge_settings.get_charge_setting(key)

    def set_charge_setting(self, key: str, value: Union[int, float]) -> Optional[object]:
        """Get item key."""
        return self.charge_settings.set_charge_setting(
            key=key,
            value=value
        )

    def has_charge_settings(self) -> bool:
        """Has Charge settings."""
        return isinstance(self.charge_settings, ChargeSettingsModel)

    def get_charge_settings(self) -> ChargeSettingsModel:
        """Get Battery Charge settings."""
        result = None
        if self.has_charge_settings():
            result = self.charge_settings
        return result

    def init_charge_settings(self, reset: float = False) -> bool:
        """Has Charge settings."""
        if not self.has_charge_settings()\
                or reset is True:
            self.charge_settings = ChargeSettingsModel()

    def set_charge_settings(self, data: dict) -> float:
        """Set Battery Charge settings."""
        result = False
        self.init_charge_settings(reset=True)
        if Ut.is_dict(data, not_null=True):
            result = self.charge_settings.set_charge_settings(data)
        return result

    def set_props(self, data: dict) -> bool:
        """Set Battery Bank Name."""
        result = False
        if Ut.is_dict(data, not_null=True):
            self.set_coef_temp(data.get('charge_t_coef'))
            self.set_charge_settings(data)
            result = True
        return result

    def init(self,
             **kwargs: ChargeSettingsProps
             ) -> bool:
        """Init battery bank data"""
        result = False
        if Ut.is_dict(kwargs, not_null=True):
            result = self.set_props(kwargs)
        return result

    @staticmethod
    def get_charge_setting_keys():
        """Test if is valid item key"""
        return ChargeSettingsModel.get_charge_setting_keys()


class BatteryCharge(BatteryChargeModel):
    """
    Battery Charge module
    """
    def __init__(self, **kwargs:ChargeSettingsProps):
        BatteryChargeModel.__init__(self, **kwargs)
        self.base_u = BaseVolt.U_2V
        self.init(**kwargs)

    def set_u_base(self, base_u: Union[int, float, BaseVolt]) -> bool:
        """Set Global Base voltage value."""
        result = False
        if BaseVolt.is_member(base_u):
            self.base_u = base_u
            result = True
        else:
            new_base_u = BaseVolt.get_base_voltage_by_value(base_u)
            if BaseVolt.is_member(new_base_u):
                self.base_u = new_base_u
                result = True
        return result

    def get_charge_settings_u_base(self) -> dict:
        """Get standardized voltage base from charge voltage."""
        result = 0
        if self.is_charge_settings():
            result = BatteryCharge.get_base_u_from_charge_u(
                **self.charge_settings.serialize()
            )
        return result

    def format_charge_settings_by_u_base(self,
                                         base_u: Union[int, float, BaseVolt]
                                         ) -> dict:
        """Get standardized voltage base from charge voltage."""
        result = False
        val_base_u = self.get_charge_settings_u_base()
        if self.is_charge_settings()\
                and BaseVolt.is_member(base_u)\
                and BaseVolt.is_member(val_base_u)\
                and val_base_u != base_u:
            result = True
            charge_items = self.charge_settings.get_charge_setting_keys()
            for charge_key in charge_items:

                if self.charge_settings.has_charge_setting(charge_key) is True:
                    charge_setting = self.charge_settings.get_charge_setting(
                        key=charge_key
                    )
                    is_set = self.charge_settings.set_charge_setting(
                        key=charge_key,
                        value=BatteryCharge.get_u_by_base(
                            value=charge_setting,
                            out_base_u=base_u
                        )
                    )
                    if not is_set:
                        result = False
                        logger.error(
                            "Unable to format %s "
                            "charge setting value from %sv to %sv",
                            charge_key,
                            val_base_u,
                            base_u
                        )
        return result

    def set_charge_settings(self, data: dict) -> float:
        """Set Battery Charge settings."""
        result = False
        self.init_charge_settings(reset=True)
        if self.is_valid_charge_values(data):
            result = self.charge_settings.set_charge_settings(data)
        return result

    def init_u_base(self,
                    base_u: Optional[Union[int, float, BaseVolt]] = None
                    ) -> bool:
        """Set Global Base voltage value."""
        result = False
        self.base_u = 0
        if Ut.is_numeric(base_u, positive=True)\
                or BaseVolt.is_member(base_u):
            result = self.set_u_base(base_u)
            if result is True:
                result = self.format_charge_settings_by_u_base(self.base_u)
                logger.info(
                    "Fix charge base voltage value to %sv from config setting.",
                    self.base_u.value
                )
        elif self.is_charge_settings():
            base_u = self.get_charge_settings_u_base()
            result = self.set_u_base(base_u)
            if result is True:
                logger.info(
                    "Defined charge base voltage %sv from "
                    "configured charge settings values.",
                    self.base_u.value
                )
        if result is False:
            logger.error(
                "Unable to Define charge base voltage."
            )
        return result

    def set_props(self, data: dict) -> bool:
        """Set Battery Bank Name."""
        result = False
        if Ut.is_dict(data, not_null=True):
            self.set_coef_temp(data.get('charge_t_coef'))
            self.set_charge_settings(data)
            result = self.init_u_base(data.get('u_base'))
        return result

    def init(self,
             **kwargs: ChargeSettingsProps
             ) -> bool:
        """Init battery bank data"""
        result = False
        if Ut.is_dict(kwargs, not_null=True):
            result = self.set_props(kwargs)
        return result

    @staticmethod
    def compare_charge_values(data: dict,
                              flags: list,
                              flag_min: BaseFlag,
                              flag_max: BaseFlag
                              ) -> bool:
        """Compare two charge values and control min value is lower than max value."""
        result = True
        if Ut.is_dict(data, not_null=True)\
                and Ut.is_list(flags, not_null=True):
            # control value min is available
            is_flag_min = flag_min in flags\
            and data.get(flag_min.value) is not None
            # control value max is available
            is_flag_max = flag_max in flags\
                and data.get(flag_max.value) is not None
            # if min and max values are availables
            if is_flag_min and is_flag_max:
                # control min value is lower than max value
                result = data.get(flag_min.value) < data.get(flag_max.value)
        return result

    @staticmethod
    def control_charge_settings_values(data: dict,
                                       flags: list,
                                       props_flag: BaseFlag = RefCols
                                      ) -> bool:
        """
        Control charge settings validity.
        charge_storage_u <= charge_float_u < charge_absorption_u < charge_equalization_u
        """
        is_eq_abs = BatteryCharge.compare_charge_values(
            data=data,
            flags=flags,
            flag_min=props_flag.ABS_U,
            flag_max=props_flag.EQ_U
        )
        is_eq_float = BatteryCharge.compare_charge_values(
            data=data,
            flags=flags,
            flag_min=props_flag.FLOAT_U,
            flag_max=props_flag.EQ_U
        )
        is_eq_store = BatteryCharge.compare_charge_values(
            data=data,
            flags=flags,
            flag_min=props_flag.STORAGE_U,
            flag_max=props_flag.EQ_U
        )
        is_abs_float = BatteryCharge.compare_charge_values(
            data=data,
            flags=flags,
            flag_min=props_flag.FLOAT_U,
            flag_max=props_flag.ABS_U
        )
        is_abs_store = BatteryCharge.compare_charge_values(
            data=data,
            flags=flags,
            flag_min=props_flag.STORAGE_U,
            flag_max=props_flag.ABS_U
        )
        is_float_store = BatteryCharge.compare_charge_values(
            data=data,
            flags=flags,
            flag_min=props_flag.STORAGE_U,
            flag_max=props_flag.FLOAT_U
        )
        return is_eq_abs and is_eq_float and is_eq_store\
                and is_abs_float and is_abs_store and is_float_store

    @staticmethod
    def is_valid_charge_values(data: dict,
                               props_flag: BaseFlag = RefCols
                               ) -> bool:
        """
        Test charge settings validity.
        Controls:
        - charge_storage_u <= charge_float_u < charge_absorption_u < charge_equalization_u
        - base voltage is same for all values. (Avoid 2.35v and 12.4v)
        - all values are valid
        """
        result = False
        if ChargeSettingsModel.is_charge_settings_props(
                data=data,
                props_flag=props_flag):
            keys = props_flag.iter_member_values()
            available = [
                (member, key)
                for member, key in keys
                if key in data\
                    and member != props_flag.T_COEF_U
            ]
            valid_values = [
                member
                for member, key in available
                if key in data\
                        and ElecHelper.is_charge_voltage(data.get(key))
            ]
            nb_valid = len(valid_values)
            nb_available = len(available)
            common_base_v = BatteryCharge.get_base_u_from_charge_u(
                absorption_u=data.get(props_flag.ABS_U.value),
                float_u=data.get(props_flag.FLOAT_U.value),
                storage_u=data.get(props_flag.STORAGE_U.value),
                equalization_u=data.get(props_flag.EQ_U.value)
            )
            if nb_valid == nb_available\
                    and nb_valid > 0\
                    and BaseVolt.is_member(common_base_v):
                result = BatteryCharge.control_charge_settings_values(
                    data=data,
                    flags=valid_values,
                    props_flag=props_flag
                )
        return result

    @staticmethod
    def format_u_base_charge_settings(charge_settings: dict,
                                      base_u: Union[int, float, BaseVolt],
                                      props_flag: BaseFlag = RefCols
                                      ) -> dict:
        """Get standardized voltage base from charge voltage."""
        result = None
        # retrieve only charge settings not temp coef's
        charge_settings = Ut.get_items_from_dict(
            charge_settings,
            ChargeSettingsModel.get_charge_setting_keys()
        )
        # get charge_settings tension base
        base_charge_settings = BatteryCharge.get_base_u_from_charge_u(
            **charge_settings
        )
        # Format tension base numeric values to Enum
        if Ut.is_numeric(base_u, not_null=True):
            base_u = BaseVolt.get_base_voltage_by_value(base_u)

        # If valid props format charge settings
        if ChargeSettingsModel.is_charge_settings_props(
                data=charge_settings,
                props_flag=props_flag)\
                and BaseVolt.is_member(base_u)\
                and BaseVolt.is_member(base_charge_settings):
            if base_charge_settings != base_u:
                result = {}
                charge_items = ChargeSettingsModel.get_charge_setting_keys()
                for charge_key in charge_items:
                    charge_value = charge_settings.get(
                        charge_key
                    )
                    if ElecHelper.is_charge_voltage(charge_value) is True:
                        value = BatteryCharge.get_u_by_base(
                            value=charge_value,
                            out_base_u=base_u
                        )

                        if ElecHelper.is_charge_voltage(value) is True:
                            result[charge_key] = value
                        else:
                            logger.error(
                                "Unable to format %s "
                                "charge setting value from %sv to %sv",
                                charge_key,
                                base_charge_settings,
                                base_u
                            )
            else:
                result = dict(charge_settings)
        return result

    @staticmethod
    def apply_temp_correction(charge_settings: dict,
                              coef_temp: Union[int, float],
                              t_bat: Union[int, float]
                              ) -> Optional[dict]:
        """Apply temperrature correction to charge settings"""
        result, correction = None, 0
        if ElecHelper.is_coef_temp(t_bat)\
            and ElecHelper.is_coef_temp(coef_temp)\
            and BatteryCharge.is_valid_charge_values(
                data=charge_settings,
                props_flag=ChargeCols):
            result = {}
            diff_temp = round(t_bat - 25, 2)
            if not 0 <= diff_temp <= 1:
                correction = round(
                    (coef_temp * diff_temp) / 1000,
                    3
                )
                logger.debug(
                    "Charge settings need "
                    "temperrature correction. "
                    "- t_bat: %s - diff_temp: %s "
                    "correction: %s",
                    t_bat,
                    diff_temp,
                    correction
                )
                charge_items = ChargeSettingsModel.get_charge_setting_keys()
                for charge_key in charge_items:
                    result[charge_key] = ElecHelper.get_charge_voltage_value(
                        charge_settings.get(charge_key) + correction
                    )
            else:
                result = dict(charge_settings)
                logger.debug(
                    "Charge settings don't need "
                    "temperrature correction. "
                    "- t_bat: %s",
                    t_bat
                )
        return result, correction

    @staticmethod
    def get_formatted_coef_temp(base_u: Optional[BaseVolt] = None,
                                coef_temp: Union[int, float] = 0,
                                coef_base_u: Optional[BaseVolt] = None
                                ) -> Optional[tuple]:
        """
        Get formatted coef_temp.
        """
        result = 0
        if ElecHelper.is_coef_temp(coef_temp)\
                and BaseVolt.is_member(base_u)\
                and BaseVolt.is_member(coef_base_u):
            if base_u != coef_base_u:
                if base_u.value < coef_base_u.value:
                    coef = coef_base_u.value / base_u.value
                    result = round(coef_temp / coef, 3)
                else:
                    coef = base_u.value / coef_base_u.value
                    result = round(coef_temp * coef, 3)
            else:
                result = coef_temp
        return result

    @staticmethod
    def get_formatted_charge_settings(charge_settings: dict,
                                      bat_voltage: Union[int, float],
                                      coef_temp: Union[int, float] = 0,
                                      coef_base_u: Optional[BaseVolt] = None,
                                      t_bat: Union[int, float] = 0,
                                      props_flag: BaseFlag = ChargeCols
                                      ) -> Optional[tuple]:
        """
        Get formatted charge settings.
        """
        data = None

        charge_settings = Ut.get_items_from_dict(
            charge_settings,
            ChargeSettingsModel.get_charge_setting_keys()
        )

        if ElecHelper.is_charge_voltage(bat_voltage)\
            and BatteryCharge.is_valid_charge_values(
                data=charge_settings,
                props_flag=props_flag):

            data = ChargeData()
            data.bat_voltage = bat_voltage
            data.t_bat = t_bat
            data.base_u = BaseVolt.get_base_voltage_by_u_value(bat_voltage)

            base_charge_settings = BatteryCharge.get_base_u_from_charge_u(
                **charge_settings
            )
            # if charge_settings base voltage is different from bat_voltage value
            if data.base_u != base_charge_settings:
                compensed_charge = BatteryCharge.format_u_base_charge_settings(
                    charge_settings=charge_settings,
                    base_u=data.base_u,
                    props_flag=ChargeCols
                )
            coef_temp_real = BatteryCharge.get_formatted_coef_temp(
                base_u=data.base_u,
                coef_temp=coef_temp,
                coef_base_u=coef_base_u
            )
            if ElecHelper.is_coef_temp(t_bat)\
                and ElecHelper.is_coef_temp(coef_temp_real):
                compensed_charge, correction = BatteryCharge.apply_temp_correction(
                    charge_settings=compensed_charge,
                    coef_temp=coef_temp_real,
                    t_bat=t_bat
                )
                data.is_temp_correction = correction != 0
                data.temp_correction = correction
                data.compensed_charge = compensed_charge

        return data

    @staticmethod
    def detect_charge_step(charge_settings: dict,
                           bat_voltage: Union[int, float],
                           coef_temp: Union[int, float] = 0,
                           coef_base_u: Optional[BaseVolt] = None,
                           t_bat: Union[int, float] = 0,
                           props_flag: BaseFlag = ChargeCols
                           ) -> Optional[EChargeStep]:
        """
        Detect current possible charge step.
        """
        result = BatteryCharge.get_formatted_charge_settings(
            charge_settings=charge_settings,
            bat_voltage=bat_voltage,
            coef_temp=coef_temp,
            coef_base_u=coef_base_u,
            t_bat=t_bat,
            props_flag=props_flag
        )

        if ElecHelper.is_charge_voltage(bat_voltage)\
                and isinstance(result, ChargeData)\
                and BaseVolt.is_member(result.base_u)\
                and BatteryCharge.is_valid_charge_values(
                    data=result.compensed_charge,
                    props_flag=props_flag):

            # get only charge_settings upper than bat_voltage
            uppers = {}
            for key, value in result.compensed_charge.items():
                if value > bat_voltage:
                    uppers[key] = value
            # Determine actual charge step
            charge_list = ChargeCols.get_ordered_list()
            for index, item in enumerate(charge_list):
                if item.value in uppers:
                    step_value = result.compensed_charge.get(item.value)
                    diff_value = round(
                        bat_voltage - step_value,
                        3
                    )
                    diff_percent = round(
                        (diff_value * 100) / result.base_u.value,
                        3
                    )

                    result.current_step = ChargeStepData(
                        charge_step=ElecEnums.get_related_charge_step(item),
                        index_step=index,
                        diff_value=diff_value,
                        diff_percent=diff_percent,
                    )
                    break
            # get back charge step and calculate diff value
            if ChargeData.is_index_step(
                    result.current_step.index_step):
                index_lower = result.current_step.index_step -1
                lower_step = charge_list[index_lower]
                lower_value = result.compensed_charge.get(lower_step.value)
                diff_lower = round(
                    bat_voltage - lower_value,
                    3
                )
                diff_percent = round(
                    (diff_lower * 100) / result.base_u.value,
                    3
                )
                result.lower_step = ChargeStepData(
                    charge_step=ElecEnums.get_related_charge_step(lower_step),
                    index_step=index_lower,
                    diff_value=diff_lower,
                    diff_percent=diff_percent,
                )

        return result
