#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration AppBlock model Helper class
"""
from typing import Optional
from ve_utils.utype import UType as Ut


class AppBlockHelper:
    """
    Configuration AppBlock model Helper class
    """
    @staticmethod
    def is_app_block(block: dict) -> bool:
        """Test if is valid App Block"""
        return Ut.is_dict(block) and\
            Ut.is_str(block.get('name')) and\
            Ut.is_str(block.get('app')) and\
            Ut.is_dict(block.get('inputs'), not_null=True) and\
            Ut.is_dict(block.get('outputs'), not_null=True)

    @staticmethod
    def add_app_block_columns(blocks_columns: list,
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

    @staticmethod
    def get_app_block_columns_from_inout(item: dict,
                                         blocks_columns: Optional[list] = None
                                         ) -> Optional[list]:
        """Get App Block columns from inputs and/or outputs"""
        if Ut.is_dict(item, not_null=True):
            for data in item.values():
                if Ut.is_list(data, not_null=True):
                    for content in data:
                        if Ut.is_dict(content)\
                                and Ut.is_list(content.get('columns'), not_null=True):
                            blocks_columns = AppBlockHelper.add_app_block_columns(
                                blocks_columns, content.get('columns'))
        return blocks_columns

    @staticmethod
    def get_app_block_columns_by_block(block: dict,
                                       blocks_columns: Optional[list] = None,
                                       selector: str = 'all'
                                       ) -> Optional[dict]:
        """Get App Block columns by blocks"""
        if not Ut.is_list(blocks_columns):
            blocks_columns = None

        if AppBlockHelper.is_app_block(block):
            if selector in ['all', 'inputs']:
                blocks_columns = AppBlockHelper.get_app_block_columns_from_inout(
                    item=block.get('inputs'),
                    blocks_columns=blocks_columns
                )
            if selector in ['all', 'outputs']:
                blocks_columns = AppBlockHelper.get_app_block_columns_from_inout(
                    item=block.get('outputs'),
                    blocks_columns=blocks_columns
                    )

        return blocks_columns

    @staticmethod
    def is_app_block_sources(sources: dict) -> bool:
        """Test if is valid App Block sources"""
        return Ut.is_dict(sources, not_null=True)

    @staticmethod
    def is_app_block_inout_source_content(content: dict) -> bool:
        """Test if is valid App Block input and/or output from source content"""
        return Ut.is_dict(content) and Ut.is_str(content.get('source'))

    @staticmethod
    def add_app_block_sources_key(sources: dict, key: str, source: str) -> None:
        """Add App Block sources key"""
        sources = Ut.init_dict_key(sources, key, [])
        if Ut.is_str(source) and\
                source not in sources.get(key):
            sources[key].append(source)
        return sources

    @staticmethod
    def get_app_block_sources_from_inout(item: dict,
                                         sources: Optional[dict] = None
                                         ) -> Optional[dict]:
        """Get App Block sources from inputs/outputs"""
        if Ut.is_dict(item, not_null=True):
            for key, data in item.items():
                if Ut.is_list(data, not_null=True):
                    for content in data:
                        if AppBlockHelper.is_app_block_inout_source_content(content):
                            sources = AppBlockHelper.add_app_block_sources_key(
                                sources, key, content.get('source')
                            )
        return sources

    @staticmethod
    def get_app_block_sources(block: dict,
                              sources: Optional[dict] = None,
                              selector: str = 'all'
                              ) -> Optional[dict]:
        """Get App Block sources"""
        if not Ut.is_dict(sources):
            sources = None

        if AppBlockHelper.is_app_block(block):
            if selector in ['all', 'inputs']:
                sources = AppBlockHelper.get_app_block_sources_from_inout(
                    block.get('inputs'), sources)

            if selector in ['all', 'outputs']:
                sources = AppBlockHelper.get_app_block_sources_from_inout(
                    block.get('outputs'), sources)
            
            if Ut.is_dict(block.get("redis_cache"), not_null=True)\
                    and Ut.is_str(
                        block['redis_cache'].get("source"), not_null=True
                    ):
                redis_source = block['redis_cache'].get("source")
                if Ut.is_dict(sources):
                    if not Ut.is_list(sources.get('redis')):
                        sources.update({'redis': [redis_source]})
                    elif Ut.is_list(sources.get('redis'), not_null=True)\
                            and redis_source not in sources.get('redis'):
                        sources['redis'].append(redis_source)
                else:
                    sources = {'redis': [redis_source]}
        return sources

    @staticmethod
    def is_app_block_args(block: dict) -> bool:
        """Test if is valid App Block Args"""
        return AppBlockHelper.is_app_block(block) and Ut.is_dict(block.get('args'), not_null=True)
