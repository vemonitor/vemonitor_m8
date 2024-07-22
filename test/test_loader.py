#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test Loader class."""
import inspect
from os import path as Opath
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.loader import Loader
from vemonitor_m8.core.exceptions import YAMLFileNotFound


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            current_script_path = Opath.dirname(
            Opath.abspath(
                    inspect.getfile(inspect.currentframe())
                )
            )
            self.test_path = Opath.join(
                current_script_path,
                "conf"
            )

    return HelperManager()


class TestLoader:
    """Test Loader class."""

    def test_file_not_found(self):
        """Test get_app_blocks_by_app_or_name method """
        file_names = ['nofile.yaml']
        with pytest.raises(YAMLFileNotFound):
            Loader(file_names)

    def test_get_yaml_config(self, helper_manager):
        """Test get_app_blocks_by_app_or_name method """
        file_names = ['dummy_conf_dict.yaml']
        obj = Loader(file_names, file_path=helper_manager.test_path)
        obj.set_file_path(
            file_name=file_names,
            base_path=helper_manager.test_path
        )

        conf = obj.get_yaml_config()
        assert Ut.is_dict(conf) and len(conf) == 7 and \
            len(conf.get('Imports')) == 2 and \
            len(conf.get('Dummy_1')) == 2 and\
            len(conf.get('Dummy_2')) == 2 and\
            len(conf.get('Dummy_3')) == 2 and\
            len(conf.get('Dummy_4')) == 2 and\
            len(conf.get('Dummy_5')) == 2 and\
            len(conf.get('Dummy_6')) == 2

        conf = obj.get_yaml_config(['dummy_conf_dict1.yaml'])
        assert Ut.is_dict(conf) and len(conf) == 5 and \
            len(conf.get('Imports')) == 2 and \
            len(conf.get('Dummy_1')) == 2 and\
            len(conf.get('Dummy_2')) == 2 and\
            len(conf.get('Dummy_3')) == 2 and\
            len(conf.get('Dummy_4')) == 2 and\
            conf.get('Dummy_5') is None and\
            conf.get('Dummy_6') is None

    def test_get_real_file_path(self, helper_manager):
        """Test get_paths_order method """
        file_name = 'dummy_conf_dict.yaml'

        # Test relative path
        test_path = Opath.join('test', 'conf', file_name)
        result = Loader.get_real_file_path(test_path)
        assert Opath.isfile(result)

        # Test absolute path
        abs_path = Opath.join(helper_manager.test_path, file_name)
        result = Loader.get_real_file_path(abs_path)
        assert Opath.isfile(result)

    def test_get_paths_order(self):
        """Test get_paths_order method """
        path_order = Loader.get_paths_order()
        assert Ut.is_list(path_order, not_null=True)

    def test_set_file_path(self, helper_manager):
        """Test set_file_path method """
        file_names = ['dummy_conf_dict.yaml']
        obj = Loader(file_names, file_path=helper_manager.test_path)

        assert Ut.is_str(obj.file_path, not_null=True)

        with pytest.raises(YAMLFileNotFound):
            obj.set_file_path(
                file_name=file_names,
                base_path=''
            )
