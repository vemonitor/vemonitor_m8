#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
from .schemaTestHelper import SchemaTestHelper
from vemonitor_m8.confManager.schemaValidate import SchemaValidate
from vemonitor_m8.confManager.loader import Loader
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError, ValidationError

class TestAppBlocksSchema(SchemaTestHelper):
    
    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        self.schema = SchemaValidate._load_schema("appBlocks")
        loader = Loader("test/conf/appBlocksTest.yaml")
        self.obj = loader.get_yaml_config()
        
        

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass
    
    def test_bad_file_key(self):
        # test empty dict
        with pytest.raises(SchemaError):
            SchemaValidate._load_schema("hallo")

    def test_data_validation(self):
        assert Ut.is_list(
            SchemaValidate.validate_data(self.obj, "appBlocks"),
            not_null=True
        )
    
    def test_string_key_pattern(self):
        """Test string_key values to validate patterns"""
        datas = [ 
                ('name', self.obj[0]),
                ('app', self.obj[0], 'bad'),
                ('batteryBanks', self.obj[0]['args']),
                ('source', self.obj[0]['inputs']['serial'][0]),
                ('material', self.obj[0]['inputs']['serial'][0]),
                ('source', self.obj[0]['outputs']['redis'][0]),
                ('redis_node', self.obj[0]['outputs']['redis'][0]),
                ('source', self.obj[0]['outputs']['influxDb2'][0]),
                ('db', self.obj[0]['outputs']['influxDb2'][0]),
                ('mesurement', self.obj[0]['outputs']['influxDb2'][0]),

                ('name', self.obj[1]),
                ('app', self.obj[1], 'bad'),
                ('batteryBanks', self.obj[1]['args']),
                ('source', self.obj[1]['inputs']['redis'][0]),
                ('redis_node', self.obj[1]['inputs']['redis'][0]),
                ('source', self.obj[1]['outputs']['influxDb2'][0]),
                ('db', self.obj[1]['outputs']['influxDb2'][0]),
                ('mesurement', self.obj[1]['outputs']['influxDb2'][0]),
            ]
        self.run_test_values(datas = datas, key = "string_key")
            
    def test_string_column_pattern(self):
        """Test string_column values to validate patterns"""
        datas = [ 
                (8, self.obj[0]['inputs']['serial'][0]['columns'])
            ]
        self.run_test_values(datas = datas, key = "string_column")
    
    def test_positive_integer_pattern(self):
        """Test positive_integer values to validate patterns"""
        datas = [ 
                ('time_interval', self.obj[0]['inputs']['serial'][0]),
                ('time_interval', self.obj[0]['outputs']['redis'][0]),
                ('time_interval', self.obj[0]['outputs']['influxDb2'][0])
            ]
        self.run_test_values(datas = datas, key = "positive_integer")

    def test_block_required(self):
        """Test block data"""

        # test required name
        val = self.obj[0]['name']
        del self.obj[0]['name']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['name'] = val

        # test required app
        val = self.obj[0]['app']
        del self.obj[0]['app']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['app'] = val

        del self.obj[0]['args']
        del self.obj[0]['inputs']
        del self.obj[0]['outputs']

        assert Ut.is_list(
            SchemaValidate.validate_data_from_schema(self.obj, self.schema),
            not_null=True
        )
    
    def test_block_args(self):
        """Test block data"""
        # test block args bad key
        val = self.obj[0]['args']
        self.obj[0]['args'].update({'hello': self.obj[0]['args'].get('batteryBanks')})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['args'] = val

        # test empty block args
        del self.obj[0]['args']['batteryBanks']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['args'] = val
    
    def test_block_inputs_outputs(self):
        """Test block data"""
        # test block inputs bad key
        val = self.obj[0]['inputs']
        self.obj[0]['inputs'].update({'badkey': self.obj[0]['inputs'].get('serial')})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['inputs'] = val

        # test empty block inputs
        del self.obj[0]['inputs']['serial']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['inputs']['serial'] = val

        # test block outputs bad key
        val = self.obj[0]['outputs']
        self.obj[0]['outputs'].update({'badkey': self.obj[0]['outputs'].get('redis')})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['outputs'] = val

        # test empty block inputs
        del self.obj[0]['outputs']['redis']
        del self.obj[0]['outputs']['influxDb2']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)

    def helper_test_time_interval(self, obj):
        # test block serial time_interval
        val = obj['time_interval']
        obj['time_interval'] = 'badInt'
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        obj['time_interval'] = val

    def helper_test_ref_cols(self, obj):
        # test block serial empty ref_cols
        val = obj['ref_cols']
        obj['ref_cols'] = list()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        obj['ref_cols'] = val

        # test block serial empty ref_cols item
        val = obj['ref_cols'][0]
        obj['ref_cols'][0] = list()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        obj['ref_cols'][0] = val

        # test block serial ref_cols item max items
        val = obj['ref_cols'][0][0]
        obj['ref_cols'][0][0] = ['idapp', 'idcol', 'badid']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        obj['ref_cols'][0][0] = val


    def helper_test_columns(self, obj):
        # test block serial empty columns
        val = obj['columns']
        obj['columns'] = list()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        obj['columns'] = val

        # test block serial unique columns
        val = obj['columns']
        obj['columns'].append('V')
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        obj['columns'] = val

    def test_block_serial(self):
        """Test block data"""
        # test block serial max items
        val = self.obj[0]['inputs']['serial']
        for i in range(0, 6):
            self.obj[0]['inputs']['serial'].append(val)
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['inputs']['serial'] = val

        # test block serial item bad key
        val = self.obj[0]['inputs']['serial'][0]
        self.obj[0]['inputs']['serial'][0].update({'bad_key': "hello"})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['inputs']['serial'][0] = val

        self.helper_test_columns(self.obj[0]['inputs']['serial'][0])
        self.helper_test_ref_cols(self.obj[0]['inputs']['serial'][0])
        self.helper_test_time_interval(self.obj[0]['inputs']['serial'][0])

    def test_block_redis(self):
        """Test block data"""
        # test block serial max items
        val = self.obj[0]['outputs']['redis']
        for i in range(0, 6):
            self.obj[0]['outputs']['redis'].append(val)
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['outputs']['redis'] = val

        # test block serial item bad key
        val = self.obj[0]['outputs']['redis'][0]
        self.obj[0]['outputs']['redis'][0].update({'bad_key': "hello"})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['outputs']['redis'][0] = val

        self.helper_test_columns(self.obj[0]['outputs']['redis'][0])
        self.helper_test_ref_cols(self.obj[0]['outputs']['redis'][0])
        self.helper_test_time_interval(self.obj[0]['outputs']['redis'][0])
    
    def test_block_influxDb2(self):
        """Test block data"""
        # test block serial max items
        val = self.obj[0]['outputs']['influxDb2']
        for i in range(0, 6):
            self.obj[0]['outputs']['influxDb2'].append(val)
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['outputs']['influxDb2'] = val

        # test block serial item bad key
        val = self.obj[0]['outputs']['influxDb2'][0]
        self.obj[0]['outputs']['influxDb2'][0].update({'bad_key': "hello"})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        self.obj[0]['outputs']['influxDb2'][0] = val

        self.helper_test_columns(self.obj[0]['outputs']['influxDb2'][0])
        self.helper_test_ref_cols(self.obj[0]['outputs']['influxDb2'][0])
        self.helper_test_time_interval(self.obj[0]['outputs']['influxDb2'][0])

        

        

        
        