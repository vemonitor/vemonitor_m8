"""Test SchemaValidateSelector class."""
import inspect
from os import path as Opath
import pytest
from jsonschema.exceptions import ValidationError
from vemonitor_m8.conf_manager.shema_validate_selector import SchemaValidateSelector as jValid
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


class TestSchemaValidateSelector:
    """Test SchemaValidateSelector class."""
    def test_is_valid_app_blocks_conf(self, helper_manager):
        """Test is_valid_app_blocks_conf method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        res = jValid.is_valid_app_blocks_conf(conf_item=settings.app_blocks)
        assert res is True

        with pytest.raises(ValidationError):
            jValid.is_valid_app_blocks_conf(conf_item={})

        with pytest.raises(ValidationError):
            jValid.is_valid_app_blocks_conf(conf_item=None)

    def test_is_valid_app_connectors_conf(self, helper_manager):
        """Test is_valid_app_connectors_conf method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        res = jValid.is_valid_app_connectors_conf(conf_item=settings.app_connectors)
        assert res is True

        with pytest.raises(ValidationError):
            jValid.is_valid_app_connectors_conf(conf_item={})

        with pytest.raises(ValidationError):
            jValid.is_valid_app_connectors_conf(conf_item=None)

    def test_is_valid_battery_banks_conf(self, helper_manager):
        """Test is_valid_battery_banks_conf method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        res = jValid.is_valid_battery_banks_conf(conf_item=imp_conf.get('batteryBanks'))
        assert res is True

        res = jValid.is_valid_battery_banks_conf(conf_item={})
        assert res is True

        with pytest.raises(ValidationError):
            jValid.is_valid_battery_banks_conf(conf_item={'a': 1})

        with pytest.raises(ValidationError):
            jValid.is_valid_battery_banks_conf(conf_item=None)

    def test_is_valid_data_structure_conf(self, helper_manager):
        """Test is_valid_app_connectors_conf method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        res = jValid.is_valid_data_structure_conf(conf_item=settings.data_structures)
        assert res is True

        res = jValid.is_valid_data_structure_conf(conf_item={})
        assert res is True

        with pytest.raises(ValidationError):
            jValid.is_valid_data_structure_conf(conf_item={'a': 1})

        with pytest.raises(ValidationError):
            jValid.is_valid_data_structure_conf(conf_item=None)
