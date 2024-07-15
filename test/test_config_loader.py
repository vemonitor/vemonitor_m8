"""Test ConfigLoader class."""
import inspect
from os import path as Opath
import pytest
from vemonitor_m8.confManager.config_loader import ConfigLoader
from vemonitor_m8.models.settings.config import Config


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
        assert settings.is_app_block(
            settings.app_blocks[0]
        ) and settings.app_blocks[0].get('app') == "batSerialMonitor"
        assert settings.has_battery_banks()

    def test_get_settings_from_schema(self, helper_manager):
        """Test get_settings_from_schema method"""
        settings = helper_manager.obj.get_settings_from_schema(
            app_name="batSerialMonitor"
        )
        assert isinstance(
            settings,
            Config
        ) and settings.is_valid() and len(settings.app_blocks) == 1
        assert settings.is_app_block(
            settings.app_blocks[0]
        ) and settings.app_blocks[0].get('app') == "batSerialMonitor"
        assert settings.has_battery_banks() and settings.has_data_structures()
