"""Test config model module."""
import inspect
from os import path as Opath
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.exceptions import SettingInvalidException
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

    def test_set_app_blocks(self, helper_manager):
        """Test set_app_blocks method """
        helper_manager.init_config_with_loader()
        result = helper_manager.obj.set_app_blocks(
            app_blocks=[]
        )
        assert result is False

    def test_set_app_connectors(self, helper_manager):
        """Test set_app_connectors method """
        helper_manager.init_config_with_loader()
        result = helper_manager.obj.set_app_connectors(
            app_connectors={}
        )
        assert result is False

    def test_has_app_connector_key_item(self, helper_manager):
        """Test has_app_connector_key_item method """
        helper_manager.init_config_with_loader()
        result = helper_manager.obj.has_app_connector_key_item(
            key="redis",
            item="local"
        )
        assert result is True

    def test_get_app_connector_by_key_item(self, helper_manager):
        """Test get_app_connector_by_key_item method """
        helper_manager.init_config_with_loader()
        result = helper_manager.obj.get_app_connector_by_key_item(
            key="redis",
            item="local"
        )
        assert Ut.is_dict(result, not_null=True)
        assert result.get('host') == '127.0.0.1'
        assert result.get('port') == 6379

        result = helper_manager.obj.get_app_connector_by_key_item(
            key="bad_key",
            item="bad_item"
        )
        assert result is None

    def test_get_app_block_by_name(self, helper_manager):
        """Test get_app_block_by_name method """
        helper_manager.init_config_with_loader()
        data = helper_manager.obj.get_app_block_by_name(
            block_name="bmvFakeSerial"
        )
        assert Ut.is_dict(data, not_null=True)
        assert data.get('name') == "bmvFakeSerial"
        assert data.get('app') == 'batSerialMonitor'

    def test_get_app_block_by_app(self, helper_manager):
        """Test get_app_block_by_app method """
        helper_manager.init_config_with_loader()
        data = helper_manager.obj.get_app_block_by_app(
            app_name="batSerialMonitor"
        )
        assert Ut.is_dict(data, not_null=True)
        assert data.get('name') == "bmvFakeSerial"
        assert data.get('app') == 'batSerialMonitor'

    def test_get_app_blocks_columns(self, helper_manager):
        """Test get_app_blocks_columns method """
        helper_manager.init_config_with_loader()
        data = helper_manager.obj.get_app_blocks_columns()
        assert Ut.is_list(data, eq=23)

    def test_get_app_blocks_sources(self, helper_manager):
        """Test get_app_blocks_columns method """
        helper_manager.init_config_with_loader()
        data = helper_manager.obj.get_app_blocks_sources()
        assert Ut.is_dict(data, eq=2)
        assert data.get('serial') == ['bmv700']
        assert data.get('redis') == ['local']

    def test_get_app_connector_by_sources(self, helper_manager):
        """Test get_app_connector_by_sources method """
        helper_manager.init_config_with_loader()
        sources = helper_manager.obj.get_app_blocks_sources()
        result = helper_manager.obj.get_app_connector_by_sources(
            sources=sources
        )
        sources_keys = list(sources.keys())
        connectors_keys = list(result.keys())
        assert Ut.is_dict(result, not_null=True)
        assert sources_keys == connectors_keys
        assert Ut.is_dict(result['serial'].get('bmv700'), not_null=True)
        assert Ut.is_dict(result['redis'].get('local'), not_null=True)

    def test_reduce_app_connector_from_sources(self, helper_manager):
        """Test reduce_app_connector_from_sources method """
        helper_manager.init_config_with_loader()
        data = helper_manager.obj.reduce_app_connector_from_sources(
            app_connector=helper_manager.obj.app_connectors
        )
        assert Ut.is_dict(data, eq=2)
        assert data == helper_manager.obj.app_connectors

    def test_set_and_reduce_app_connectors(self, helper_manager):
        """Test set_and_reduce_app_connectors method """
        helper_manager.init_config_with_loader()
        result = helper_manager.obj.set_and_reduce_app_connectors(
            app_connector=helper_manager.obj.app_connectors
        )
        assert result is True

        result = helper_manager.obj.set_and_reduce_app_connectors(
            app_connector={}
        )
        assert result is False

    def test_set_data_structures(self, helper_manager):
        """Test set_data_structures method """
        helper_manager.init_config_with_loader()
        helper_manager.obj.set_data_structures(
            data_structures=helper_manager.obj.data_structures
        )

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_data_structures(
                data_structures={'a': 2}
            )

    def test_has_data_structures(self, helper_manager):
        """Test has_data_structures method """
        helper_manager.init_config_with_loader()
        assert helper_manager.obj.has_data_structures() is True

    def test_has_data_structures_point_key(self, helper_manager):
        """Test has_data_structures_point_key method """
        helper_manager.init_config_with_loader()
        assert helper_manager.obj.has_data_structures_point_key(
            key='V'
        ) is True

    def test_get_data_structures_point_by_columns(self, helper_manager):
        """Test get_data_structures_point_by_columns method """
        helper_manager.init_config_with_loader()
        columns = ['V', 'I', 'P']
        result = helper_manager.obj.get_data_structures_point_by_columns(
            columns=columns
        )
        assert Ut.is_dict(result, eq=3)
        assert Ut.is_dict(result.get('V'), not_null=True)
        assert Ut.is_dict(result.get('I'), not_null=True)
        assert Ut.is_dict(result.get('P'), not_null=True)

    def test_is_missing_data_structure(self, helper_manager):
        """Test is_missing_data_structure method """
        helper_manager.init_config_with_loader()
        columns = ['V', 'I', 'P']
        result = helper_manager.obj.is_missing_data_structure(
            data_structures=helper_manager.obj.data_structures,
            cols=columns
        )
        assert result is False

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.is_missing_data_structure(
                data_structures=helper_manager.obj.data_structures,
                cols=['V', 'bad_point']
            )

    def test_has_battery_banks(self, helper_manager):
        """Test has_battery_banks method """
        helper_manager.init_config_with_loader()
        assert helper_manager.obj.has_battery_banks() is True

    def test_validate_battery_banks(self, helper_manager):
        """Test validate_battery_banks method """
        helper_manager.init_config_with_loader()

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.validate_battery_banks(
                battery_banks={}
            )

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.validate_battery_banks(
                battery_banks={'a': 1}
            )

    def test_set_battery_banks(self, helper_manager):
        """Test set_battery_banks method """
        helper_manager.init_config_with_loader()

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_battery_banks(
                battery_banks={}
            )

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
