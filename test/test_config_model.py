"""Test config model module."""
import inspect
from os import path as Opath
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.models.config import Config
from vemonitor_m8.conf_manager.config_loader import ConfigLoader


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = Config()
            self.test_path = None
            self.loader = None

        def init_loader(self):
            """Init config loader module"""
            current_script_path = Opath.dirname(
                Opath.abspath(
                    inspect.getfile(inspect.currentframe())
                )
            )
            self.test_path = Opath.join(
                current_script_path,
                "conf"
            )
            self.loader = ConfigLoader(self.test_path)

        def init_config_with_loader(self):
            """Init config loader module"""
            self.init_loader()
            settings = self.loader.get_settings_from_schema(
                app_name="batSerialMonitor"
            )
            self.obj = settings

    return HelperManager()


class TestConfig:
    """Test Config model class."""

    def test_is_valid(self, helper_manager):
        """Test is_valid method """
        assert helper_manager.obj.is_valid() is False
        helper_manager.init_config_with_loader()
        assert helper_manager.obj.is_valid() is True

    def test___str__(self, helper_manager):
        """Test __str__ method """
        helper_manager.init_config_with_loader()
        data = str(helper_manager.obj)
        assert Ut.is_str(data, not_null=True)

    def test_serialize(self, helper_manager):
        """Test serialize method """
        helper_manager.init_config_with_loader()
        data = helper_manager.obj.serialize()
        assert Ut.is_dict(data, eq=5)
