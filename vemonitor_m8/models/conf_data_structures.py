#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration AppBlock model Helper class
"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector\
    import SchemaValidateSelector as jValid
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.models.conf_app_connectors import ConfigAppConnectors


class ConfigDataStructures(ConfigAppConnectors):
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
        ConfigAppConnectors.__init__(
            self,
            app_blocks=app_blocks,
            app_connectors=app_connectors
        )
        self.data_structures = None

    def has_data_structures(self) -> bool:
        """Test if obj has valid Data Structures"""
        return ConfigDataStructures.is_data_structures(self.data_structures)

    def has_data_structures_point_key(self, key) -> bool:
        """Test if obj has valid Data Structure point key"""
        return ConfigDataStructures.is_data_structures_point_key(
            self.data_structures,
            key
        )

    def get_data_structures_point_by_columns(self,
                                             columns: list
                                             ) -> Optional[dict]:
        """Get Data Structure point by columns names"""
        result = None
        if self.has_data_structures() and Ut.is_list(columns, not_null=True):
            result = {}
            data_points = self.data_structures.get('points')
            for col in columns:
                if Ut.is_str(col) and self.has_data_structures_point_key(col):
                    result[col] = data_points.get(col)
        return result

    def set_data_structures(self, data_structures: dict) -> None:
        """Set Data Structures Conf"""
        cols = self.get_app_blocks_columns()
        if ConfigDataStructures.is_data_structures(data_structures)\
                and not ConfigDataStructures.is_missing_data_structure(
                    data_structures, cols)\
                and jValid.is_valid_data_structure_conf(
                    conf_item=data_structures):
            self.data_structures = data_structures
            return True
        raise SettingInvalidException(
                "Error on data_structure configuration, "
                "unable to retrieve all appBlock columns checks."
            )

    @staticmethod
    def is_data_structures(data_structures) -> bool:
        """Test if is valid Data Structure conf"""
        return Ut.is_dict(data_structures) and\
            Ut.is_dict(data_structures.get('devices'), not_null=True) and\
            Ut.is_dict(data_structures.get('points'), not_null=True)

    @staticmethod
    def is_data_structures_point_key(data_structures, key) -> bool:
        """Test if is valid Data Structure point key"""
        return ConfigDataStructures.is_data_structures(data_structures) and\
            Ut.is_str(key) and\
            Ut.is_dict(data_structures['points'].get(key), not_null=True)

    @staticmethod
    def is_all_data_structures_covered(data_structures, cols) -> bool:
        """Test if obj has all Data Structure covered"""
        return ConfigDataStructures.is_data_structures(data_structures)\
            and Ut.is_list(cols, not_null=True)\
            and len(data_structures.get('points')) == len(cols)

    @staticmethod
    def is_missing_data_structure(data_structures, cols) -> bool:
        """Test if is missing Data Structure conf"""
        result = False
        if Ut.is_dict(data_structures, not_null=True)\
                and Ut.is_dict(data_structures.get('points'), not_null=True)\
                and not ConfigDataStructures.is_all_data_structures_covered(
                    data_structures=data_structures,
                    cols=cols
                ):
            result = True
            missing = []
            for i in cols:
                if data_structures['points'].get(i) is None:
                    missing.append(i)
            if len(missing) > 0:
                raise SettingInvalidException(
                    "Error on checkColumns configuration, "
                    "unable to retrieve all appBlock columns checks. "
                    "Add missing columns to victronDeviceData.yaml "
                    "or userColumnsChecks.yaml "
                    f"Missing columns list : {missing}"
                )
            result = False
        return result
