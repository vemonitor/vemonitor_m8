#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test DataChecker class."""
import inspect
from os import path as Opath
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.data_structure_loader import DataStructureLoader
from vemonitor_m8.core.data_checker import DataChecker
from vemonitor_m8.core.exceptions import DeviceDataConfError
from vemonitor_m8.core.exceptions import DeviceInputValueError
from vemonitor_m8.core.exceptions import DeviceOutputValueError


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
            self.obj = DataStructureLoader(
                file_names="dummy_g_conf.yaml",
                file_path=self.test_path)
            self.checkers = self.obj.get_yaml_data_structure()

    return HelperManager()


class TestDataChecker:
    """Test DataChecker class."""

    def test_validate_checker(self):
        """Test validate_checker method """
        checker = checker = {
                'name': 'Number of automatic synchronizations',
                'input_type': 'int',
                'output_type': 'float',
                'floatpoint': 0.1
        }
        assert DataChecker.validate_checker(
                key='V',
                checker=checker
            ) is True

        with pytest.raises(DeviceDataConfError):
            DataChecker.validate_checker(
                key='V',
                checker={}
            )

    def test_validate_input_value(self):
        """Test validate_input_value method """
        checker = {
                'name': 'Number of automatic synchronizations',
                'input_type': 'int',
                'output_type': 'float',
                'floatpoint': 0.1
        }
        assert DataChecker.validate_input_value(
                key='V',
                value="25525",
                checker=checker
            ) is True

        with pytest.raises(DeviceInputValueError):
            DataChecker.validate_input_value(
                key='V',
                value=25.2,
                checker=checker
            )

    def test_validate_output_value(self):
        """Test validate_output_value method """
        checker = {
                'name': 'Number of automatic synchronizations',
                'input_type': 'int',
                'output_type': 'float',
                'floatpoint': 0.1
        }
        assert DataChecker.validate_output_value(
                key='V',
                value=25.2,
                checker=checker
            ) is True

        with pytest.raises(DeviceOutputValueError):
            DataChecker.validate_output_value(
                key='V',
                value="25.2",
                checker=checker
            )

    def test_bad_checker(self, helper_manager):
        """Test check_input_columns method with bad chckers data """
        data = {'H10': '26', 'H6': '-5526739', 'H7': '11733', 'H8': '16161', 'H9': '368301'}
        local_checkers = {
            'H10': {
                'name': 'Number of automatic synchronizations',
                'floatpoint': '0.1'
            }
        }

        with pytest.raises(DeviceDataConfError):
            DataChecker.check_input_columns(
                columns=data,
                checkers=helper_manager.checkers.get('points'),
                local_checkers=local_checkers
            )

    def test_bad_floatpoint(self, helper_manager):
        """Test check_input_columns method with bad floatpoint value """
        data = {'H10': '26', 'H6': '-5526739', 'H7': '11733', 'H8': '16161', 'H9': '368301'}

        # Test bad floatpoint type error
        local_checkers = {
            'H10': {
                'name': 'Number of automatic synchronizations',
                'input_type': 'int',
                'output_type': 'float',
                'floatpoint': '0.1'
            }
        }
        with pytest.raises(DeviceDataConfError):
            DataChecker.check_input_columns(
                columns=data,
                checkers=helper_manager.checkers.get('points'),
                local_checkers=local_checkers
            )

    def test_check_input_columns(self, helper_manager):
        """Test check_input_columns method """
        data = {'H10': '26', 'H6': '-5526739', 'H7': '11733', 'H8': '16161', 'H9': '368301'}

        result = DataChecker.check_input_columns(
            columns=data,
            checkers=helper_manager.checkers.get('points')
        )
        assert Ut.is_dict(result, not_null=True) and len(data) == len(result)
        item = result.get('H10')
        assert Ut.is_int(item) and item == 26
        item = result.get('H6')
        assert Ut.is_float(item) and item == -5526.739
        item = result.get('H7')
        assert Ut.is_float(item) and item == 11.733
        item = result.get('H8')
        assert Ut.is_float(item) and item == 16.161
        item = result.get('H9')
        assert Ut.is_int(item) and item == 368301

    def test_check_input_columns_with_local_checkers(self, helper_manager):
        """Test check_input_columns method """
        data = {'H10': '26', 'H6': '-5526739', 'H7': '11733', 'H8': '16161', 'H9': '368301'}

        local_checkers = {
            'H10': {
                'name': 'Number of automatic synchronizations',
                'input_type': 'int',
                'output_type': 'float',
                'floatpoint': 0.1
            }
        }
        result = DataChecker.check_input_columns(
            columns=data,
            checkers=helper_manager.checkers.get('points'),
            local_checkers=local_checkers
        )

        assert Ut.is_dict(result, not_null=True) and len(data) == len(result)
        item = result.get('H10')
        assert Ut.is_float(item) and item == 2.6

    def test_check_output_columns(self, helper_manager):
        """Test check_output_columns method """
        data = {'H10': 26, 'H6': -5526.739, 'H7': 11.733, 'H8': 16.161, 'H9': 368301}

        result = DataChecker.check_output_columns(
            columns=data,
            checkers=helper_manager.checkers.get('points')
        )
        assert Ut.is_dict(result, not_null=True) and len(data) == len(result)
        item = result.get('H10')
        assert Ut.is_int(item) and item == 26
        item = result.get('H6')
        assert Ut.is_float(item) and item == -5526.739
        item = result.get('H7')
        assert Ut.is_float(item) and item == 11.733
        item = result.get('H8')
        assert Ut.is_float(item) and item == 16.161
        item = result.get('H9')
        assert Ut.is_int(item) and item == 368301

    def test_check_output_columns_with_local_checkers(self, helper_manager):
        """Test check_output_columns method """
        data = {'H10': 2.6, 'H6': -5526.739, 'H7': 11.733, 'H8': 16.161, 'H9': 368301}

        local_checkers = {
            'H10': {
                'name': 'Number of automatic synchronizations',
                'input_type': 'int',
                'output_type': 'float',
                'floatpoint': 0.1
            }
        }

        result = DataChecker.check_output_columns(
            columns=data,
            checkers=helper_manager.checkers.get('points'),
            local_checkers=local_checkers
        )

        assert Ut.is_dict(result, not_null=True) and len(data) == len(result)
        item = result.get('H10')
        assert Ut.is_float(item) and item == 2.6
