#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
from .schemaTestHelper import SchemaTestHelper
from vemonitor_m8.confManager.schemaValidate import SchemaValidate
from vemonitor_m8.confManager.loader import Loader
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError, ValidationError

class TestBatteryBankSchema(SchemaTestHelper):
    
    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        self.schema = SchemaValidate._load_schema("batteryBanks")
        self.obj = None

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass
    
    def load_battery_bank_conf(self, key):
        if key == "batteryDatas":
            path = "test/conf/batteryBanksTest.yaml"
        elif key == "batteryBankArgs":
            path = "test/conf/batteryBankArgsTest.yaml"
        else:
            raise ValueError(
                "Unable to load battery bank conf,"
                "invalid file key %s." %
                (key)
            )
        loader = Loader(path)
        self.obj = loader.get_yaml_config()

    def test_bad_file_key(self):
        # test empty dict
        with pytest.raises(SchemaError):
            SchemaValidate._load_schema("bad_key")

    def test_data_validation(self):
        self.load_battery_bank_conf('batteryDatas')
        assert Ut.is_dict(
            SchemaValidate.validate_data(self.obj, "batteryBanks"),
            not_null=True
        )
        
    def test_datas_string_key_pattern(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryDatas')
        datas = [ 
                ('battery_key', self.obj['batteryDatas']['bankItems']['existant']),
                ('battery_type', self.obj['batteryDatas']['bankItems']['existant']),
                ('battery_key', self.obj['batteryDatas']['bankItems']['project1']),
                ('battery_type', self.obj['batteryDatas']['bankItems']['project1'])
            ]
        self.run_test_values(datas = datas, key = "string_key")

    def test_datas_string_text_pattern(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryDatas')
        datas = [ 
                ('manufacturer', self.obj['batteryDatas']['batteries']['existant']),
                ('model', self.obj['batteryDatas']['batteries']['existant']),
                ('manufacturer', self.obj['batteryDatas']['batteries']['project1']),
                ('model', self.obj['batteryDatas']['batteries']['project1'])
            ]
        self.run_test_values(datas = datas, key = "string_text")

    def test_datas_positive_number(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryDatas')
        datas =  [
                ('cell_voltage', self.obj['batteryDatas']['batteries']['existant']),
                ('bulk_voltage', self.obj['batteryDatas']['batteries']['existant']),
                ('float_voltage', self.obj['batteryDatas']['batteries']['existant']),
                ('cell_voltage', self.obj['batteryDatas']['batteries']['project1']),
                ('bulk_voltage', self.obj['batteryDatas']['batteries']['project1']),
                ('float_voltage', self.obj['batteryDatas']['batteries']['project1']),
            ]
        self.run_test_values(datas = datas, key = "positive_number")
    
    def test_datas_positive_integer(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryDatas')
        datas =  [
                ('in_series', self.obj['batteryDatas']['bankItems']['existant']),
                ('in_parallel', self.obj['batteryDatas']['bankItems']['existant']),
                ('nb_cells', self.obj['batteryDatas']['batteries']['existant']),
                ('in_series', self.obj['batteryDatas']['bankItems']['project1']),
                ('in_parallel', self.obj['batteryDatas']['bankItems']['project1']),
                ('nb_cells', self.obj['batteryDatas']['batteries']['project1'])
            ]
        self.run_test_values(datas = datas, key = "positive_integer")

    def test_batteryBankArgs_string_key_pattern(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('name', self.obj['batteryBankArgs']),
                ('battery_type', self.obj['batteryBankArgs']),
                ('battery_key', self.obj['batteryBankArgs'])
            ]
        self.run_test_values(datas = datas, key = "string_key")
    
    def test_batteryBankArgs_string_text_pattern(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('manufacturer', self.obj['batteryBankArgs']['battery']),
                ('model', self.obj['batteryBankArgs']['battery'])
            ]
        self.run_test_values(datas = datas, key = "string_text")
    
    def test_batteryBankArgs_positive_number(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('cell_voltage', self.obj['batteryBankArgs']['battery']), 
                ('bulk_voltage', self.obj['batteryBankArgs']['battery']), 
                ('float_voltage', self.obj['batteryBankArgs']['battery']), 
                (0, self.obj['batteryBankArgs']['battery']['capacity'][0]), 
                (1, self.obj['batteryBankArgs']['battery']['capacity'][0]),
                (2, self.obj['batteryBankArgs']['battery']['capacity'][0]),  
            ]
        self.run_test_values(datas = datas, key = "positive_number")
        
    def test_batteryBankArgs_positive_integer(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryBankArgs')
        datas =  [
                ('in_series', self.obj['batteryBankArgs']),
                ('in_parallel', self.obj['batteryBankArgs']),
                ('nb_cells', self.obj['batteryBankArgs']['battery'])
            ]
        self.run_test_values(datas = datas, key = "positive_integer")

    def test_batteryBankArgs_validation(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryBankArgs')
        
        # test batteryBankArgs invalid key
        self.obj['batteryBankArgs'].update({'badkey': 'hello'})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        del self.obj['batteryBankArgs']['badkey']

        # test batteryBankArgs empty
        self.obj['batteryBankArgs'] = dict()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)

    def test_batteryBankArgs_battery(self):
        """Test bad key patterns on data"""
        self.load_battery_bank_conf('batteryBankArgs')

        # test batteryBankArgs empty
        self.obj['batteryBankArgs']['battery'] = dict()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)