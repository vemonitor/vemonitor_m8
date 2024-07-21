#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test App Blocks json schema validation."""
import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError, ValidationError
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
            self.schema = SchemaValidate.load_schema("appBlocks")
            loader = Loader("test/conf/appBlocksTest.yaml")
            self.obj = loader.get_yaml_config()

    return SchemaManager()


class TestAppBlocksSchema:
    """Test App Blocks json schema validation."""

    def test_bad_file_key(self):
        """Test bad file key"""
        # test empty dict
        with pytest.raises(SchemaError):
            SchemaValidate.load_schema("hallo")

    def test_data_validation(self, schema_manager):
        """Test data validation"""
        assert Ut.is_list(
            SchemaValidate.validate_data(schema_manager.obj, "appBlocks"),
            not_null=True
        )

    def test_string_key_pattern(self, schema_manager):
        """Test string_key values to validate patterns"""
        datas = [
                ('name', schema_manager.obj[0]),
                ('app', schema_manager.obj[0], 'bad'),
                ('batteryBanks', schema_manager.obj[0]['args']),
                ('source', schema_manager.obj[0]['inputs']['serial'][0]),
                ('device', schema_manager.obj[0]['inputs']['serial'][0]),
                ('source', schema_manager.obj[0]['outputs']['redis'][0]),
                ('redis_node', schema_manager.obj[0]['outputs']['redis'][0]),
                ('source', schema_manager.obj[0]['outputs']['influxDb2'][0]),
                ('db', schema_manager.obj[0]['outputs']['influxDb2'][0]),
                ('measurement', schema_manager.obj[0]['outputs']['influxDb2'][0]),

                ('name', schema_manager.obj[1]),
                ('app', schema_manager.obj[1], 'bad'),
                ('batteryBanks', schema_manager.obj[1]['args']),
                ('source', schema_manager.obj[1]['inputs']['redis'][0]),
                ('redis_node', schema_manager.obj[1]['inputs']['redis'][0]),
                ('source', schema_manager.obj[1]['outputs']['influxDb2'][0]),
                ('db', schema_manager.obj[1]['outputs']['influxDb2'][0]),
                ('measurement', schema_manager.obj[1]['outputs']['influxDb2'][0]),
            ]
        schema_manager.run_test_values(datas = datas, key = "string_key")

    def test_string_column_pattern(self, schema_manager):
        """Test string_column values to validate patterns"""
        datas = [
                (8, schema_manager.obj[0]['inputs']['serial'][0]['columns'])
            ]
        schema_manager.run_test_values(datas = datas, key = "string_column")

    def test_positive_number_pattern(self, schema_manager):
        """Test positive_number values to validate patterns"""
        datas = [
                ('time_interval', schema_manager.obj[0]['inputs']['serial'][0]),
                ('time_interval', schema_manager.obj[0]['outputs']['redis'][0]),
                ('time_interval', schema_manager.obj[0]['outputs']['influxDb2'][0])
            ]
        schema_manager.run_test_values(datas = datas, key = "positive_number")

    def test_block_required(self, schema_manager):
        """Test block data"""

        # test required name
        val = schema_manager.obj[0]['name']
        del schema_manager.obj[0]['name']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['name'] = val

        # test required app
        val = schema_manager.obj[0]['app']
        del schema_manager.obj[0]['app']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['app'] = val

        del schema_manager.obj[0]['args']
        del schema_manager.obj[0]['inputs']
        del schema_manager.obj[0]['outputs']

        assert Ut.is_list(
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema),
            not_null=True
        )

    def test_block_args(self, schema_manager):
        """Test block data"""
        schema_manager.init_data()
        # test block args bad key
        val = schema_manager.obj[0]['args']
        schema_manager.obj[0]['args'].update(
            {'hello': schema_manager.obj[0]['args'].get('batteryBanks')}
        )
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['args'] = val

        # test empty block args
        del schema_manager.obj[0]['args']['batteryBanks']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['args'] = val

    def test_block_inputs_outputs(self, schema_manager):
        """Test block data"""
        schema_manager.init_data()
        # test block inputs bad key
        val = schema_manager.obj[0]['inputs']
        schema_manager.obj[0]['inputs'].update(
            {'badkey': schema_manager.obj[0]['inputs'].get('serial')}
        )
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['inputs'] = val

        # test empty block inputs
        del schema_manager.obj[0]['inputs']['serial']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['inputs']['serial'] = val

        # test block outputs bad key
        val = schema_manager.obj[0]['outputs']
        schema_manager.obj[0]['outputs'].update(
            {'badkey': schema_manager.obj[0]['outputs'].get('redis')}
        )
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['outputs'] = val

        # test empty block inputs
        del schema_manager.obj[0]['outputs']['redis']
        del schema_manager.obj[0]['outputs']['influxDb2']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)

    def helper_test_time_interval(self, obj, schema_manager):
        """Helper to test time interval values"""
        # test block serial time_interval
        val = obj['time_interval']
        obj['time_interval'] = 'badInt'
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        obj['time_interval'] = val

    def helper_test_ref_cols(self, obj, schema_manager):
        """Helper to test ref cols values"""
        # test block serial empty ref_cols
        val = obj['ref_cols']
        obj['ref_cols'] = list()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        obj['ref_cols'] = val

        # test block serial empty ref_cols item
        val = obj['ref_cols'][0]
        obj['ref_cols'][0] = list()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        obj['ref_cols'][0] = val

        # test block serial ref_cols item max items
        val = obj['ref_cols'][0][0]
        obj['ref_cols'][0][0] = ['idapp', 'idcol', 'badid']
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        obj['ref_cols'][0][0] = val


    def helper_test_columns(self, obj, schema_manager):
        """Helper test columns"""
        # test block serial empty columns
        val = obj['columns']
        obj['columns'] = list()
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        obj['columns'] = val

        # test block serial unique columns
        val = obj['columns']
        if Ut.is_list(obj['columns'], not_null=True):
            obj['columns'].append('V')
        elif Ut.is_dict(obj['columns'], not_null=True):
            keys = list(obj['columns'].keys())
            key = keys[0]
            obj['columns'][key].append(obj['columns'][key][0])
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        obj['columns'] = val

    def test_block_serial(self, schema_manager):
        """Test block data"""
        schema_manager.init_data()
        # test block serial max items
        val = schema_manager.obj[0]['inputs']['serial']
        for i in range(0, 6):
            schema_manager.obj[0]['inputs']['serial'].append(val)
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['inputs']['serial'] = val

        # test block serial item bad key
        val = schema_manager.obj[0]['inputs']['serial'][0]
        schema_manager.obj[0]['inputs']['serial'][0].update({'bad_key': "hello"})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['inputs']['serial'][0] = val
        data = schema_manager.obj[0]['inputs']['serial'][0]
        self.helper_test_columns(data, schema_manager)
        self.helper_test_ref_cols(data, schema_manager)
        self.helper_test_time_interval(data, schema_manager)

    def test_block_redis(self, schema_manager):
        """Test block data"""
        schema_manager.init_data()
        # test block serial max items
        val = schema_manager.obj[0]['outputs']['redis']
        for i in range(0, 6):
            schema_manager.obj[0]['outputs']['redis'].append(val)
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['outputs']['redis'] = val

        # test block serial item bad key
        val = schema_manager.obj[0]['outputs']['redis'][0]
        schema_manager.obj[0]['outputs']['redis'][0].update({'bad_key': "hello"})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['outputs']['redis'][0] = val

        data = schema_manager.obj[0]['outputs']['redis'][0]

        self.helper_test_columns(data, schema_manager)
        self.helper_test_ref_cols(data, schema_manager)
        self.helper_test_time_interval(data, schema_manager)

    def test_block_influx_db2(self, schema_manager):
        """Test block data influx_db2"""
        schema_manager.init_data()
        # test block serial max items
        val = schema_manager.obj[0]['outputs']['influxDb2']
        for i in range(0, 6):
            schema_manager.obj[0]['outputs']['influxDb2'].append(val)
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['outputs']['influxDb2'] = val

        # test block serial item bad key
        val = schema_manager.obj[0]['outputs']['influxDb2'][0]
        schema_manager.obj[0]['outputs']['influxDb2'][0].update({'bad_key': "hello"})
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(schema_manager.obj, schema_manager.schema)
        schema_manager.obj[0]['outputs']['influxDb2'][0] = val

        data = schema_manager.obj[0]['outputs']['influxDb2'][0]

        self.helper_test_columns(data, schema_manager)
        self.helper_test_ref_cols(data, schema_manager)
        self.helper_test_time_interval(data, schema_manager)
