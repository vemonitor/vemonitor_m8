#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test DataChecker class."""
import time
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.data_cache import DataCache


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            self.obj = DataCache(
                max_rows=50
            )

    return HelperManager()


class TestDataChecker:
    """Test DataChecker class."""

    def test_add_data_cache(self, helper_manager):
        """Test check_columns method with bad chckers data """
        time_key = Ut.get_int(time.time())

        helper_manager.obj.add_data_cache(
            time_key=time_key,
            key='V',
            data=25.06
        )

        result = helper_manager.obj.get_data_from_cache(
           nb_items=1
        )
        assert Ut.is_tuple(result, not_null=True) and len(result) == 3
        cache_item = result[0].get(time_key)
        assert Ut.is_dict(cache_item, not_null=True) and len(cache_item) == 1
        assert cache_item.get('V') == 25.06

        helper_manager.obj.add_data_cache(
            time_key=time_key,
            key='I',
            data=2.25
        )

        result = helper_manager.obj.get_data_from_cache(
           nb_items=1
        )
        assert Ut.is_tuple(result, not_null=True) and len(result) == 3
        cache_item = result[0].get(time_key)
        assert Ut.is_dict(cache_item, not_null=True) and len(cache_item) == 2
        assert cache_item.get('I') == 2.25
