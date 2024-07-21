"""Test ConfigLoaderHelper class."""
import inspect
from os import path as Opath
import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import ValidationError
from vemonitor_m8.conf_manager.config_loader_helper import ConfigLoaderHelper as clh
from vemonitor_m8.conf_manager.config_loader import ConfigLoader
from vemonitor_m8.core.exceptions import SettingInvalidException


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


class TestConfigLoaderHelper:
    """Test ConfigLoaderHelper class."""

    def test_get_app_blocks_by_app_or_name(self, helper_manager):
        """Test get_app_blocks_by_app_or_name method """
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        res = clh.get_app_blocks_by_app_or_name(app_blocks=settings.app_blocks)
        assert res == settings.app_blocks

        res = clh.get_app_blocks_by_app_or_name(
            app_blocks=settings.app_blocks,
            block_name='bmvFakeSerial'
        )
        assert res == settings.app_blocks

        res = clh.get_app_blocks_by_app_or_name(
            app_blocks=settings.app_blocks,
            app_name='batSerialMonitor'
        )
        assert res == settings.app_blocks

        res = clh.get_app_blocks_by_app_or_name(
            app_blocks=settings.app_blocks,
            app_name='bad_app_name'
        )
        assert Ut.is_list(res) and len(res) == 0

        res = clh.get_app_blocks_by_app_or_name(
            app_blocks=settings.app_blocks,
            block_name='bad_block_name'
        )
        assert Ut.is_list(res) and len(res) == 0

        res = clh.get_app_blocks_by_app_or_name(app_blocks=list())
        assert res is None

    def test_get_app_blocks_by_app_or_name_errors(self):
        """Test get_app_blocks_by_app_or_name method """
        with pytest.raises(ValidationError):
            clh.get_app_blocks_by_app_or_name(app_blocks=['1', '2'])

    def test_get_args_objects_from_conf(self, helper_manager):
        """
        Test get_args_objects_from_conf method
        """
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = c_loader._get_settings_from_file()
        res = clh.get_args_objects_from_conf(
            args=settings.app_blocks[0].get('args'),
            conf=imp_conf
        )
        assert Ut.is_dict(res, not_null=True) #

        res = clh.get_args_objects_from_conf(
            args=dict(),
            conf=imp_conf
        )
        assert res is None

        res = clh.get_args_objects_from_conf(
            args=settings.app_blocks[0].get('args'),
            conf=dict()
        )
        assert res is None

    def test_get_app_blocks_args_objects(self, helper_manager):
        """Test get_app_blocks_args_objects method."""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = c_loader._get_settings_from_file()
        res = clh.get_app_blocks_args_objects(
            app_blocks=settings.app_blocks,
            conf=imp_conf
        )
        assert Ut.is_dict(res, not_null=True)

        res = clh.get_app_blocks_args_objects(
            app_blocks=settings.app_blocks,
            conf=dict()
        )
        assert res is None

        with pytest.raises(ValidationError):
            clh.get_app_blocks_args_objects(
                app_blocks=['1', '2'],
                conf=imp_conf
            )

    def test_get_app_conector_from_source(self, helper_manager):
        """Test get_app_conector_from_source method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = c_loader._get_settings_from_file()
        sources = settings.get_app_blocks_sources()
        res = clh.get_app_conector_from_source(
            conector=imp_conf.get('appConnectors').get('serial'),
            sources=sources.get('serial')
        )
        assert Ut.is_dict(res, not_null=True)

        with pytest.raises(SettingInvalidException):
            clh.get_app_conector_from_source(
                conector=imp_conf.get('appConnectors'),
                sources=sources.get('serial')
            )

        with pytest.raises(SettingInvalidException):
            clh.get_app_conector_from_source(
                conector=dict(),
                sources=sources.get('serial')
            )

        with pytest.raises(SettingInvalidException):
            clh.get_app_conector_from_source(
                conector=imp_conf.get('appConnectors'),
                sources=list()
            )

    def test_get_app_connectors_from_sources(self, helper_manager):
        """Test get_app_connectors_from_sources method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = c_loader._get_settings_from_file()
        res = clh.get_app_connectors_from_sources(
            app_conectors=imp_conf.get('appConnectors'),
            sources=settings.get_app_blocks_sources()
        )
        assert Ut.is_dict(res, not_null=True)

    def test_is_battery_banks(self, helper_manager):
        """Test is_battery_banks method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        assert clh.is_battery_banks(imp_conf.get('batteryBanks')) is True

        assert clh.is_battery_banks(dict()) is False

        assert clh.is_battery_banks({'a': 1}) is False

    def test_is_battery_banks_items(self, helper_manager):
        """Test is_battery_banks_items method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        assert clh.is_battery_banks_items(imp_conf.get('batteryBanks')) is True

    def test_is_battery_banks_items_key(self, helper_manager):
        """Test is_battery_banks_items_key method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        assert clh.is_battery_banks_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks')) is True

    def test_get_battery_banks_items_key(self, helper_manager):
        """Test get_battery_banks_items_key method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        res = clh.get_battery_banks_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks'))
        assert Ut.is_dict(res, not_null=True)

    def test_is_battery_items(self, helper_manager):
        """Test is_battery_items method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        assert clh.is_battery_items(imp_conf.get('batteryBanks')) is True

    def test_is_battery_items_key(self, helper_manager):
        """Test is_battery_items_key method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        assert clh.is_battery_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks')
        ) is True

    def test_get_battery_items_key(self, helper_manager):
        """Test get_battery_items_key method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        res = clh.get_battery_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks')
        )
        assert Ut.is_dict(res, not_null=True)

    def test_set_battery_item(self, helper_manager):
        """Test set_battery_item method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        res = clh.set_battery_item(
            key='project1',
            battery=dict(),
            battery_bank=imp_conf.get('batteryBanks')
        )
        assert Ut.is_dict(res, not_null=True)

    def test_get_battery_bank_from_arg(self, helper_manager):
        """Test get_battery_bank_from_arg method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        imp_conf = c_loader._get_settings_from_file()
        res = clh.get_battery_bank_from_arg(
            arg='project1',
            battery_bank=imp_conf.get('batteryBanks')
        )
        assert Ut.is_dict(res, not_null=True)

        with pytest.raises(ValidationError):
            clh.get_battery_bank_from_arg(
                arg='project1',
                battery_bank={'a': 1}
            )

        with pytest.raises(SettingInvalidException):
            clh.get_battery_bank_from_arg(
                arg='bad_arg',
                battery_bank=imp_conf.get('batteryBanks')
            )

    def test__is_filtered_key(self):
        """Test _is_filtered_key method"""
        res = clh._is_filtered_key(
            key='project1',
            check_keys=None
        )
        assert res is True

        res = clh._is_filtered_key(
            key='project1',
            check_keys=['project1', 'project2', 'project2']
        )
        assert res is True

        res = clh._is_filtered_key(
            key='project5',
            check_keys=['project1', 'project2', 'project2']
        )
        assert res is False

        res = clh._is_filtered_key(
            key='',
            check_keys=['project1', 'project2', 'project2']
        )
        assert res is False

    def test__check_column_keys(self):
        """Test _check_column_keys method"""
        res = clh._check_column_keys(
            data=dict()

        )
        assert Ut.is_dict(res)

        with pytest.raises(SettingInvalidException):
            clh._check_column_keys(
                data=None
            )

        with pytest.raises(SettingInvalidException):
            clh._check_column_keys(
                data={"key": 1}
            )

    def test__check_column_points(self):
        """Test _check_column_points method"""
        res = clh._check_column_points(
            data={"key": 1}
        )
        assert Ut.is_dict(res)

        with pytest.raises(SettingInvalidException):
            clh._check_column_points(
                data=None
            )

    def test_get_data_structure(self, helper_manager):
        """Test get_data_structure method"""
        c_loader = ConfigLoader(helper_manager.test_path)
        settings = c_loader.get_settings_from_schema(app_name="batSerialMonitor")
        res = clh.get_data_structure(
            data_structure=settings.data_structures
        )
        assert Ut.is_dict(res, not_null=True)

        with pytest.raises(ValidationError):
            clh.get_data_structure(
                data_structure=None
            )
