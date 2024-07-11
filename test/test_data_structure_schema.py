#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
from .schemaTestHelper import SchemaTestHelper
from vemonitor_m8.confManager.schemaValidate import SchemaValidate
from vemonitor_m8.confManager.loader import Loader
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError, ValidationError

class TestColumnsChecksSchema(SchemaTestHelper):
    """ToDo: Test all patterns in jsonshema"""
    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        self.schema = SchemaValidate._load_schema("data_structure")
        loader = Loader("vemonitor_m8/confManager/confFiles/victronDeviceData.yaml")
        self.obj = loader.get_yaml_columns_check(file_path="victronDeviceData.yaml")

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

    def test_bad_file_key(self):
        # test empty dict
        with pytest.raises(SchemaError):
            SchemaValidate._load_schema("bad_key")

    def test_data_validation(self):
        data = SchemaValidate.validate_data(self.obj, "data_structure")
        assert Ut.is_dict(data, not_null=True)
        
    def test_datas_string_key_pattern(self):
        """Test bad key patterns on data"""
        datas = [ 
                ('input_type', self.obj['points']['V']),
                ('output_type', self.obj['points']['V'])
            ]
        self.run_test_values(datas = datas, key = "string_key")

    def test_string_column_pattern(self):
        """Test string_column values to validate patterns"""
        datas = [ 
                (0, self.obj['keys']['BMV'])
            ]
        self.run_test_values(datas = datas, key = "string_column")

    def test_datas_positive_number(self):
        """Test bad key patterns on data"""
        datas =  [
                ('floatpoint', self.obj['points']['V'])
            ]
        self.run_test_values(datas = datas, key = "positive_number")
    
    