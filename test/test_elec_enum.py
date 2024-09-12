"""Test Electricity Enum's module."""
from test.schema_test_helper import LoopTests
import pytest
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.enums.core import BaseFlag
from vemonitor_m8.enums.elec import BaseVolt
from vemonitor_m8.enums.elec import ChargeCols
from vemonitor_m8.enums.elec import EChargeStep
from vemonitor_m8.enums.elec import ElecEnums

@pytest.fixture(name="hm", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager(LoopTests):
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None

    return HelperManager()


class TestBaseVolt:
    """Test BaseVolt Enum."""
    def test_is_member(self, hm):
        """Test is_member method """

        ok_tests = [
            BaseVolt.U_2V,
            BaseVolt.U_4V,
            BaseVolt.U_6V,
            BaseVolt.U_12V,
            BaseVolt.U_24V,
            BaseVolt.U_48V
        ]

        bad_tests = [
            None,
            2,
            -1,
            0,
            'a',
            [],
            ()
        ]
        hm.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=BaseVolt.is_member
        )

    def test_get_default(self):
        """Test get_default method """
        assert BaseVolt.get_default() == BaseVolt.U_2V

    def test_get_default_value(self):
        """Test get_default_value method """
        assert BaseVolt.get_default_value() == 2

    def test_get_base_voltage_values(self):
        """Test get_default_value method """
        assert Ut.is_list(BaseVolt.get_base_voltage_values(), not_null=True)

    def test_get_base_voltage_by_value(self, hm):
        """Test get_base_voltage_by_value method """

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

            result = BaseVolt.get_base_voltage_by_value(
                **kwargs
            )

            if is_valid:
                assert BaseVolt.is_member(result)
            if has_result:
                assert result == conditions.get('result')
            return True

        ok_tests = [
            {
                'value': 2,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_2V
                }
            },
            {
                'value': 4,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_4V
                }
            },
            {
                'value': 6,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_6V
                }
            },
            {
                'value': 12,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_12V
                }
            },
            {
                'value': 24,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_24V
                }
            },
            {
                'value': 48,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_48V
                }
            },
            {
                'value': 0,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'value': None,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'value': 3,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'value': 7,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            }
        ]

        hm.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )

    def test_get_base_voltage_by_u_value(self, hm):
        """Test get_base_voltage_by_u_value method """

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

            result = BaseVolt.get_base_voltage_by_u_value(
                **kwargs
            )

            if is_valid:
                assert BaseVolt.is_member(result)
            if has_result:
                assert result == conditions.get('result')
            return True

        ok_tests = [
            {
                'charge_voltage': 2.800,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_2V
                }
            },
            {
                'charge_voltage': 2.801,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 5.600,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_4V
                }
            },
            {
                'charge_voltage': 5.601,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 8.400,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_6V
                }
            },
            {
                'charge_voltage': 8.401,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 16.8,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_12V
                }
            },
            {
                'charge_voltage': 16.801,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 33.600,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_24V
                }
            },
            {
                'charge_voltage': 33.601,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 67.200,
                'conditions': {
                    'is_valid': True,
                    'result': BaseVolt.U_48V
                }
            },
            {
                'charge_voltage': 67.201,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 0,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': None,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 3,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            },
            {
                'charge_voltage': 9,
                'conditions': {
                    'is_valid': False,
                    'result': 0
                }
            }
        ]

        hm.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )


class TestElecEnums:
    """Test ElecEnums Helper."""
    def test_get_related_charge_cols(self, hm):
        """Test get_related_charge_cols method """
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

            result = ElecEnums.get_related_charge_cols(
                **kwargs
            )

            if is_valid:
                assert ChargeCols.is_member(result)
            if has_result:
                assert result == conditions.get('result')
            return True

        ok_tests = [
            {
                'member': EChargeStep.ABSORPTION,
                'conditions': {
                    'is_valid': True,
                    'result': ChargeCols.ABS_U
                }
            },
            {
                'member': EChargeStep.FLOAT,
                'conditions': {
                    'is_valid': True,
                    'result': ChargeCols.FLOAT_U
                }
            },
            {
                'member': EChargeStep.STORAGE,
                'conditions': {
                    'is_valid': True,
                    'result': ChargeCols.STORAGE_U
                }
            },
            {
                'member': EChargeStep.EQUALIZATION,
                'conditions': {
                    'is_valid': True,
                    'result': ChargeCols.EQ_U
                }
            },
            {
                'member': 0,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            },
            {
                'member': None,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            },
            {
                'member': EChargeStep,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            },
            {
                'member': BaseFlag,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            }
        ]

        hm.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )

    def test_get_related_charge_step(self, hm):
        """Test get_related_charge_step method """
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

            result = ElecEnums.get_related_charge_step(
                **kwargs
            )

            if is_valid:
                assert EChargeStep.is_member(result)
            if has_result:
                assert result == conditions.get('result')
            return True

        ok_tests = [
            {
                'member': ChargeCols.ABS_U,
                'conditions': {
                    'is_valid': True,
                    'result': EChargeStep.ABSORPTION
                }
            },
            {
                'member': ChargeCols.FLOAT_U,
                'conditions': {
                    'is_valid': True,
                    'result': EChargeStep.FLOAT
                }
            },
            {
                'member': ChargeCols.STORAGE_U,
                'conditions': {
                    'is_valid': True,
                    'result': EChargeStep.STORAGE
                }
            },
            {
                'member': ChargeCols.EQ_U,
                'conditions': {
                    'is_valid': True,
                    'result': EChargeStep.EQUALIZATION
                }
            },
            {
                'member': 0,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            },
            {
                'member': None,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            },
            {
                'member': EChargeStep,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            },
            {
                'member': ChargeCols,
                'conditions': {
                    'is_valid': False,
                    'result': None
                }
            }
        ]

        hm.run_tests(
            data=ok_tests,
            callback=test_callback,
            is_kwargs=True
        )
