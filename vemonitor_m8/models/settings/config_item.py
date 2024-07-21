#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Config Item Model Class
"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector import SchemaValidateSelector as jValid
from vemonitor_m8.models.settings.config_helper import ConfigHelper
from vemonitor_m8.core.exceptions import SettingInvalidException

class ConfigItem(ConfigHelper):
    """
    Config Item Model Class
    """

    def __init__(self, **kwargs):
        """
        :param app_content: app_content settings
        :param app_block: Serial inputs settings
        :param app_connectors: Output Api's settings
        """
        ConfigHelper.__init__(self)
        self.app_block = None
        self.app_connectors = None
        self.data_structures = None
        self.init_data(**kwargs)

    def init_data(self, **kwargs):
        """Init Config item data"""
        if kwargs.get('app_block') is not None:
            self.set_app_block(kwargs.get('app_block'))
        if kwargs.get('app_conectors') is not None:
            self.set_app_connectors(kwargs.get('app_conectors'))
        if kwargs.get('check_points') is not None:
            self.set_data_structures(kwargs.get('check_points'))

    def is_valid(self):
        """Test if is valid Config Item Data"""
        return self.has_app_block() and self.has_app_connectors() and self.has_data_structures()

    def has_app_block(self) -> bool:
        """Test if obj has valid App Block item"""
        return ConfigHelper.is_app_block(self.app_block)

    def set_app_block(self, block: list) -> bool:
        """Set App Block item"""
        if jValid.is_valid_app_blocks_conf([block]):
            self.app_block = block
            return True
        return False

    def has_app_block_inputs(self) -> bool:
        """Test if obj has valid App Block inputs"""
        return self.has_app_block() and Ut.is_dict(self.app_block.get('inputs'), not_null=True)

    def has_app_block_outputs(self) -> bool:
        """Test if obj has valid App Block outputs"""
        return self.has_app_block() and Ut.is_dict(self.app_block.get('outputs'), not_null=True)

    def get_app_block_inputs(self) -> Optional[list]:
        """Get App Block inputs"""
        result = None
        if self.has_app_block_inputs():
            result = self.app_block.get('inputs')
        return result

    def get_app_block_outputs(self) -> Optional[list]:
        """Get App Block outputs"""
        result = None
        if self.has_app_block_outputs():
            result = self.app_block.get('outputs')
        return result

    def is_app_block_input_key(self, key:str) -> bool:
        """Test if is valid App Block input key"""
        return self.has_app_block_inputs()\
            and Ut.is_list(self.app_block['inputs'].get(key), not_null=True)

    def get_app_block_input_by_key(self, key:str) -> Optional[list]:
        """Get App Block input key"""
        result = None
        if self.is_app_block_input_key(key):
            result = self.app_block['inputs'].get(key)
        return result

    def get_app_block_columns(self) -> Optional[dict]:
        """Get App Block columns"""
        return ConfigHelper.get_app_block_columns_by_block(self.app_block)

    def set_data_structures(self, data_structures: dict) -> None:
        """Set Data Structure Conf"""
        cols = self.get_app_block_columns()
        if not ConfigHelper.is_missing_data_structure(data_structures, cols)\
                and jValid.is_valid_data_structure_conf(
                    conf_item=data_structures
                ):
            self.data_structures = data_structures
            return True
        raise SettingInvalidException(
                "Error on data_structure configuration, "
                "unable to retrieve all appBlock columns checks."
            )

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
            'app_block': self.app_block,
            'app_conector': self.app_connectors,
            'data_structures': self.data_structures
        }

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
