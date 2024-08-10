#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration AppBlock model Helper class
"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector\
    import SchemaValidateSelector as jValid

from vemonitor_m8.models.conf_app_blocks import ConfigAppBlocks


class ConfigAppConnectors(ConfigAppBlocks):
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
        ConfigAppBlocks.__init__(self, app_blocks=app_blocks)
        self.app_connectors = None

        self.set_app_connectors(app_connectors)

    def has_app_connectors(self) -> bool:
        """Test if object has valid App Connectors"""
        return ConfigAppConnectors.is_app_connectors(self.app_connectors)

    def has_app_connector_key(self, key: str) -> bool:
        """Test if object has valid App Connectors key"""
        return ConfigAppConnectors.is_app_connector_key(
            app_connector=self.app_connectors,
            key=key
        )

    def has_app_connector_key_item(self, key: str, item: str) -> bool:
        """Test if object has valid App Connectors key item"""
        return ConfigAppConnectors.is_app_connector_key_item(
            self.app_connectors,
            key,
            item
        )

    def set_app_connectors(self, app_connectors: Optional[dict]) -> bool:
        """Set App Connectors"""
        result = False
        if Ut.is_dict(app_connectors, not_null=True)\
                and jValid.is_valid_app_connectors_conf(app_connectors):
            self.app_connectors = app_connectors
            result = True
        return result

    def get_app_connector_by_key(self, key: str) -> Optional[dict]:
        """Get App Connectors by key"""
        result = None
        if self.has_app_connector_key(key):
            result = self.app_connectors.get(key)
        return result

    def get_app_connector_by_key_item(self,
                                      key: str,
                                      item: str
                                      ) -> Optional[dict]:
        """Get App Connectors by key item"""
        result = None
        if self.has_app_connector_key_item(key, item):
            result = self.app_connectors[key].get(item)
        return result

    def get_app_connector_by_sources(self, sources: dict) -> Optional[dict]:
        """Get App Connectors by sources"""
        result = None
        if ConfigAppBlocks.is_app_block_sources(sources):
            result = {}
            for key, items in sources.items():
                if Ut.is_list(items, not_null=True):
                    for item in items:
                        if self.has_app_connector_key_item(key, item):
                            if not Ut.is_dict(result.get(key)):
                                result[key] = {}
                            result[key][item] = self.get_app_connector_by_key_item(
                                key=key,
                                item=item
                            )
        return result

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
        if ConfigAppConnectors.is_app_connectors(app_connector)\
                and ConfigAppBlocks.is_app_block_sources(sources):

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

    @staticmethod
    def is_app_connectors(app_connectors: dict) -> bool:
        """Test if is valid App Connectors"""
        return Ut.is_dict(app_connectors, not_null=True)

    @staticmethod
    def is_app_connector_key(app_connector: dict, key: str) -> bool:
        """Test if is valid App Connectors key"""
        return ConfigAppConnectors.is_app_connectors(app_connector) and \
            Ut.is_str(key) and \
            Ut.is_dict(app_connector.get(key), not_null=True)

    @staticmethod
    def is_app_connector_key_item(app_connector: Optional[dict],
                                  key: str,
                                  item_key: str
                                  ) -> bool:
        """Test if is valid App Connectors key item"""
        return ConfigAppConnectors.is_app_connector_key(app_connector, key)\
            and Ut.is_str(item_key)\
            and Ut.is_dict(app_connector[key].get(item_key), not_null=True)
