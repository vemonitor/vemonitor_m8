#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Config Model Class
"""
from typing import Optional
from jsonschema import SchemaError, ValidationError
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector import SchemaValidateSelector as jValid
from vemonitor_m8.models.config_helper import ConfigHelper
from vemonitor_m8.core.exceptions import SettingInvalidException


class Config(ConfigHelper):
    """
    Config Model Class
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
        ConfigHelper.__init__(self)
        self.app_blocks = None
        self.app_connectors = None
        self.data_structures = None
        self.battery_banks = None
        self.solar_plants = None

        if app_blocks is not None:
            self.set_app_blocks(app_blocks)

        if app_connectors is not None:
            self.set_app_connectors(app_connectors)

    def is_valid(self):
        """Test if is valid Config Data"""
        return self.has_app_blocks()\
            and self.has_app_connectors()\
            and self.has_data_structures()

    def has_app_blocks(self) -> bool:
        """Test instance has app_blocks configuration"""
        return Ut.is_list(self.app_blocks, not_null=True)

    def set_app_blocks(self, app_blocks: list) -> bool:
        """Set App Blocks configuration"""
        if Ut.is_list(app_blocks, not_null=True)\
                and jValid.is_valid_app_blocks_conf(app_blocks):
            self.app_blocks = app_blocks
            return True
        return False

    def get_app_block_by_name(self, block_name: str) -> Optional[dict]:
        """Get App Blocks by Name"""
        result = None
        if self.has_app_blocks():
            for block in self.app_blocks:
                if ConfigHelper.is_app_block(block)\
                        and block.get('name') == block_name:
                    result = block
                    break
        return result

    def get_app_block_by_app(self, app_name: str) -> Optional[dict]:
        """Get App Blocks by App"""
        result = None
        if self.has_app_blocks():
            for block in self.app_blocks:
                if ConfigHelper.is_app_block(block)\
                        and block.get('app') == app_name:
                    result = block
                    break
        return result

    def get_app_blocks_columns(self) -> Optional[dict]:
        """Get App Blocks columns"""
        res = None
        if self.has_app_blocks():
            for block in self.app_blocks:
                if ConfigHelper.is_app_block(block):
                    res = ConfigHelper.get_app_block_columns_by_block(block)
        return res

    def get_app_blocks_sources(self) -> Optional[dict]:
        """Get App Blocks sources"""
        sources = None
        if self.has_app_blocks():
            for block in self.app_blocks:
                sources = ConfigHelper.get_app_block_sources(
                    block=block,
                    sources=sources
                )
        return sources

    def set_and_reduce_app_connectors(self, app_connector: dict) -> None:
        """Get And reduce App Connectors"""
        if Ut.is_dict(app_connector, not_null=True):
            if self.has_app_blocks():
                self.set_app_connectors(
                    self.reduce_app_connector_from_sources(app_connector)
                )
            else:
                self.set_app_connectors(app_connector)
            return Ut.is_dict(self.app_connectors, not_null=True)
        return False

    def reduce_app_connector_from_sources(self, app_connector: dict) -> dict:
        """Reduce App Connectors from sources"""
        res = None
        sources = self.get_app_blocks_sources()
        if ConfigHelper.is_app_connectors(app_connector)\
                and ConfigHelper.is_app_block_sources(sources):

            sources_keys = list(sources.keys())
            res = {}
            for key, conector in app_connector.items():
                if key in sources_keys:
                    if not Ut.is_dict(res.get(key)):
                        res[key] = {}

                    if Ut.is_dict(conector):
                        for item_key, item in conector.items():
                            if Ut.is_dict(item) and\
                                    item_key in sources.get(key):
                                res[key][item_key] = item
        return res

    def set_data_structures(self, data_structures: dict) -> None:
        """Set Data Structures Conf"""
        cols = self.get_app_blocks_columns()
        if ConfigHelper.is_data_structures(data_structures)\
                and not ConfigHelper.is_missing_data_structure(
                    data_structures, cols)\
                and jValid.is_valid_data_structure_conf(
                    conf_item=data_structures):
            self.data_structures = data_structures
            return True
        raise SettingInvalidException(
                "Error on data_structure configuration, "
                "unable to retrieve all appBlock columns checks."
            )

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

    def get_battery_banks_from_args(self, args: dict) -> Optional[dict]:
        """Get Battery Banks from Args"""
        res = None
        if Ut.is_dict(args, not_null=True):
            for key, arg in args.items():
                if Ut.is_str(arg) and Ut.is_str(arg):
                    if key == 'batteryBanks':
                        if Ut.is_dict(self.battery_banks.get(arg)):
                            return self.battery_banks.get(arg)
        return res

    def __str__(self):
        """__str__"""
        return str(self.serialize())

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of order
        :rtype: Dict
        """

        return {
            'app_blocks': self.app_blocks,
            'app_connector': self.app_connectors,
            'battery_banks': self.battery_banks,
            'solar_plants': self.solar_plants,
            'data_structures': self.data_structures
        }
