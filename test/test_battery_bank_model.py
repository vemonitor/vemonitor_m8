"""Test Battery Banks models module."""
from test.schema_test_helper import LoopTests
import pytest
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.battery import BatteryFloodedModel, BatteryModel
from vemonitor_m8.models.battery_bank import BatteryBankBase
from vemonitor_m8.models.battery_bank import BankBattery
from vemonitor_m8.models.battery_bank import BatteryBankStructure
from vemonitor_m8.models.battery_bank import BatteryBank

@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager(LoopTests):
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None
            self.test_path = None
            self.loader = None

        def init_battery_bank_base_model(self):
            """Init BatteryDataModel object"""
            self.obj = BatteryBankBase(
                **HelperManager.get_battery_bank_base_data()
            )

        def init_bank_battery_model(self):
            """Init BatteryDataModel object"""
            self.obj = BankBattery(
                **HelperManager.get_bank_battery_data()
            )

        def init_battery_structure_model(self):
            """Init BatteryStructureModel object"""
            self.obj = BatteryBankStructure(
                **HelperManager.get_structure_data()
            )

        def init_battery_bank_model(self):
            """Init BatteryChargeSettings object"""
            self.obj = BatteryBank(
                **HelperManager.get_battery_bank_model_data()
            )

        @staticmethod
        def get_battery_bank_base_data():
            """Init BatteryStructureModel object"""
            return {
                'name': "rollsBat1",
            }

        @staticmethod
        def get_battery_data():
            """Init BatteryStructureModel object"""
            return {
                'name': "rollsBat1",
                'manufacturer': "Rolls",
                'model': "7p4_z2",
                'battery_type': "flooded",
                'cell_voltage': 2,
                'bat_voltage': 6,
                'nb_cells': 3,
                'capacity': [
                    [5, 185, 37],
                    [20, 220, 11],
                    [100, 250, 2.5]
                ],
                'charge_settings': {
                    'charge_absorption_u': 14.1,
                    'charge_float_u': 13.8,
                    'charge_storage_u': 13.2,
                    'charge_equalization_u': 15.9,
                    'charge_t_coef': -16.02
                }

            }

        @staticmethod
        def get_bank_battery_data():
            """Init BatteryStructureModel object"""
            result = HelperManager.get_battery_bank_base_data()
            result.update({
                'battery': HelperManager.get_battery_data()
            })
            return result

        @staticmethod
        def get_structure_data():
            """Init BatteryStructureModel object"""
            result = HelperManager.get_bank_battery_data()
            result.update({
                'in_series': 1,
                'in_parallel': 1
            })
            return result

        @staticmethod
        def get_battery_bank_model_data():
            """Init BatteryStructureModel object"""
            result = HelperManager.get_structure_data()
            charge_settings = {
                'charge_absorption_u': 14.1,
                'charge_float_u': 13.8,
                'charge_storage_u': 13.2,
                'charge_equalization_u': 15.9,
                'charge_t_coef': -16.02
            }
            result.update({
                'charge_settings': charge_settings
            })
            return result

    return HelperManager()

class TestBatteryBankBase:
    """Test BatteryBankBase model class."""
    def test_set_name(self, helper_manager):
        """Test set_name method """
        helper_manager.init_battery_bank_base_model()
        assert helper_manager.obj.has_name() is True

        assert helper_manager.obj.set_name() is False
        assert helper_manager.obj.set_name("Hello") is True
        assert helper_manager.obj.get_name() == "Hello"

        ok_tests = [
            "Hel_lo_5", "Hel_lo", "5"
        ]

        bad_tests = [
            "_Hello", "-Hello", "Hello$", "Hel-lo", "Hello Hello"
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_name
        )

        helper_manager.obj.name = None
        assert helper_manager.obj.has_name() is False

    def test_base(self, helper_manager):
        """Test base methods """
        helper_manager.init_battery_bank_base_model()
        assert helper_manager.obj.has_name() is True

        props = {'name': "HelloInit"}
        assert helper_manager.obj.init(
            **props
        ) is True
        assert helper_manager.obj.get_name() == "HelloInit"

        data = helper_manager.obj.serialize()
        assert data == props
        assert str(props) == str(helper_manager.obj)


class TestBankBattery:
    """Test BankBattery model class."""
    def test_set_battery(self, helper_manager):
        """Test set_battery method """
        helper_manager.init_bank_battery_model()
        assert helper_manager.obj.has_battery() is True
        assert isinstance(
            helper_manager.obj.get_battery(),
            BatteryModel
        ) is True
        # on fail set battery, battery value
        # will be reset to None type
        assert helper_manager.obj.set_battery() is False
        assert helper_manager.obj.has_battery() is False

        # test set_battery
        ok_tests = [
            # with minimal dict props
            {
                'name': "MyTestBat",
                'battery_type': "flooded"
            }
        ]

        bad_tests = [
            # without name in dict props
            {
                'battery_type': "flooded"
            },
            # without battery_type in dict props
            {
                'name': "MyTestBat"
            },
            # with bad name in dict props
            # wronk key pattern
            {
                'name': "My Test Bat",
                'battery_type': "flooded"
            },
            # with bad name in dict props
            # wronk key pattern
            {
                'name': "MyTestBat",
                'battery_type': "bad_type"
            }
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_battery
        )

        helper_manager.obj.battery = None
        assert helper_manager.obj.has_battery() is False

    def test_set_charge_settings(self, helper_manager):
        """Test set_charge_settings method """
        helper_manager.init_bank_battery_model()
        assert helper_manager.obj.has_battery() is True

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
            }
        ]

        bad_tests = [
            # without any charge settings props
            {
                'battery_type': "flooded"
            },
            # with different base voltage
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
                'charge_storage_u': 16.3
            }
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_charge_settings
        )
