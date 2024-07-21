"""Test SchemaValidate class."""
import inspect
from os import path as Opath
import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError
from vemonitor_m8.conf_manager.shema_validate_selector import SchemaValidate as jValid
from vemonitor_m8.conf_manager.config_loader import ConfigLoader


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


class TestSchemaValidate:
    """Test SchemaValidate class."""

    def test_validate_data(self, helper_manager):
        """Test validate_data method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        res = jValid.validate_data(data=settings.app_blocks, shem_key_path='appBlocks')
        assert Ut.is_list(res, not_null=True)

        with pytest.raises(SchemaError):
            jValid.validate_data(data=settings.app_blocks, shem_key_path='bad_schema_key')

    def test_validate_data_from_schema(self, helper_manager):
        """Test validate_data_from_schema method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        schema = jValid.load_schema('appBlocks')
        res = jValid.validate_data_from_schema(data=settings.app_blocks, schema=schema)
        assert Ut.is_list(res, not_null=True)

        with pytest.raises(SchemaError):
            jValid.validate_data_from_schema(data=settings.app_blocks, schema={})

    def test_load_schema(self):
        """Test load_schema method"""
        schema = jValid.load_schema('appBlocks')
        assert Ut.is_dict(schema, not_null=True)

        with pytest.raises(SchemaError):
            jValid.load_schema('')
