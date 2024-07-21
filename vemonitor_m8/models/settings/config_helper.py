#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration model Helper class
"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector import SchemaValidateSelector as jValid
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.models.settings.app_block_helper import AppBlockHelper


class ConfigHelper(AppBlockHelper):
    """
    This Class is representing configuration settings.
    """

    def __init__(self):
        """
        Initialise ConfigHelper model instance.

        :Example :
            >>> conf_helper = ConfigHelper()
        """
        self.app_connectors = None
        self.data_structures = None

    def has_app_connectors(self) -> bool:
        """Test if object has valid App Connectors"""
        return ConfigHelper.is_app_connectors(self.app_connectors)

    def has_app_connector_key(self, key: str) -> bool:
        """Test if object has valid App Connectors key"""
        return ConfigHelper.is_app_connector_key(self.app_connectors, key)

    def has_app_connector_key_item(self, key: str, item: str) -> bool:
        """Test if object has valid App Connectors key item"""
        return ConfigHelper.is_app_connector_key_item(self.app_connectors, key, item)

    def set_app_connectors(self, app_connectors: dict) -> None:
        """Set App Connectors"""
        if jValid.is_valid_app_connectors_conf(app_connectors):
            self.app_connectors = app_connectors
            return True
        return False

    def get_app_connector_by_key(self, key: str) -> Optional[dict]:
        """Get App Connectors by key"""
        if self.has_app_connector_key(key):
            return self.app_connectors.get(key)
        return None

    def get_app_connector_by_key_item(self, key: str, item: str) -> Optional[dict]:
        """Get App Connectors by key item"""
        if self.has_app_connector_key_item(key, item):
            return self.app_connectors[key].get(item)
        return None

    def get_app_connector_by_sources(self, sources: dict) -> Optional[dict]:
        """Get App Connectors by sources"""
        res = None
        if ConfigHelper.is_app_block_sources(sources):
            res = {}
            for key, items in sources.items():
                if Ut.is_list(items, not_null=True):
                    for item in items:
                        if self.has_app_connector_key_item(key, item):
                            if not Ut.is_dict(res.get(key)):
                                res[key] = {}
                            res[key][item] = self.app_connectors[key].get(item)
        return res

    def has_data_structures(self) -> bool:
        """Test if obj has valid Data Structures"""
        return ConfigHelper.is_data_structures(self.data_structures)

    def has_data_structures_point_key(self, key) -> bool:
        """Test if obj has valid Data Structure point key"""
        return ConfigHelper.is_data_structures_point_key(self.data_structures, key)

    def get_data_structures_point_by_columns(self,
                                             columns: list
                                             ) -> Optional[dict]:
        """Get Data Structure point by columns names"""
        res = None
        if self.has_data_structures() and Ut.is_list(columns, not_null=True):
            res = {}
            data_points = self.data_structures.get('points')
            for col in columns:
                if Ut.is_str(col) and self.has_data_structures_point_key(col):
                    res[col] = data_points['points'].get(col)
        return res

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__

    @staticmethod
    def is_app_connectors(app_connectors: dict) -> bool:
        """Test if is valid App Connectors"""
        return Ut.is_dict(app_connectors, not_null=True)

    @staticmethod
    def is_app_connector_key(app_connector: dict, key: str) -> bool:
        """Test if is valid App Connectors key"""
        return ConfigHelper.is_app_connectors(app_connector) and \
            Ut.is_str(key) and \
            Ut.is_dict(app_connector.get(key), not_null=True)

    @staticmethod
    def is_app_connector_key_item(app_connector: dict, key: str, item_key: str) -> bool:
        """Test if is valid App Connectors key item"""
        return ConfigHelper.is_app_connector_key(app_connector, key) and \
            Ut.is_str(item_key) and \
            Ut.is_dict(app_connector[key].get(item_key), not_null=True)

    @staticmethod
    def is_data_structures(data_structures) -> bool:
        """Test if is valid Data Structure conf"""
        return Ut.is_dict(data_structures) and\
            Ut.is_dict(data_structures.get('devices'), not_null=True) and\
            Ut.is_dict(data_structures.get('points'), not_null=True)

    @staticmethod
    def is_data_structures_point_key(data_structures, key) -> bool:
        """Test if is valid Data Structure point key"""
        return ConfigHelper.is_data_structures(data_structures) and\
            Ut.is_str(key) and\
            Ut.is_dict(data_structures['points'].get(key), not_null=True)

    @staticmethod
    def is_all_data_structures_covered(data_structures, cols) -> bool:
        """Test if obj has all Data Structure covered"""
        return ConfigHelper.is_data_structures(data_structures)\
            and Ut.is_list(cols, not_null=True)\
            and len(data_structures.get('points')) == len(cols)

    @staticmethod
    def is_missing_data_structure(data_structures, cols) -> bool:
        """Test if is missing Data Structure conf"""
        result = False
        if not ConfigHelper.is_all_data_structures_covered(data_structures, cols):
            result = True
            missing = []
            for i in cols:
                if data_structures['points'].get(i) is None:
                    missing.append(i)
            if len(missing) > 0:
                raise SettingInvalidException(
                    "Error on checkColumns configuration, "
                    "unable to retrieve all appBlock columns checks. "
                    "Add missing columns to victronDeviceData.yaml or userColumnsChecks.yaml "
                    f"Missing columns list : {missing}"
                )
            result = False
        return result
