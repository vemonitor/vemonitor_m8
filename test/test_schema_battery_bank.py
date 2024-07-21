#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test Battery Banks json schema validation."""
import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError, ValidationError
from vemonitor_m8.conf_manager.schema_validate import SchemaValidate
from vemonitor_m8.conf_manager.loader import Loader
from .schema_test_helper import SchemaTestHelper


#schema_manager.init_data()
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
            self.schema = SchemaValidate.load_schema("batteryBanks")
            self.obj = None

        def load_battery_bank_conf(self, key):
            """Load dummy config file"""
            if key == "batteryDatas":
                path = "test/conf/batteryBanksTest.yaml"
            elif key == "batteryBankArgs":
                path = "test/conf/batteryBankArgsTest.yaml"
            else:
                raise ValueError(
                    "Unable to load battery bank conf,"
                    f"invalid file key {key}."
                )
            self.init_data()
            loader = Loader(path)
            self.obj = loader.get_yaml_config()

    return SchemaManager()


class TestBatteryBankSchema:
    """Test Battery Banks json schema validation."""

    def test_bad_file_key(self):
        """Test bad file key"""
        with pytest.raises(SchemaError):
            SchemaValidate.load_schema("bad_key")

    def test_data_validation(self, schema_manager):
        """Test data validation"""
        schema_manager.load_battery_bank_conf('batteryDatas')
        assert Ut.is_dict(
            SchemaValidate.validate_data(schema_manager.obj, "batteryBanks"),
            not_null=True
        )

    def test_datas_string_key_pattern(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryDatas')
        datas = [
                ('battery_key', schema_manager.obj['batteryDatas']['bankItems']['existant']),
                ('battery_type', schema_manager.obj['batteryDatas']['bankItems']['existant']),
                ('battery_key', schema_manager.obj['batteryDatas']['bankItems']['project1']),
                ('battery_type', schema_manager.obj['batteryDatas']['bankItems']['project1'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_key")

    def test_datas_string_text_pattern(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryDatas')
        datas = [
                ('manufacturer', schema_manager.obj['batteryDatas']['batteries']['existant']),
                ('model', schema_manager.obj['batteryDatas']['batteries']['existant']),
                ('manufacturer', schema_manager.obj['batteryDatas']['batteries']['project1']),
                ('model', schema_manager.obj['batteryDatas']['batteries']['project1'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_text")

    def test_datas_positive_number(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryDatas')
        datas =  [
                ('cell_voltage', schema_manager.obj['batteryDatas']['batteries']['existant']),
                ('bulk_voltage', schema_manager.obj['batteryDatas']['batteries']['existant']),
                ('float_voltage', schema_manager.obj['batteryDatas']['batteries']['existant']),
                ('cell_voltage', schema_manager.obj['batteryDatas']['batteries']['project1']),
                ('bulk_voltage', schema_manager.obj['batteryDatas']['batteries']['project1']),
                ('float_voltage', schema_manager.obj['batteryDatas']['batteries']['project1']),
            ]
        schema_manager.run_test_values(datas = datas, key = "positive_number")

    def test_datas_positive_integer(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryDatas')
        datas =  [
                ('in_series', schema_manager.obj['batteryDatas']['bankItems']['existant']),
                ('in_parallel', schema_manager.obj['batteryDatas']['bankItems']['existant']),
                ('nb_cells', schema_manager.obj['batteryDatas']['batteries']['existant']),
                ('in_series', schema_manager.obj['batteryDatas']['bankItems']['project1']),
                ('in_parallel', schema_manager.obj['batteryDatas']['bankItems']['project1']),
                ('nb_cells', schema_manager.obj['batteryDatas']['batteries']['project1'])
            ]
        schema_manager.run_test_values(datas = datas, key = "positive_integer")

    def test_battery_bank_args_string_key_pattern(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('name', schema_manager.obj['batteryBankArgs']),
                ('battery_type', schema_manager.obj['batteryBankArgs']),
                ('battery_key', schema_manager.obj['batteryBankArgs'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_key")

    def test_battery_bank_args_string_text_pattern(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('manufacturer', schema_manager.obj['batteryBankArgs']['battery']),
                ('model', schema_manager.obj['batteryBankArgs']['battery'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_text")

    def test_battery_bank_args_positive_number(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('cell_voltage', schema_manager.obj['batteryBankArgs']['battery']),
                ('bulk_voltage', schema_manager.obj['batteryBankArgs']['battery']),
                ('float_voltage', schema_manager.obj['batteryBankArgs']['battery']),
                # (0, schema_manager.obj['batteryBankArgs']['battery']['capacity'][0]),
                # (1, schema_manager.obj['batteryBankArgs']['battery']['capacity'][0]),
                # (2, schema_manager.obj['batteryBankArgs']['battery']['capacity'][0]),
            ]
        schema_manager.run_test_values(datas = datas, key = "positive_number")

    def test_battery_bank_args_positive_integer(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('in_series', schema_manager.obj['batteryBankArgs']),
                ('in_parallel', schema_manager.obj['batteryBankArgs']),
                ('nb_cells', schema_manager.obj['batteryBankArgs']['battery'])
            ]
        schema_manager.run_test_values(datas = datas, key = "positive_integer")

    def test_battery_bank_args_validation(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryBankArgs')

        # test batteryBankArgs invalid key
        schema_manager.obj['batteryBankArgs'].update({'badkey': 'hello'})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        del schema_manager.obj['batteryBankArgs']['badkey']

        # test batteryBankArgs empty
        schema_manager.obj['batteryBankArgs'] = dict()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)

    def test_battery_bank_args_battery(self, schema_manager):
        """Test bad key patterns on data"""
        schema_manager.load_battery_bank_conf('batteryBankArgs')

        # test batteryBankArgs empty
        schema_manager.obj['batteryBankArgs']['battery'] = dict()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
