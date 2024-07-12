import pytest
import inspect
from os import path as Opath
from ve_utils.utype import UType as Ut
from vemonitor_m8.confManager.configLoaderHelper import ConfigLoaderHelper as clh
from vemonitor_m8.confManager.configLoader import ConfigLoader
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError

from vemonitor_m8.core.exceptions import NullSettingException, SettingInvalidException


class TestConfigLoaderHelper:

    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        current_script_path = Opath.dirname(
            Opath.abspath(
                inspect.getfile(inspect.currentframe())
            )
        )
        self.test_path = Opath.join(
            current_script_path,
            "conf"
        )

    def test_is_jsonschema_validated(self):
        cLoader = ConfigLoader(self.test_path)
        settings = cLoader.get_settings_from_schema(app_name="batSerialMonitor")
        res = clh.is_jsonschema_validated(key="appConnectors", conf_item=settings.app_connectors)
        assert res is True

    def test_is_jsonschema_validated_errors(self):
        # test empty dict
        with pytest.raises(SchemaError):
            clh.is_jsonschema_validated(key="bad_key", conf_item=dict())

    def test_get_app_blocks_by_app_or_name(self):
        cLoader = ConfigLoader(self.test_path)
        settings = cLoader.get_settings_from_schema(app_name="batSerialMonitor")
        res = clh.get_app_blocks_by_app_or_name(app_blocks=settings.app_blocks)
        assert res == settings.app_blocks

        res = clh.get_app_blocks_by_app_or_name(app_blocks=settings.app_blocks, block_name='bmvFakeSerial')
        assert res == settings.app_blocks

        res = clh.get_app_blocks_by_app_or_name(app_blocks=settings.app_blocks, app_name='batSerialMonitor')
        assert res == settings.app_blocks

        res = clh.get_app_blocks_by_app_or_name(app_blocks=settings.app_blocks, app_name='bad_app_name')
        assert Ut.is_list(res) and len(res) == 0

        res = clh.get_app_blocks_by_app_or_name(app_blocks=settings.app_blocks, block_name='bad_block_name')
        assert Ut.is_list(res) and len(res) == 0

        res = clh.get_app_blocks_by_app_or_name(app_blocks=list())
        assert res is None

    def test_get_app_blocks_by_app_or_name_errors(self):
        # test empty dict
        with pytest.raises(ValidationError):
            clh.get_app_blocks_by_app_or_name(app_blocks=['1', '2'])

    def test_get_args_objects_from_conf(self):
        """
        Test get_args_objects_from_conf method
        """
        cLoader = ConfigLoader(self.test_path)
        settings = cLoader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = cLoader._get_settings_from_file()
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

    def test_get_app_blocks_args_objects(self):
        cLoader = ConfigLoader(self.test_path)
        settings = cLoader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = cLoader._get_settings_from_file()
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

    def test_get_app_conector_from_source(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        settings = cLoader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = cLoader._get_settings_from_file()
        sources = settings.get_app_blocks_sources()
        res = clh.get_app_conector_from_source(
            key='serial',
            conector=imp_conf.get('appConnectors').get('serial'),
            sources=sources.get('serial')
        )
        assert Ut.is_dict(res, not_null=True)

        with pytest.raises(SettingInvalidException):
            clh.get_app_conector_from_source(
                key='serial',
                conector=imp_conf.get('appConnectors'),
                sources=sources.get('serial')
            )

        with pytest.raises(SettingInvalidException):
            clh.get_app_conector_from_source(
                key='serial',
                conector=dict(),
                sources=sources.get('serial')
            )
        
        with pytest.raises(SettingInvalidException):
            clh.get_app_conector_from_source(
                key='serial',
                conector=imp_conf.get('appConnectors'),
                sources=list()
            )
    
    def test_get_app_connectors_from_sources(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        settings = cLoader.get_settings_from_schema(app_name="batSerialMonitor")
        imp_conf = cLoader._get_settings_from_file()
        res = clh.get_app_connectors_from_sources(
            app_conectors=imp_conf.get('appConnectors'),
            sources=settings.get_app_blocks_sources()
        )
        assert Ut.is_dict(res, not_null=True)

    def test_is_battery_banks(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        assert clh.is_battery_banks(imp_conf.get('batteryBanks')) is True

        assert clh.is_battery_banks(dict()) is False

        assert clh.is_battery_banks({'a': 1}) is False
    
    def test_is_battery_banks_items(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        assert clh.is_battery_banks_items(imp_conf.get('batteryBanks')) is True
    
    def test_is_battery_banks_items_key(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        assert clh.is_battery_banks_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks')) is True
    
    def test_get_battery_banks_items_key(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        res = clh.get_battery_banks_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks'))
        assert Ut.is_dict(res, not_null=True)
    
    def test_is_battery_items(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        assert clh.is_battery_items(imp_conf.get('batteryBanks')) is True
    
    def test_is_battery_items_key(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        assert clh.is_battery_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks')
        
        ) is True
    
    def test_get_battery_items_key(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        res = clh.get_battery_items_key(
            key='project1',
            battery_bank=imp_conf.get('batteryBanks')
        
        )
        assert Ut.is_dict(res, not_null=True)
    
    def test_set_battery_item(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        res = clh.set_battery_item(
            key='project1',
            battery=dict(),
            battery_bank=imp_conf.get('batteryBanks')
        
        )
        assert Ut.is_dict(res, not_null=True)

    def test_get_battery_bank_from_arg(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        res = clh.get_battery_bank_from_arg(
            key='batteryBanks',
            arg='project1',
            battery_bank=imp_conf.get('batteryBanks')
        
        )
        assert Ut.is_dict(res, not_null=True)

        with pytest.raises(SettingInvalidException):
            clh.get_battery_bank_from_arg(
                key='bad_key',
                arg='project1',
                battery_bank=imp_conf.get('batteryBanks')
            
            )

        with pytest.raises(SettingInvalidException):
            clh.get_battery_bank_from_arg(
                key='batteryBanks',
                arg='project1',
                battery_bank={'a': 1}
            
            )
        
        with pytest.raises(SettingInvalidException):
            clh.get_battery_bank_from_arg(
                key='batteryBanks',
                arg='bad_arg',
                battery_bank=imp_conf.get('batteryBanks')
            
            )

    def test__is_filtered_key(self):
        """"""
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
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
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
        """"""
        cLoader = ConfigLoader(self.test_path)
        imp_conf = cLoader._get_settings_from_file()
        res = clh._check_column_points(
            data={"key": 1}
        
        )
        assert Ut.is_dict(res)

        with pytest.raises(SettingInvalidException):
            clh._check_column_points(
                data=None
            )

    def test_get_columns_check(self):
        """"""
        cLoader = ConfigLoader(self.test_path)
        settings = cLoader.get_settings_from_schema(app_name="batSerialMonitor")
        res = clh.get_columns_check(
            columns_check=settings.columns_checks        
        )
        assert Ut.is_dict(res, not_null=True)

        with pytest.raises(ValidationError):
            clh.get_columns_check(
                columns_check=None
            )
