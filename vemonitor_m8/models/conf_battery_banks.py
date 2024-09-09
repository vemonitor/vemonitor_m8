#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration AppBlock model Helper class
"""
from typing import Optional
from jsonschema import SchemaError, ValidationError
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector\
    import SchemaValidateSelector as jValid
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.models.conf_data_structures import ConfigDataStructures


class ConfigBatteryBanks(ConfigDataStructures):
    """
    Configuration App Connectors model Helper class
    """
    def __init__(self,
                 app_blocks: Optional[list] = None,
                 app_connectors: Optional[dict] = None):
        """
        Initialise Config model instance.

        :Example :
            >>> conf = Config(app_blocks=[...], app_connectors={...})
        :param app_blocks: App Blocks settings
        :param app_connectors: Output Api Connectors settings
        """
        ConfigDataStructures.__init__(
            self,
            app_blocks=app_blocks,
            app_connectors=app_connectors
        )
        self.battery_banks = None

    def has_battery_banks(self) -> bool:
        """Test if obj has valid Battery Banks"""
        return Ut.is_dict(self.battery_banks, not_null=True)

    def validate_battery_banks(self, battery_banks: dict) -> None:
        """Validate Battery Banks"""
        result = False
        if Ut.is_dict(battery_banks, not_null=True):
            result = True
            for item in battery_banks.values():
                try:
                    jValid.is_valid_battery_banks_conf(
                        conf_item={"batteryBankArgs": item}
                    )
                except (SchemaError, ValidationError) as ex:
                    result = False
                    raise SettingInvalidException(
                        "Fatal Error : invalid batteryBank data,"
                        "for key {key}."
                    ) from ex
        else:
            raise SettingInvalidException(
                "Fatal Error : invalid batteryBank data,"
                "is empty or not a dict."
            )
        return result

    def set_battery_banks(self, battery_banks: dict) -> None:
        """Set Battery Banks"""
        result = False
        if self.validate_battery_banks(battery_banks):
            self.battery_banks = battery_banks
            result = True
        return result

    def get_battery_banks_from_mid(self, middlewares: dict) -> Optional[dict]:
        """Get Battery Banks from middlewares"""
        res = None
        if Ut.is_dict(middlewares, not_null=True):
            for key, arg in middlewares.items():
                if Ut.is_str(arg) and Ut.is_str(arg):
                    if key == 'batteryBanks':
                        if Ut.is_dict(self.battery_banks.get(arg)):
                            return self.battery_banks.get(arg)
        return res

    def get_battery_bank(self) -> None:
        """Get Battery Bank from Args"""
        res = None
        project_name = None
        if self.has_app_block_key(0)\
                and self.has_battery_banks()\
                and Ut.is_dict(
                    self.app_blocks[0].get('middlewares'),
                    not_null=True):
            project_name = self.app_blocks[0]['middlewares'].get('batteryBanks')

        if Ut.is_str(project_name, not_null=True)\
                and self.has_battery_banks()\
                and Ut.is_dict(
                    self.battery_banks.get(project_name),
                    not_null=True):
            res = self.battery_banks.get(project_name)
        return res
