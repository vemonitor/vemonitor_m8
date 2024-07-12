#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
from .schemaTestHelper import SchemaTestHelper
from vemonitor_m8.confManager.schemaValidate import SchemaValidate
from vemonitor_m8.confManager.loader import Loader
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError


class TestAppConnectorsSchema(SchemaTestHelper):
    
    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        self.schema = SchemaValidate._load_schema("appConnectors")
        loader = Loader("test/conf/appConnectorsTest.yaml")
        self.obj = loader.get_yaml_config()

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass
    
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
        if Ut.is_str(key) and choice in ['good', 'bad']:
            if key == "string_key":
                return self.get_string_key_values_helper(choice)
            elif key == "string_column":
                return self.get_string_columns_values_helper(choice)
            elif key == "string_text":
                return self.get_string_text_values_helper(choice)
            elif key == "string_auth":
                return self.get_string_auth_values_helper(choice)
            elif key == "string_path":
                return self.get_string_path_values_helper(choice)
            elif key == "positive_number":
                return self.get_positive_number_values_helper(choice)
            elif key == "positive_integer":
                return self.get_positive_integer_values_helper(choice)

    def test_bad_file_key(self):
        # test empty dict
        with pytest.raises(SchemaError):
            SchemaValidate._load_schema("bad_key")

    def test_data_validation(self):
        assert Ut.is_dict(
            SchemaValidate.validate_data(self.obj, "appConnectors"),
            not_null=True
        )
    
    def test_string_key_pattern(self):
        """Test string_key values to validate patterns"""
        datas = [ 
                ('onError', self.obj['serial']['bmv700']),
                ('typeTest', self.obj['serial']['bmv700']['serialTest']['PIDTest'])
            ]
        self.run_test_values(datas = datas, key = "string_key")

    def test_string_column_pattern(self):
        """Test string_column values to validate patterns"""
        datas = [ 
                ('key', self.obj['serial']['bmv700']['serialTest']['PIDTest'])
            ]
        self.run_test_values(datas = datas, key = "string_column")

    def test_string_text_pattern(self):
        """Test string_auth values to validate patterns"""
        datas = [ 
                ('value', self.obj['serial']['bmv700']['serialTest']['PIDTest'])
            ]
        self.run_test_values(datas = datas, key = "string_auth")

    def test_string_auth_pattern(self):
        """Test string_auth values to validate patterns"""
        datas = [ 
                ('auth', self.obj['redis']['local']),
                ('auth', self.obj['influxDb2']['local'])
            ]
        self.run_test_values(datas = datas, key = "string_auth")

    def test_string_path_pattern(self):
        """Test string_path values to validate patterns"""
        datas = [ 
                ('serialpath', self.obj['serial']['bmv700']),
                ('serialPort', self.obj['serial']['bmv700'])
            ]
        self.run_test_values(datas = datas, key = "string_path")


    