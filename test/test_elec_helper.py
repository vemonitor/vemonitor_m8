"""Test ElecHelper model class."""
from test.schema_test_helper import LoopTests
import pytest
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.core.elec_helper import ElecHelper

@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager(LoopTests):
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None

    return HelperManager()


class TestElecHelper:
    """Test ElecHelper model class."""
    def test_is_coef_temp(self, helper_manager):
        """Test is_coef_temp method """
        ok_tests = [
            -1000, -5, -0.1, 0.1, 5, 1000
        ]

        bad_tests = [
            -1000.1, 0, None, "a", 1000.1
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=ElecHelper.is_coef_temp
        )

        assert ElecHelper.format_coef_temp_value(
            -16.03554654654) == -16.04
        assert ElecHelper.format_coef_temp_value(
            16.1) == 16.1
        assert ElecHelper.format_coef_temp_value(
            -16) == -16

        assert ElecHelper.get_coef_temp_value(
            -16.03554654654) == -16.04
        assert ElecHelper.get_coef_temp_value(
            16.1) == 16.1
        assert ElecHelper.get_coef_temp_value(
            -16) == -16

        assert ElecHelper.get_coef_temp_value(
            0) == 0
        assert ElecHelper.get_coef_temp_value(
            None) == 0
        assert ElecHelper.get_coef_temp_value(
            -1000.1) == 0
        assert ElecHelper.get_coef_temp_value(
            1000.1) == 0

    def test_is_charge_voltage(self, helper_manager):
        """Test is_charge_voltage method """
        ok_tests = [
            0.1, 5, 1000
        ]

        bad_tests = [
            -1000.1, -5, -1, 0, None, "a", 1000.1
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=ElecHelper.is_charge_voltage
        )

        assert ElecHelper.get_charge_voltage_value(
            16.03554654654) == 16.036
        assert ElecHelper.get_charge_voltage_value(
            16.1) == 16.1
        assert ElecHelper.get_charge_voltage_value(
            16) == 16

        assert ElecHelper.get_charge_voltage_value(
            0) == 0
        assert ElecHelper.get_charge_voltage_value(
            None) == 0
        assert ElecHelper.get_charge_voltage_value(
            -0.1) == 0
        assert ElecHelper.get_charge_voltage_value(
            1000.1) == 0
