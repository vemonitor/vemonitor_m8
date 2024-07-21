"""Test ConfigLoader class."""
import inspect
from os import path as Opath
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.config_loader import ConfigLoader
from vemonitor_m8.core.exceptions import YAMLFileNotFound
from vemonitor_m8.models.config import Config
from vemonitor_m8.models.config_helper import ConfigHelper


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
            self.obj = ConfigLoader(self.test_path)

    return HelperManager()


class TestConfigLoader():
    """Test ConfigLoader class."""

    def test_set_settings_from_files(self, helper_manager):
        """Test set_settings_from_files method"""
        settings = helper_manager.obj.set_settings_from_files(
            app_name="batSerialMonitor"
        )
        assert isinstance(
            settings,
            Config
        )
        assert ConfigHelper.is_app_block(
            settings.app_blocks[0]
        ) and settings.app_blocks[0].get('app') == "batSerialMonitor"
        assert settings.has_battery_banks()

    def test_get_yaml_data_structure(self, helper_manager):
        """Test get_app_blocks_by_app_or_name method """
        assert Ut.is_dict(helper_manager.obj.get_yaml_data_structure())

        with pytest.raises(YAMLFileNotFound):
            helper_manager.obj.get_yaml_data_structure("userDeviceData.yaml")

    def test_get_settings_from_schema(self, helper_manager):
        """Test get_settings_from_schema method"""
        settings = helper_manager.obj.get_settings_from_schema(
            app_name="batSerialMonitor"
        )
        assert isinstance(
            settings,
            Config
        ) and settings.is_valid() and len(settings.app_blocks) == 1
        assert ConfigHelper.is_app_block(
            settings.app_blocks[0]
        ) and settings.app_blocks[0].get('app') == "batSerialMonitor"
        assert settings.has_battery_banks() and settings.has_data_structures()
