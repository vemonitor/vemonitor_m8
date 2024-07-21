#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Test data_structure json schema validation.
"""
import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError
from vemonitor_m8.conf_manager.schema_validate import SchemaValidate
from vemonitor_m8.conf_manager.data_structure_loader import DataStructureLoader
from .schema_test_helper import SchemaTestHelper

@pytest.fixture(name="schema_manager", scope="class")
def schema_manager_fixture():
    """Json Schema test manager fixture"""
    class SchemaManager(SchemaTestHelper):
        """Json Schema test manager fixture Class"""
        def __init__(self):
            SchemaTestHelper.__init__(self)
            self.schema = SchemaValidate.load_schema("data_structure")
            loader = DataStructureLoader(
                "vemonitor_m8/conf_manager/confFiles/victronDeviceData.yaml"
            )
            self.obj = loader.get_yaml_data_structure(
                file_path="victronDeviceData.yaml"
            )

    return SchemaManager()

class TestSchemaDataStructure:
    """
    Test data_structure json schema validation.
    ToDo: Test all patterns in jsonshema
    """

    def test_bad_file_key(self):
        """Test bad file keys"""
        # test empty dict
        with pytest.raises(SchemaError):
            SchemaValidate.load_schema("bad_key")

    def test_data_validation(self, schema_manager):
        """Test data validation"""
        data = SchemaValidate.validate_data(schema_manager.obj, "data_structure")
        assert Ut.is_dict(data, not_null=True)

    def test_datas_string_key_pattern(self, schema_manager):
        """Test bad key patterns on data"""
        datas = [
                ('input_type', schema_manager.obj['points']['V']),
                ('output_type', schema_manager.obj['points']['V'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_key")

    def test_string_column_pattern(self, schema_manager):
        """Test string_column values to validate patterns"""
        datas = [
                (0, schema_manager.obj['devices']['BMV']),
            ]
        schema_manager.run_test_values(datas = datas, key = "string_column")

    def test_datas_positive_number(self, schema_manager):
        """Test bad key patterns on data"""
        datas =  [
                ('floatpoint', schema_manager.obj['points']['V'])
            ]
        schema_manager.run_test_values(datas = datas, key = "positive_number")
