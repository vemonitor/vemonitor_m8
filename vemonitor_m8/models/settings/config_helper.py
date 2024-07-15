#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration model Helper class
"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.confManager.shema_validate_selector import SchemaValidateSelector as jValid
from vemonitor_m8.core.exceptions import SettingInvalidException


class ConfigHelper(object):
    """
    This Class is representing configuration settings.
    """

    def __init__(self):
        """

        """
        self.app_connectors = None
        self.data_structures = None

    def is_app_block(self, block: dict) -> bool:
        """Test if is valid App Block"""
        return Ut.is_dict(block) and\
            Ut.is_str(block.get('name')) and\
            Ut.is_str(block.get('app')) and\
            Ut.is_dict(block.get('inputs'), not_null=True) and\
            Ut.is_dict(block.get('outputs'), not_null=True)

    def add_app_block_columns(self,
                              blocks_columns: list,
                              columns: list
                              ) -> list:
        """Add App Block columns to config"""
        if Ut.is_list(columns, not_null=True):
            if not Ut.is_list(blocks_columns, not_null=True):
                blocks_columns = columns
            else:
                for col in columns:
                    if Ut.is_str(col) and col not in blocks_columns:
                        blocks_columns.append(col)
        return blocks_columns

    def get_app_block_columns_from_inout(self,
                                         item: dict,
                                         blocks_columns: Optional[list] = None
                                         ) -> Optional[list]:
        """Get App Block columns from in and out"""
        if Ut.is_dict(item, not_null=True):
            for data in item.values():
                if Ut.is_list(data, not_null=True):
                    for content in data:
                        if Ut.is_dict(content)\
                                and Ut.is_list(content.get('columns'), not_null=True):
                            blocks_columns = self.add_app_block_columns(
                                blocks_columns, content.get('columns'))
        return blocks_columns

    def get_app_block_columns_by_block(self,
                                       block: dict,
                                       blocks_columns: Optional[list] = None,
                                       selector: str = 'all'
                                       ) -> Optional[dict]:
        """Get App Block columns by blocks"""
        if not Ut.is_list(blocks_columns):
            blocks_columns = None

        if self.is_app_block(block):
            if selector in ['all', 'inputs']:
                blocks_columns = self.get_app_block_columns_from_inout(
                    block.get('inputs'), blocks_columns)
            if selector in ['all', 'outputs']:
                blocks_columns = self.get_app_block_columns_from_inout(
                    block.get('outputs'), blocks_columns)

        return blocks_columns

    def is_app_block_sources(self, sources: dict) -> bool:
        """Test if is valid App Block sources"""
        return Ut.is_dict(sources, not_null=True)

    def is_app_block_inout_source_content(self, content: dict) -> bool:
        """Test if is valid App Block input and/or output from source content"""
        return Ut.is_dict(content) and Ut.is_str(content.get('source'))

    def add_app_block_sources_key(self, sources: dict, key: str, source: str) -> None:
        """Add App Block sources key"""
        sources = Ut.init_dict_key(sources, key, [])
        if Ut.is_str(source) and\
                source not in sources.get(key):
            sources[key].append(source)
        return sources

    def get_app_block_sources_from_inout(self,
                                         item: dict,
                                         sources: Optional[dict] = None
                                         ) -> Optional[dict]:
        """Get App Block sources from inputs/outputs"""
        if Ut.is_dict(item, not_null=True):
            for key, data in item.items():
                if Ut.is_list(data, not_null=True):
                    for content in data:
                        if self.is_app_block_inout_source_content(content):
                            sources = self.add_app_block_sources_key(
                                sources, key, content.get('source')
                            )
        return sources

    def get_app_block_sources(self,
                              block: dict,
                              sources: Optional[dict] = None,
                              selector: str = 'all'
                              ) -> Optional[dict]:
        """Get App Block sources"""
        if not Ut.is_dict(sources):
            sources = None

        if self.is_app_block(block):
            if selector in ['all', 'inputs']:
                sources = self.get_app_block_sources_from_inout(
                    block.get('inputs'), sources)

            if selector in ['all', 'outputs']:
                sources = self.get_app_block_sources_from_inout(
                    block.get('outputs'), sources)
        return sources

    def is_app_block_args(self, block: dict) -> bool:
        """Test if is valid App Block Args"""
        return self.is_app_block(block) and Ut.is_dict(block.get('args'), not_null=True)

    def is_app_connectors(self, app_connectors: dict) -> bool:
        """Test if is valid App Connectors"""
        return Ut.is_dict(app_connectors, not_null=True)

    def is_app_connector_key(self, app_connector: dict, key: str) -> bool:
        """Test if is valid App Connectors key"""
        return self.is_app_connectors(app_connector) and \
            Ut.is_str(key) and \
            Ut.is_dict(app_connector.get(key), not_null=True)

    def is_app_connector_key_item(self, app_connector: dict, key: str, item_key: str) -> bool:
        """Test if is valid App Connectors key item"""
        return self.is_app_connector_key(app_connector, key) and \
            Ut.is_str(item_key) and \
            Ut.is_dict(app_connector[key].get(item_key), not_null=True)

    def has_app_connectors(self) -> bool:
        """Test if object has valid App Connectors"""
        return self.is_app_connectors(self.app_connectors)

    def has_app_connector_key(self, key: str) -> bool:
        """Test if object has valid App Connectors key"""
        return self.is_app_connector_key(self.app_connectors, key)

    def has_app_connector_key_item(self, key: str, item: str) -> bool:
        """Test if object has valid App Connectors key item"""
        return self.is_app_connector_key_item(self.app_connectors, key, item)

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
        if self.is_app_block_sources(sources):
            res = {}
            for key, items in sources.items():
                if Ut.is_list(items, not_null=True):
                    for item in items:
                        if self.has_app_connector_key_item(key, item):
                            if not Ut.is_dict(res.get(key)):
                                res[key] = {}
                            res[key][item] = self.app_connectors[key].get(item)
        return res

    def is_data_structures(self, data_structures) -> bool:
        """Test if is valid Data Structure conf"""
        return Ut.is_dict(data_structures) and\
            Ut.is_dict(data_structures.get('keys'), not_null=True) and\
            Ut.is_dict(data_structures.get('points'), not_null=True)

    def is_data_structures_point_key(self, data_structures, key) -> bool:
        """Test if is valid Data Structure point key"""
        return self.is_data_structures(data_structures) and\
            Ut.is_str(key) and\
            Ut.is_dict(data_structures['points'].get(key), not_null=True)

    def has_data_structures(self) -> bool:
        """Test if obj has valid Data Structures"""
        return self.is_data_structures(self.data_structures)

    def has_data_structures_point_key(self, key) -> bool:
        """Test if obj has valid Data Structure point key"""
        return self.is_data_structures_point_key(self.data_structures, key)

    def has_all_data_structures_covered(self, data_structures, cols) -> bool:
        """Test if obj has all Data Structure covered"""
        return self.is_data_structures(data_structures)\
            and Ut.is_list(cols, not_null=True)\
            and len(data_structures.get('points')) == len(cols)

    def is_missing_data_structure(self, data_structures, cols) -> bool:
        """Test if is missing Data Structure conf"""
        if not self.has_all_data_structures_covered(data_structures, cols):
            missing = []
            for i in cols:
                if data_structures['points'].get(i) is None:
                    missing.append(i)

            raise SettingInvalidException(
                "Error on checkColumns configuration, "
                "unable to retrieve all appBlock columns checks. "
                "Add missing columns to victronDeviceData.yaml or userColumnsChecks.yaml "
                f"Missing columns list : {missing}"
            )
        return True

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
