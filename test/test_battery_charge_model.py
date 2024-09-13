"""Test BatteryCharge models module."""
from typing import Union
from test.schema_test_helper import LoopTests
import pytest
from vemonitor_m8.core.elec_helper import ElecHelper
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.enums.elec import BaseVolt
from vemonitor_m8.models.battery_charge import ChargeCols, ChargeData, RefCols
from vemonitor_m8.models.battery_charge import ChargeSettingsModel
from vemonitor_m8.models.battery_charge import BatteryChargeHelper
from vemonitor_m8.models.battery_charge import BatteryChargeModel
from vemonitor_m8.models.battery_charge import BatteryCharge

@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager(LoopTests):
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None
            self.test_path = None
            self.loader = None

        def init_charge_settings_model(self):
            """Init BatteryDataModel object"""
            self.obj = ChargeSettingsModel(**HelperManager.get_charge_data_12v())

        def init_battery_charge_model(self):
            """Init BatteryDataModel object"""
            self.obj = BatteryChargeModel(**HelperManager.get_charge_data_12v())

        def init_battery_charge(self):
            """Init BatteryDataModel object"""
            self.obj = BatteryCharge(**HelperManager.get_charge_data_12v())

        @staticmethod
        def get_charge_data_12v():
            """Init BatteryStructureModel object"""
            return {
                RefCols.ABS_U.value: 14.1,
                RefCols.FLOAT_U.value: 13.8,
                RefCols.STORAGE_U.value: 13.2,
                RefCols.EQ_U.value: 15.9,
                RefCols.T_COEF_U.value: -16.02
            }

    return HelperManager()


class TestChargeSettingsModel:
    """Test ChargeSettingsModel model class."""
    def test_set_items(self, helper_manager):
        """Test set_absorption_u method """
        helper_manager.init_charge_settings_model()
        # Test instanse has all charge settings
        helper_manager.run_tests(
            data=helper_manager.obj.get_charge_setting_keys(),
            callback=helper_manager.obj.has_charge_setting
        )


        assert helper_manager.obj.set_charge_setting(
            key=ChargeCols.ABS_U.value,
            value=6
        ) is True
        assert helper_manager.obj.get_charge_setting(
            key=ChargeCols.ABS_U.value
        ) == 6
        assert helper_manager.obj.has_charge_setting(
            key=ChargeCols.ABS_U.value
        ) is True

        charge_items = helper_manager.obj.get_charge_setting_keys()
        callback_res = True
        def test_callback(value: Union[int, float]):
            """Test Charge settings callback"""
            result = True
            for charge_key in charge_items:
                is_set = helper_manager.obj.set_charge_setting(
                    key=charge_key,
                    value=value
                )
                if is_set is False:
                    result = False
                assert is_set is callback_res
            return result

        ok_tests = [
            0.1, 5, 1000
        ]

        helper_manager.run_tests(
            data=ok_tests,
            callback=test_callback
        )
        callback_res = False
        bad_tests = [
            -1000.1, -5, -1, 0, None, "a", 1000.1
        ]
        helper_manager.run_tests(
            data=bad_tests,
            callback=test_callback,
            is_false=True
        )

        helper_manager.obj.items = None
        assert helper_manager.obj.has_charge_setting(
            ChargeCols.ABS_U.value
        ) is False

class TestBatteryChargeHelper:
    """Test BatteryChargeHelper model class."""

    def test_get_base_u_from_charge_u_item(self, helper_manager):
        """Test get_base_u_from_charge_u_item method """
        callback_def = BaseVolt.U_12V
        def base_u_callback(charge_voltage: float):
            """Battery Base voltage callback"""
            base_u = BaseVolt.get_base_voltage_by_u_value(
                charge_voltage
            )
            return  base_u == callback_def

        ok_tests = [
            12.1, 12.2, 12.6, 12.7, 12.8, 12.9, 13.1, 16.5, 16.8
        ]
        helper_manager.run_tests(
            data=ok_tests,
            callback=base_u_callback
        )
        callback_def = 0
        bad_tests = [
            None, -1, 0, 1,
            2, 2.9, 3,
            4, 5.7, 5.9,
            6, 8.5, 9,
            12, 16.9, 20,
            24, 33.7, 45,
            48, 67.3
        ]
        helper_manager.run_tests(
            data=bad_tests,
            callback=base_u_callback
        )

    def test_get_base_u_from_charge_u(self, helper_manager):
        """Test get_base_u_from_charge_u method """
        callback_def = BaseVolt.U_12V
        def base_u_callback(absorption_u: Union[int, float],
                            float_u: Union[int, float],
                            storage_u: Union[int, float],
                            equalization_u: Union[int, float]):
            """Battery Base voltage callback"""
            base_u = BatteryChargeHelper.get_base_u_from_charge_u(
                absorption_u=absorption_u,
                float_u=float_u,
                storage_u=storage_u,
                equalization_u=equalization_u,
            )
            return  base_u == callback_def

        ok_tests = [
            {
                'absorption_u': 14.1,
                'float_u': 0,
                'storage_u': 0,
                'equalization_u': 0
            }
        ]
        helper_manager.run_tests(
            data=ok_tests,
            callback=base_u_callback,
            is_kwargs=True
        )
        callback_def = 0
        bad_tests = [
            {
                'absorption_u': 0,
                'float_u': 0,
                'storage_u': 0,
                'equalization_u': 0
            },
            {
                'absorption_u': None,
                'float_u': None,
                'storage_u': None,
                'equalization_u': None
            },
            {
                'absorption_u': 14.1,
                'float_u': 2.2,
                'storage_u': 0,
                'equalization_u': 0
            },
            {
                'absorption_u': 14.1,
                'float_u': 2.2,
                'storage_u': 6.4,
                'equalization_u': 48.5
            }
        ]
        helper_manager.run_tests(
            data=bad_tests,
            callback=base_u_callback,
            is_kwargs=True
        )

    def test_get_u_by_base(self, helper_manager):
        """Test get_u_by_base method """
        # Set up test callback function
        out_base_u = BaseVolt.U_12V
        callback_bool = True
        def base_u_callback(charge_voltage: float):
            """Battery Base voltage callback"""
            u = BatteryChargeHelper.get_u_by_base(
                value=charge_voltage,
                out_base_u=out_base_u
            )
            result = ElecHelper.is_charge_voltage(u) is callback_bool
            if callback_bool is True\
                and result is True:
                result = BaseVolt.get_base_voltage_by_u_value(u) == out_base_u
            return result
        # get list of all base_u enum members
        list_base_u = BaseVolt.get_base_voltage_values()
        # test all possible base_u values
        for member, base_u in list_base_u:
            out_base_u = member
            # Test 12v base voltage values
            ok_tests = [
                2.3, 4.6, 6.7, 15.9, 28.1, 50.2
            ]
            helper_manager.run_tests(
                data=ok_tests,
                callback=base_u_callback
            )
        # test bad charge_voltage values
        out_base_u = BaseVolt.U_2V
        callback_bool = False
        bad_tests = [
            None, -1, 0, 1,
            2, 2.9, 3,
            4, 5.7, 5.9,
            6, 8.5, 9,
            12, 16.9, 20,
            24, 33.7, 45,
            48, 67.3
        ]
        helper_manager.run_tests(
            data=bad_tests,
            callback=base_u_callback
        )


class TestBatteryChargeModel:
    """Test BatteryChargeModel model class."""
    def test_set_coef_temp(self, helper_manager):
        """Test set_coef_temp method """
        helper_manager.init_battery_charge_model()
        assert helper_manager.obj.has_coef_temp() is True

        assert helper_manager.obj.set_coef_temp() is False
        assert helper_manager.obj.set_coef_temp(6) is True
        assert helper_manager.obj.get_coef_temp() == 6
        assert helper_manager.obj.has_coef_temp() is True

        ok_tests = [
            -1000, -5, -0.1, 0.1, 5, 1000
        ]

        bad_tests = [
            0, None, "a",
            [], {}, (),
            -1000.1, 0, 1000.1
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_coef_temp
        )

        helper_manager.obj.coef_temp = 0
        assert helper_manager.obj.has_coef_temp() is False

    def test_charge_model(self, helper_manager):
        """Test charge_model methods """
        helper_manager.init_battery_charge_model()
        assert helper_manager.obj.is_ready() is True


class TestBatteryCharge:
    """Test BatteryCharge model class."""
    def test_init_u_base(self, helper_manager):
        """Test define_u_base_from_data method """
        helper_manager.init_battery_charge()
        assert helper_manager.obj.is_ready() is True
        assert helper_manager.obj.base_u == BaseVolt.U_12V

        assert helper_manager.obj.init_u_base(0) is True

        # get list of all base_u enum members
        list_base_u = BaseVolt.get_base_voltage_values()
        for member, base_u in list_base_u:
            out_base_u = member
            assert helper_manager.obj.init_u_base(
                out_base_u.value) is True
            assert helper_manager.obj.base_u == out_base_u
            assert helper_manager.obj.get_charge_settings_u_base(
            ) == out_base_u


        assert helper_manager.obj.init_u_base(BaseVolt.U_2V) is True
        assert helper_manager.obj.base_u == BaseVolt.U_2V
        assert helper_manager.obj.init_u_base(BaseVolt.U_6V) is True
        assert helper_manager.obj.base_u == BaseVolt.U_6V
        assert helper_manager.obj.init_u_base(BaseVolt.U_24V) is True
        assert helper_manager.obj.base_u == BaseVolt.U_24V

        assert helper_manager.obj.init_u_base(3) is False
        assert helper_manager.obj.init_u_base(5) is False
        assert helper_manager.obj.init_u_base(9) is False
        assert helper_manager.obj.init_u_base(18) is False

    def test_is_valid_charge_values(self, helper_manager):
        """Test is_valid_charge_values method """
        helper_manager.init_battery_charge()
        assert helper_manager.obj.is_ready() is True

        # test set_charge_settings
        # initial data is formatted as 12v format
        ok_tests = [
            # with same settings as 2v format dict props
            {
                'charge_absorption_u': 2.35,
                'charge_float_u': 2.3,
                'charge_storage_u': 2.2,
                'charge_equalization_u': 2.65,
                'charge_t_coef': -16.02
            },
            # with settings as 12v format dict props
            {
                'charge_absorption_u': 14.1,
                'charge_storage_u': 12.8
            },
            # with settings as 24v format dict props
            {
                'charge_absorption_u': 28.4,
                'charge_float_u': 27.2
            },
            # with settings as 24v format dict props
            {
                'charge_absorption_u': 49.8,
                'charge_float_u': 49.1,
                'charge_equalization_u': 52.1,
            }
        ]

        bad_tests = [
            # without any charge settings props
            {
                'battery_type': "flooded"
            },
            # without valid values
            {
                'charge_absorption_u': 0,
                'charge_float_u': 0,
                'charge_storage_u': 0,
                'charge_equalization_u': 0
            },
            # with many different base voltage
            {
                'charge_absorption_u': 14.2,
                'charge_float_u': 16.1,
                'charge_storage_u': 2.3,
                'charge_equalization_u': 18.3
            },
            # with bad values valid data must be:
            # charge_storage_u <= charge_float_u < charge_absorption_u < charge_equalization_u
            {
                'charge_absorption_u': 14.2,
                'charge_float_u': 16.1,
                'charge_storage_u': 12.3,
                'charge_equalization_u': 11.3
            },
            # with bad values valid data must be:
            # charge_absorption_u <= charge_equalization_u
            {
                'charge_equalization_u': 14.2,
                'charge_absorption_u': 16.3
            },
            # with bad values valid data must be:
            # charge_float_u <= charge_equalization_u
            {
                'charge_equalization_u': 14.2,
                'charge_float_u': 16.3
            },
            # with bad values valid data must be:
            # charge_storage_u <= charge_equalization_u
            {
                'charge_equalization_u': 14.2,
                'charge_storage_u': 16.3
            },
            # with bad values valid data must be:
            # charge_storage_u <= charge_absorption_u
            {
                'charge_absorption_u': 14.2,
                'charge_storage_u': 16.3
            },
            # with bad values valid data must be:
            # charge_float_u <= charge_absorption_u
            {
                'charge_absorption_u': 14.2,
                'charge_float_u': 16.3
            },
            # with bad values valid data must be:
            # charge_storage_u <= charge_absorption_u
            {
                'charge_float_u': 14.2,
                'charge_storage_u': 15.3
            }
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.is_valid_charge_values
        )

    def test_format_u_base_charge_settings(self, helper_manager):
        """Test format_u_base_charge_settings method """
        helper_manager.init_battery_charge()
        assert helper_manager.obj.is_ready() is True

        def test_callback(**kwargs):
            """Test Callback method"""
            conditions = None
            is_conditions, is_valid, is_same = False, False, False
            if 'conditions' in kwargs:
                conditions = kwargs.pop('conditions')
                is_conditions = Ut.is_dict(conditions, not_null=True)

            if is_conditions:
                is_valid = conditions.get('is_valid') is True
                is_same = conditions.get('is_same') is True

            formatted = BatteryCharge.format_u_base_charge_settings(
                charge_settings=kwargs.get('charge_settings'),
                base_u=kwargs.get('base_u'),
                props_flag=ChargeCols
            )

            if is_valid:
                assert BatteryCharge.is_valid_charge_values(
                    formatted,
                    ChargeCols
                )
            if is_same:
                assert formatted == Ut.get_items_from_dict(
                    kwargs.get('charge_settings'),
                    ChargeSettingsModel.get_charge_setting_keys()
                )
            return True

        # test format_u_base_charge_settings
        ok_tests = [
            # with settings as 2v format and out base_u 12v
            {
                'charge_settings':{
                    'absorption_u': 2.35,
                    'float_u': 2.3,
                    'storage_u': 2.2,
                    'equalization_u': 2.65
                },
                'base_u': BaseVolt.U_12V,
                'conditions': {
                    'is_valid': True,
                    'is_same': False
                }
            },
            # with settings as 2v format and out base_u 12v
            {
                'charge_settings':{
                    'absorption_u': 2.35,
                    'float_u': 2.3,
                    'storage_u': 2.2,
                    'equalization_u': 2.65
                },
                'base_u': 12,
                'conditions': {
                    'is_valid': True,
                    'is_same': False
                }
            },
            # with settings as 12v format and out base_u 24v
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 13.8,
                    ChargeCols.STORAGE_U.value: 13.2,
                    ChargeCols.EQ_U.value: 15.9,
                    ChargeCols.T_COEF_U.value: -16.02
                },
                'base_u': 24,
                'conditions': {
                    'is_valid': True,
                    'is_same': False
                }
            },
            # with settings as 12v format and out base_u 12v
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 13.8,
                    ChargeCols.STORAGE_U.value: 13.2,
                    ChargeCols.EQ_U.value: 15.9,
                    ChargeCols.T_COEF_U.value: -16.02
                },
                'base_u': 12,
                'conditions': {
                    'is_valid': True,
                    'is_same': True
                }
            },
            # with settings as 12v format and out base_u 24v
            # charge_settings don't have same base voltage
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 2.3,
                    ChargeCols.STORAGE_U.value: 13.2,
                    ChargeCols.EQ_U.value: 15.9,
                    ChargeCols.T_COEF_U.value: -16.02
                },
                'base_u': 24,
                'conditions': {
                    'is_valid': False,
                    'is_same': False
                }
            },
            # with settings as 12v format and out base_u 24v
            # float value is upper than absoption value
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 15.1,
                },
                'base_u': 24,
                'conditions': {
                    'is_valid': False,
                    'is_same': False
                }
            }
        ]

        helper_manager.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )

    def test_apply_temp_correction(self, helper_manager):
        """Test apply_temp_correction method """
        helper_manager.init_battery_charge()
        assert helper_manager.obj.is_ready() is True

        def test_callback(**kwargs):
            """Test Callback method"""
            conditions = None
            is_conditions, is_valid, is_same = False, False, False
            if 'conditions' in kwargs:
                conditions = kwargs.pop('conditions')
                is_conditions = Ut.is_dict(conditions, not_null=True)

            if is_conditions:
                is_valid = conditions.get('is_valid') is True
                is_same = conditions.get('is_same') is True
                is_corrected = conditions.get('is_corrected') is True

            corrected, correction = BatteryCharge.apply_temp_correction(
                **kwargs
            )

            if is_valid:
                assert BatteryCharge.is_valid_charge_values(
                    corrected,
                    ChargeCols
                )
            if is_same:
                assert corrected == Ut.get_items_from_dict(
                    kwargs.get('charge_settings'),
                    ChargeSettingsModel.get_charge_setting_keys()
                )

            if is_corrected:
                assert correction != 0

            return True

        # test set_charge_settings
        # initial data is formatted as 12v format
        ok_tests = [
            # with settings as 2v format and t_bat 45.23°C
            # correction applyed to charge_settings
            {
                'charge_settings':{
                    'absorption_u': 2.35,
                    'float_u': 2.3,
                    'storage_u': 2.2,
                    'equalization_u': 2.65
                },
                'coef_temp': -16.02,
                't_bat': 45.23,
                'conditions': {
                    'is_valid': True,
                    'is_same': False,
                    'is_corrected': True
                }
            },
            # with settings as 2v format and t_bat 25°C
            # correction not applyed to charge_settings
            {
                'charge_settings':{
                    'absorption_u': 2.35,
                    'float_u': 2.3,
                    'storage_u': 2.2,
                    'equalization_u': 2.65
                },
                'coef_temp': -16.02,
                't_bat': 25,
                'conditions': {
                    'is_valid': True,
                    'is_same': True,
                    'is_corrected': False
                }
            },
            # with settings as 12v format and t_bat -10°C
            # correction applyed to charge_settings
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 13.8,
                    ChargeCols.STORAGE_U.value: 13.2,
                    ChargeCols.EQ_U.value: 15.9,
                    ChargeCols.T_COEF_U.value: -16.02
                },
                'coef_temp': -16.02,
                't_bat': -10,
                'conditions': {
                    'is_valid': True,
                    'is_same': False,
                    'is_corrected': True
                }
            },
            # with bad settings as 12v format and t_bat -10°C
            # charge_settings don't have same base voltage
            # correction not applyed to charge_settings
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 2.3,
                    ChargeCols.STORAGE_U.value: 13.2,
                    ChargeCols.EQ_U.value: 15.9,
                    ChargeCols.T_COEF_U.value: -16.02
                },
                'coef_temp': -16.02,
                't_bat': -10,
                'conditions': {
                    'is_valid': False,
                    'is_same': False,
                    'is_corrected': False
                }
            },
            # with bad settings as 12v format and t_bat -10°C
            # float value is upper than absoption value
            # correction not applyed to charge_settings
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 15.1,
                },
                'coef_temp': -16.02,
                't_bat': -10,
                'conditions': {
                    'is_valid': False,
                    'is_same': False
                }
            }
        ]

        helper_manager.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )

    def test_get_formatted_coef_temp(self, helper_manager):
        """Test get_formatted_coef_temp method """
        helper_manager.init_battery_charge()
        assert helper_manager.obj.is_ready() is True

        def test_callback(**kwargs):
            """Test Callback method"""
            is_conditions, is_valid, has_result = False, False, False
            if 'conditions' in kwargs:
                conditions = kwargs.pop('conditions')
                is_conditions = Ut.is_dict(conditions, not_null=True)

            if is_conditions:
                is_valid = conditions.get('is_valid') is True
                has_result = 'result' in conditions

            coef_temp = BatteryCharge.get_formatted_coef_temp(
                base_u=kwargs.get('base_u'),
                coef_temp=kwargs.get('coef_temp'),
                coef_base_u=kwargs.get('coef_base_u')
            )

            if is_valid:
                assert ElecHelper.is_coef_temp(
                    coef_temp
                )
            if has_result:
                assert coef_temp == conditions.get('result')
            return True

        # test format_u_base_charge_settings
        ok_tests = [
            #
            {
                'base_u':BaseVolt.U_12V,
                'coef_temp': -16.2,
                'coef_base_u':BaseVolt.U_12V,
                'conditions': {
                    'is_valid': True,
                    'result': -16.2
                }
            },
            #
            {
                'base_u':BaseVolt.U_24V,
                'coef_temp': -16.2,
                'coef_base_u':BaseVolt.U_12V,
                'conditions': {
                    'is_valid': True,
                    'result': -32.4
                }
            },
            #
            {
                'base_u':BaseVolt.U_2V,
                'coef_temp': -16.2,
                'coef_base_u':BaseVolt.U_12V,
                'conditions': {
                    'is_valid': True,
                    'result': -2.7
                }
            }
        ]

        helper_manager.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )

    def test_detect_charge_step(self, helper_manager):
        """Test detect_charge_step method """
        helper_manager.init_battery_charge()
        assert helper_manager.obj.is_ready() is True

        def test_callback(**kwargs):
            """Test Callback method"""
            conditions = None
            is_conditions, is_valid, has_result = False, False, False
            if 'conditions' in kwargs:
                conditions = kwargs.pop('conditions')
                is_conditions = Ut.is_dict(conditions, not_null=True)

            if is_conditions:
                is_valid = conditions.get('is_valid') is True
                has_result = 'result' in conditions

            charge_step = BatteryCharge.detect_charge_step(
                **kwargs
            )

            if is_valid:
                assert isinstance(charge_step, ChargeData)
            if has_result:
                assert charge_step.serialize() == conditions.get('result')
            return True

        # test set_charge_settings
        # initial data is formatted as 12v format
        ok_tests = [
            # with settings as 2v format and t_bat 45.23°C
            # correction applyed to charge_settings
            {
                'charge_settings':{
                    'absorption_u': 14.4,
                    'float_u': 13.8,
                    'storage_u': 13.2,
                    'equalization_u': 15.9
                },
                'bat_voltage': 28.5,
                'coef_temp': -16.02,
                'coef_base_u': BaseVolt.U_12V,
                't_bat': 50,
                'conditions': {
                    'is_valid': True,
                    'result': {
                        'bat_voltage': 28.5,
                        't_bat': 50,
                        'base_u': 24, 
                        'is_temp_correction': True, 
                        'temp_correction': -0.801,
                        'compensed_charge': {
                            'absorption_u': 27.999,
                            'float_u': 26.799,
                            'storage_u': 25.599,
                            'equalization_u': 30.999
                        },
                        'current_step': {
                            'charge_step': 'equalization',
                            'index_step': 3,
                            'diff_value': -2.499,
                            'diff_percent': -10.412
                        },
                        'lower_step': {
                            'charge_step': 'absorption',
                            'index_step': 2,
                            'diff_value': 0.501,
                            'diff_percent': 2.087
                        }
                    }
                }
            },
            # with settings as 2v format and t_bat 25°C
            # correction not applyed to charge_settings
            {
                'charge_settings':{
                    'absorption_u': 14.4,
                    'float_u': 13.8,
                    'storage_u': 13.2,
                    'equalization_u': 15.9
                },
                'bat_voltage': 28.5,
                'coef_temp': -16.02,
                'coef_base_u': BaseVolt.U_12V,
                't_bat': 25,
                'conditions': {
                    'is_valid': True,
                    'result': {
                        'bat_voltage': 28.5,
                        't_bat': 25,
                        'base_u': 24, 
                        'compensed_charge': {
                            'absorption_u': 28.8,
                            'float_u': 27.6,
                            'storage_u': 26.4,
                            'equalization_u': 31.8
                        },
                        'is_temp_correction': False, 
                        'temp_correction': 0, 
                        'current_step': {
                            'charge_step': 'absorption',
                            'index_step': 2,
                            'diff_value': -0.3,
                            'diff_percent': -1.25
                        },
                        'lower_step': {
                            'charge_step': 'float',
                            'index_step': 1,
                            'diff_value': 0.9,
                            'diff_percent': 3.75
                        }
                    }
                }
            },
            # with settings as 12v format and t_bat -10°C
            # correction not applyed to charge_settings
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 13.8,
                    ChargeCols.STORAGE_U.value: 13.2,
                    ChargeCols.EQ_U.value: 15.9,
                    ChargeCols.T_COEF_U.value: -16.02
                },
                'bat_voltage': 28.5,
                'coef_temp': -16.02,
                'coef_base_u': BaseVolt.U_12V,
                't_bat': -20,
                'conditions': {
                    'is_valid': True,
                    'result': {
                        'bat_voltage': 28.5,
                        't_bat': -20,
                        'base_u': 24,
                        'compensed_charge': {
                            'absorption_u': 29.642,
                            'float_u': 29.042,
                            'storage_u': 27.842,
                            'equalization_u': 33.242
                        },
                        'is_temp_correction': True, 
                        'temp_correction': 1.442, 
                        'current_step': {
                            'charge_step': 'float',
                            'index_step': 1,
                            'diff_value': -0.542,
                            'diff_percent': -2.258
                        },
                        'lower_step': {
                            'charge_step': 'storage',
                            'index_step': 0,
                            'diff_value': 0.658,
                            'diff_percent': 2.742
                        }
                    }
                }
            },
            # with bad settings as 12v format and t_bat -10°C
            # charge_settings don't have same base voltage
            # correction not applyed to charge_settings
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 2.3,
                    ChargeCols.STORAGE_U.value: 13.2,
                    ChargeCols.EQ_U.value: 15.9,
                    ChargeCols.T_COEF_U.value: -16.02
                },
                'bat_voltage': 28.5,
                'coef_temp': -16.02,
                'coef_base_u': BaseVolt.U_12V,
                't_bat': -10,
                'conditions': {
                    'is_valid': False,
                    'is_same': False
                }
            },
            # with bad settings as 12v format and t_bat -10°C
            # float value is upper than absoption value
            # correction not applyed to charge_settings
            {
                'charge_settings':{
                    ChargeCols.ABS_U.value: 14.1,
                    ChargeCols.FLOAT_U.value: 15.1,
                },
                'bat_voltage': 28.5,
                'coef_temp': -16.02,
                'coef_base_u': BaseVolt.U_12V,
                't_bat': -10,
                'conditions': {
                    'is_valid': False,
                    'is_same': False
                }
            }
        ]

        helper_manager.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )
