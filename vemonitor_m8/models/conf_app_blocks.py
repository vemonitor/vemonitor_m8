#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration AppBlock model Helper class
"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector\
    import SchemaValidateSelector as jValid
from vemonitor_m8.models.app_block_helper import AppBlockHelper


class ConfigAppBlocks(AppBlockHelper):
    """
    Configuration App Connectors model Helper class
    """
    def __init__(self,
                 app_blocks: Optional[list] = None
                 ):
        """
        Initialise Config model instance.

        :Example :
            >>> conf = Config(app_blocks=[...], app_connectors={...})
        :param app_blocks: App Blocks settings
        :param app_connectors: Output Api Connectors settings
        """
        self.app_blocks: Optional[list] = None

        self.set_app_blocks(app_blocks)

    def has_app_blocks(self) -> bool:
        """Test instance has app_blocks configuration"""
        return Ut.is_list(self.app_blocks, not_null=True)

    def has_app_block_key(self, index: int) -> bool:
        """Test instance has app_blocks configuration"""
        return self.has_app_blocks()\
            and Ut.is_int(index, mini=0)\
            and len(
                self.app_blocks  # type: ignore
            ) > index\
            and ConfigAppBlocks.is_app_block(
                block=self.app_blocks[index]  # type: ignore
            )

    def set_app_blocks(self, app_blocks: Optional[list]) -> bool:
        """Set App Blocks configuration"""
        if Ut.is_list(app_blocks, not_null=True)\
                and jValid.is_valid_app_blocks_conf(
                    app_blocks):  # type: ignore
            self.app_blocks = app_blocks
            return True
        return False

    def get_app_block_by_name(self, block_name: str) -> Optional[dict]:
        """Get App Blocks by Name"""
        result = None
        if self.has_app_blocks():
            for block in self.app_blocks:  # type: ignore
                if ConfigAppBlocks.is_app_block(block)\
                        and block.get('name') == block_name:
                    result = block
                    break
        return result

    def get_app_block_by_app(self, app_name: str) -> Optional[dict]:
        """Get App Blocks by App"""
        result = None
        if self.has_app_blocks():
            for block in self.app_blocks:  # type: ignore
                if ConfigAppBlocks.is_app_block(block)\
                        and block.get('app') == app_name:
                    result = block
                    break
        return result

    def get_app_blocks_columns(self) -> Optional[dict]:
        """Get App Blocks columns"""
        res = None
        if self.has_app_blocks():
            for block in self.app_blocks:  # type: ignore
                if ConfigAppBlocks.is_app_block(block):
                    res = ConfigAppBlocks.get_app_block_columns_by_block(block)
        return res

    def get_app_blocks_sources(self) -> Optional[dict]:
        """Get App Blocks sources"""
        sources = None
        if self.has_app_blocks():
            for block in self.app_blocks:  # type: ignore
                sources = ConfigAppBlocks.get_app_block_sources(
                    block=block,
                    sources=sources
                )
        return sources

    def get_redis_cache_by_key(self, index: int) -> Optional[dict]:
        """Get App Block redis cache conf"""
        result = None
        if self.has_app_block_key(index=index):
            result = self.app_blocks[index].get('redis_cache')  # type: ignore
        return result
