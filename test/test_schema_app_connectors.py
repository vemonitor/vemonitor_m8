#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test App Connectors json schema validation."""

import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError
from vemonitor_m8.conf_manager.schema_validate import SchemaValidate
from vemonitor_m8.conf_manager.loader import Loader
from .schema_test_helper import SchemaTestHelper



@pytest.fixture(name="schema_manager", scope="class")
def schema_manager_fixture():
    """Json Schema test manager fixture"""
    class SchemaManager(SchemaTestHelper):
        """Json Schema test manager fixture Class"""
        def __init__(self):
            SchemaTestHelper.__init__(self)
            self.init_data()

        def init_data(self):
            """Init data"""
            self.schema = SchemaValidate.load_schema("appConnectors")
            loader = Loader("test/conf/appConnectorsTest.yaml")
            self.obj = loader.get_yaml_config()

        def get_string_auth_values_helper(self, choice: str) -> list:
            """
            Return a list of string_auth values to test jsonschema validation.

            The function returns different lists depending on the choice parameter,
            which is either good or bad.
            If choice is set to good,
            then strings that are expected to be valid will be returned.
            If choice is set to bad,
            then strings that are expected not to be valid will be returned
            :param self: Allow a function to refer to itself
            :param choice: Determine which list of values to return
            :return: A list of values that are bad or good string_auth.
            """
            if choice == "good":
                return["hello", "HeLlO", "H1eL2lO", "0H1e/L2lO.dev", "0H1e_L2lO#@/.-+"]
            else:
                return[0, -1, -0.1, 0.1, 2.2, "_hel lo",
                    False, None, dict(), tuple()
                    ]

        def get_string_path_values_helper(self, choice: str) -> list:
            """
            Return a list of string_path values to test jsonschema validation.

            The function returns different lists depending on the choice parameter,
            which is either good or bad.
            If choice is set to good,
            then strings that are expected to be valid will be returned.
            If choice is set to bad,
            then strings that are expected not to be valid will be returned.

            :param self: Allow a function to refer to itself
            :param choice: Determine which list of values to return
            :return: A list of values that are bad or good string_path
            """
            if choice == "good":
                return["hello", "HeLlO", "H1eL2lO", "0H1e/L2lO.dev", "0H1e_L2lO"]
            else:
                return[0, -1, -0.1, 0.1, 2.2, "_hel lo",
                    False, None, dict(), tuple()
                    ]

        def get_values_helper(self, key: str, choice: str) -> list:
            """
            Return a list of values to test json schema validation.

            Accepts two parameters, key and choice.
            - 'key' is a string that specifies the type of value to be returned.
            - 'choice' is also a string that specifies whether
                to return good or bad values for the specified key.

            :param self: Access variables that belongs to the class
            :param key: Determine which type of values to return
            :param choice: Determine which values to return
            :return: A list of values for the given key and choice
            :doc-author: Trelent
            """
            result = None
            if Ut.is_str(key) and choice in ['good', 'bad']:
                if key == "string_key":
                    result = self.get_string_key_values_helper(choice)
                elif key == "string_column":
                    result = self.get_string_columns_values_helper(choice)
                elif key == "string_text":
                    result = self.get_string_text_values_helper(choice)
                elif key == "string_auth":
                    result = self.get_string_auth_values_helper(choice)
                elif key == "string_path":
                    result = self.get_string_path_values_helper(choice)
                elif key == "positive_number":
                    result = self.get_positive_number_values_helper(choice)
                elif key == "positive_integer":
                    result = self.get_positive_integer_values_helper(choice)
            return result

    return SchemaManager()


class TestAppConnectorsSchema:
    """Test App Connectors json schema validation."""

    def test_bad_file_key(self):
        """Test bad file key"""
        with pytest.raises(SchemaError):
            SchemaValidate.load_schema("bad_key")

    def test_data_validation(self, schema_manager):
        """Test data validation"""
        assert Ut.is_dict(
            SchemaValidate.validate_data(schema_manager.obj, "appConnectors"),
            not_null=True
        )

    def test_string_key_pattern(self, schema_manager):
        """Test string_key values to validate patterns"""
        datas = [
                ('onError', schema_manager.obj['serial']['bmv700']),
                ('typeTest', schema_manager.obj['serial']['bmv700']['serialTest']['PIDTest'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_key")

    def test_string_column_pattern(self, schema_manager):
        """Test string_column values to validate patterns"""
        datas = [
                ('key', schema_manager.obj['serial']['bmv700']['serialTest']['PIDTest'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_column")

    def test_string_text_pattern(self, schema_manager):
        """Test string_auth values to validate patterns"""
        datas = [
                ('value', schema_manager.obj['serial']['bmv700']['serialTest']['PIDTest'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_auth")

    def test_string_auth_pattern(self, schema_manager):
        """Test string_auth values to validate patterns"""
        datas = [
                ('password', schema_manager.obj['redis']['local']),
                ('auth', schema_manager.obj['influxDb2']['local'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_auth")

    def test_string_path_pattern(self, schema_manager):
        """Test string_path values to validate patterns"""
        datas = [
                ('serialPort', schema_manager.obj['serial']['bmv700'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_path")
