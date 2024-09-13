"""Test Battery models module."""
from typing import Union
from test.schema_test_helper import LoopTests
import pytest
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.models.battery_charge import ChargeCols
from vemonitor_m8.models.battery_data import BatteryDataModel
from vemonitor_m8.models.battery_data import BatteryCapacityModel
from vemonitor_m8.models.battery_data import BatteryStructureModel
from vemonitor_m8.models.battery_data import BatteryChargeSettings

@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager(LoopTests):
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None
            self.test_path = None
            self.loader = None

        def init_battery_data_model(self):
            """Init BatteryDataModel object"""
            self.obj = BatteryDataModel(**HelperManager.get_base_data())

        def init_battery_structure_model(self):
            """Init BatteryStructureModel object"""
            self.obj = BatteryStructureModel(**HelperManager.get_structure_data())

        def init_battery_capacity_model(self):
            """Init BatteryStructureModel object"""
            self.obj = BatteryCapacityModel(**HelperManager.get_capacity_data())

        def init_battery_charge_data_model(self):
            """Init BatteryChargeSettings object"""
            self.obj = BatteryChargeSettings(**HelperManager.get_charge_data())

        @staticmethod
        def get_base_data():
            """Init BatteryStructureModel object"""
            return {
                'name': "rollsBat1",
                'manufacturer': "Rolls",
                'model': "7p4_z2"
            }

        @staticmethod
        def get_structure_data():
            """Init BatteryStructureModel object"""
            result = HelperManager.get_base_data()
            result.update({
                'cell_voltage': 2,
                'bat_voltage': 6,
                'nb_cells': 3
            })
            return result

        @staticmethod
        def get_capacity_data():
            """Init BatteryStructureModel object"""
            result = HelperManager.get_structure_data()
            result.update({
                'capacity': [
                    [5, 185, 37],
                    [20, 220, 11],
                    [100, 250, 2.5]
                ]
            })
            return result

        @staticmethod
        def get_charge_data():
            """Init BatteryStructureModel object"""
            result = HelperManager.get_capacity_data()
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



class TestBatteryDataModel:
    """Test BatteryDataModel model class."""
    def test_set_name(self, helper_manager):
        """Test set_name method """
        helper_manager.init_battery_data_model()
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

    def test_set_manufacturer(self, helper_manager):
        """Test set_manufacturer method """
        helper_manager.init_battery_data_model()
        assert helper_manager.obj.has_manufacturer() is True

        assert helper_manager.obj.set_manufacturer() is False
        assert helper_manager.obj.set_manufacturer("Hello") is True
        assert helper_manager.obj.get_manufacturer() == "Hello"

        ok_tests = [
            "Hel_lo_5", "Hel_lo", "5", "Hel lo", "Hel (lo)",
            "Hel-lo", "_Hel_lo", "-Hel_lo"
        ]

        bad_tests = [
            5, False, "&", "#", "%", "$", "@", "'", "`"
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_manufacturer
        )

        helper_manager.obj.model['manufacturer'] = None
        assert helper_manager.obj.has_manufacturer() is False

        helper_manager.obj.model = None
        assert helper_manager.obj.has_manufacturer() is False

    def test_set_model_name(self, helper_manager):
        """Test set_model_name method """
        helper_manager.init_battery_data_model()
        assert helper_manager.obj.has_model_name() is True

        assert helper_manager.obj.set_model_name() is False
        assert helper_manager.obj.set_model_name("Hello") is True
        assert helper_manager.obj.get_model_name() == "Hello"

        ok_tests = [
            "Hel_lo_5", "Hel_lo", "5", "Hel lo", "Hel (lo)",
            "Hel-lo", "_Hel_lo", "-Hel_lo"
        ]

        bad_tests = [
            5, False, "&", "#", "%", "$", "@", "'", "`"
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_model_name
        )

        helper_manager.obj.model['model'] = None
        assert helper_manager.obj.has_model_name() is False

        helper_manager.obj.model = None
        assert helper_manager.obj.has_model_name() is False

    def test_set_model_data(self, helper_manager):
        """Test set_model_data method """
        helper_manager.init_battery_data_model()
        assert helper_manager.obj.has_manufacturer() is True
        assert helper_manager.obj.has_model_name() is True

        helper_manager.obj.model['manufacturer'] = None
        helper_manager.obj.model['model'] = None
        assert helper_manager.obj.has_manufacturer() is False
        assert helper_manager.obj.has_model_name() is False

        assert helper_manager.obj.set_model_data({
            'manufacturer': "manufacturer_name",
            'model': "model_name"
        }) is True

        assert helper_manager.obj.set_model_data({
            'manufacturer': "manufacturer_name",
            'model': None
        }) is False

        assert helper_manager.obj.set_model_data({
            'manufacturer': None,
            'model': "model_name"
        }) is False

        assert helper_manager.obj.set_model_data() is False

    def test_init(self, helper_manager):
        """Test set_model_data method """
        helper_manager.init_battery_data_model()
        assert helper_manager.obj.has_name() is True
        assert helper_manager.obj.has_manufacturer() is True
        assert helper_manager.obj.has_model_name() is True

        helper_manager.obj.model['manufacturer'] = None
        helper_manager.obj.model['model'] = None
        helper_manager.obj.name = None
        assert helper_manager.obj.has_name() is False
        assert helper_manager.obj.has_manufacturer() is False
        assert helper_manager.obj.has_model_name() is False

        assert helper_manager.obj.init(**{
            'name': "battery_name",
            'manufacturer': "Manufacturer name",
            'model': "Model name"
        }) is True

        assert helper_manager.obj.is_valid() is True
        assert helper_manager.obj.has_name() is True
        assert helper_manager.obj.has_manufacturer() is True
        assert helper_manager.obj.has_model_name() is True

        helper_manager.obj.model['manufacturer'] = None
        helper_manager.obj.model['model'] = None
        assert helper_manager.obj.has_manufacturer() is False
        assert helper_manager.obj.has_model_name() is False

        assert helper_manager.obj.is_valid() is True
        helper_manager.obj.name = None
        assert helper_manager.obj.is_valid() is False

    def test_serialize(self, helper_manager):
        """Test serialize method """
        helper_manager.init_battery_data_model()

        assert helper_manager.obj.init(**{
            'name': "battery_name",
            'manufacturer': "Manufacturer name",
            'model': "Model name"
        }) is True

        data = helper_manager.obj.serialize()
        res = {
            'name': "battery_name",
            'model': {
                'manufacturer': "Manufacturer name",
                'model': "Model name"
            }
        }
        assert res == data
        assert str(res) == str(helper_manager.obj)


class TestBatteryStructureModelModel:
    """Test BatteryStructureModel model class."""
    def test_set_bat_voltage(self, helper_manager):
        """Test set_bat_voltage method """
        helper_manager.init_battery_structure_model()
        assert helper_manager.obj.has_battery_structure() is True

        assert helper_manager.obj.set_bat_voltage() is False
        assert helper_manager.obj.set_bat_voltage(6) is True
        assert helper_manager.obj.get_bat_voltage() == 6
        assert helper_manager.obj.has_bat_voltage() is True

        ok_tests = [
            2, 3.7, 6, 12, 24
        ]

        bad_tests = [
            -1, 0, None, "a"
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_bat_voltage
        )

        helper_manager.obj.bat_voltage = None
        assert helper_manager.obj.has_bat_voltage() is False

    def test_set_cell_voltage(self, helper_manager):
        """Test set_cell_voltage method """
        helper_manager.init_battery_structure_model()
        assert helper_manager.obj.has_battery_structure() is True

        assert helper_manager.obj.set_cell_voltage() is False
        assert helper_manager.obj.set_cell_voltage(6) is True
        assert helper_manager.obj.get_cell_voltage() == 6
        assert helper_manager.obj.has_cell_voltage() is True

        ok_tests = [
            2, 3.7, 6, 12, 24
        ]

        bad_tests = [
            -1, 0, None, "a"
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_cell_voltage
        )

        helper_manager.obj.cell_voltage = None
        assert helper_manager.obj.has_cell_voltage() is False

    def test_set_nb_cells(self, helper_manager):
        """Test set_nb_cells method """
        helper_manager.init_battery_structure_model()
        assert helper_manager.obj.has_battery_structure() is True

        assert helper_manager.obj.set_nb_cells() is False
        assert helper_manager.obj.set_nb_cells(6) is True
        assert helper_manager.obj.get_nb_cells() == 6
        assert helper_manager.obj.has_nb_cells() is True

        ok_tests = [
            2, 6, 12, 24
        ]

        bad_tests = [
            -1, 0, None, "a", 1.1
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_nb_cells
        )

        helper_manager.obj.nb_cells = None
        assert helper_manager.obj.has_nb_cells() is False

    def test_battery_structure(self, helper_manager):
        """Test battery_structure methods """
        helper_manager.init_battery_structure_model()
        assert helper_manager.obj.has_battery_structure() is True

        helper_manager.obj.reset_battery_structure()
        assert helper_manager.obj.has_battery_structure() is False
        assert helper_manager.obj.validate_battery_structure() is False

        ok_tests = [
            # values are correct 12 == 2 * 6
            {'nb_cells': 6, 'cell_voltage': 2, 'bat_voltage': 12},
            # values are incorrect 24 != 2 * 6
            # but bat_voltage in [2, 6, 12, 24, 36, 48](standard_voltages)
            {'nb_cells': 6, 'cell_voltage': 2, 'bat_voltage': 24}
        ]

        bad_tests = [
            # values are incorrect 24 != 2 * 6
            # and bat_voltage not in [2, 6, 12, 24, 36, 48](standard_voltages)
            {'nb_cells': 6, 'cell_voltage': 2, 'bat_voltage': 24.2},
            # no values
            {}
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            is_kwargs=True,
            callback=helper_manager.obj.set_battery_structure
        )

        assert helper_manager.obj.set_battery_structure(
            **{'nb_cells': 6, 'cell_voltage': 2}
        ) is True
        assert helper_manager.obj.get_bat_voltage() == 12

        assert helper_manager.obj.set_battery_structure(
            **{'nb_cells': 6, 'bat_voltage': 12}
        ) is True
        assert helper_manager.obj.get_cell_voltage() == 2

        assert helper_manager.obj.set_battery_structure(
            **{'cell_voltage': 2, 'bat_voltage': 12}
        ) is True
        assert helper_manager.obj.get_nb_cells() == 6


class TestBatteryCapacityModelModel:
    """Test BatteryCapacityModel model class."""
    def test_set_capacity(self, helper_manager):
        """Test set_capacity method """
        helper_manager.init_battery_capacity_model()
        assert helper_manager.obj.has_battery_structure() is True

        assert helper_manager.obj.set_capacity() is False
        assert helper_manager.obj.set_capacity(
            [[5, 185, 37]]
        ) is True
        assert helper_manager.obj.get_capacity() == [[5, 185, 37]]
        assert helper_manager.obj.has_capacity() is True

        ok_tests = [
            [
                [5, 185, 37],
                [20, 220, 11],
                [100, 250, 2.5]
            ],
            [
                [5, 185, 37]
            ]
        ]

        bad_tests = [
            -1, 0, None, "a",
            [], {}, (),
            [[5, 185]],
            [[5, 185, 37, 37]],
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=helper_manager.obj.set_capacity
        )

        helper_manager.obj.capacity = None
        assert helper_manager.obj.has_capacity() is False

    def test_is_valid_capacity(self, helper_manager):
        """Test is_valid_capacity method """
        ok_tests = [
            [
                [5, 185, 37],
                [20, 220, 11],
                [100, 250, 2.5]
            ],
            [
                [5, 185, 37]
            ]
        ]

        bad_tests = [
            -1, 0, None, "a",
            [], {}, (),
            [[5, 185]],
            [[5, 185, 37, 37]],
        ]

        helper_manager.run_all_tests(
            data_ok=ok_tests,
            data_bad=bad_tests,
            callback=BatteryCapacityModel.is_valid_capacity
        )

    def test_get_capacity_diff_err(self, helper_manager):
        """Test get_capacity_diff_err method """

        diff = BatteryCapacityModel.get_capacity_diff_err(
            *[5, 185, 37]
        )
        assert diff == 0

        diff = BatteryCapacityModel.get_capacity_diff_err(
            *[20, 220, 11]
        )
        assert diff == 0

        diff = BatteryCapacityModel.get_capacity_diff_err(
            *[11, 220, 20]
        )
        assert diff == 0

        diff = BatteryCapacityModel.get_capacity_diff_err(
            *[220, 11, 20]
        )
        assert diff == (219.45, -4389, 19.95)

        diff = BatteryCapacityModel.get_capacity_diff_err(
            *[11, 20, 220]
        )
        assert diff == (10.909, -2400, 218.182)

        diff = BatteryCapacityModel.get_capacity_diff_err(
            *[20, 220, 15]
        )
        assert diff == (5.333, -80, 4.0)

    def test_is_valid_capacity_item(self):
        """Test is_valid_capacity_item method """
        diff = BatteryCapacityModel.is_valid_capacity_item(
            *[5, 185, 37]
        )
        assert diff is True

        diff = BatteryCapacityModel.is_valid_capacity_item(
            *[20, 220, 11]
        )
        assert diff is True

        diff = BatteryCapacityModel.is_valid_capacity_item(
            *[11, 220, 20]
        )
        assert diff is True

        diff = BatteryCapacityModel.is_valid_capacity_item(
            *[220, 11, 20]
        )
        assert diff is False

        diff = BatteryCapacityModel.is_valid_capacity_item(
            *[11, 20, 220]
        )
        assert diff is False

        diff = BatteryCapacityModel.is_valid_capacity_item(
            *[20, 220, 15]
        )
        assert diff is False

    def test_get_column(self):
        """Test get_column method """
        result = BatteryCapacityModel.get_discharge_capacity_column()
        assert Ut.is_list(result, not_null=True)

        result = BatteryCapacityModel.get_temp_capacity_column()
        assert Ut.is_list(result, not_null=True)

        result = BatteryCapacityModel.get_temp_cycle_life_column()
        assert Ut.is_list(result, not_null=True)

        result = BatteryCapacityModel.get_capacity_voltage_column()
        assert Ut.is_list(result, not_null=True)

        result = BatteryCapacityModel.get_capacity_voltage_by_hour_rate_column()
        assert Ut.is_list(result, not_null=True)


class TestBatteryChargeSettings:
    """Test BatteryChargeSettings model class."""
    def test_set_charge_settinngs(self, helper_manager):
        """Test set_charge_t_coef method """
        helper_manager.init_battery_charge_data_model()
        assert helper_manager.obj.has_charge_settings() is True

        # Test instanse has all charge settings
        helper_manager.run_tests(
            data=helper_manager.obj.charge.get_charge_setting_keys(),
            callback=helper_manager.obj.charge.has_charge_setting
        )
        # ToDo: on set charge voltage with other base it will be translated to main base
        assert helper_manager.obj.charge.set_charge_setting(
            key=ChargeCols.ABS_U.value,
            value=6
        ) is True
        assert helper_manager.obj.charge.get_charge_setting(
            key=ChargeCols.ABS_U.value
        ) == 6
        assert helper_manager.obj.charge.has_charge_setting(
            key=ChargeCols.ABS_U.value
        ) is True

        charge_items = helper_manager.obj.charge.get_charge_setting_keys()
        callback_res = True
        def test_callback(value: Union[int, float]):
            """Test Charge settings callback"""
            result = True
            for charge_key in charge_items:
                is_set = helper_manager.obj.charge.set_charge_setting(
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

        helper_manager.obj.charge.charge_settings.items = None
        assert helper_manager.obj.charge.has_charge_setting(
            ChargeCols.ABS_U.value
        ) is False
