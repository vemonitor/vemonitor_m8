"""Test vedirect_app module."""
import os
import time
import pytest
from ve_utils.utype import UType as Ut
from vedirect_m8.exceptions import InputReadException
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.workers.vedirect.vedirect_app import VedirectApp


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None

        def init_vedirect_app(self):
            """Init WorkersDict class"""
            self.obj = VedirectApp(
                serial_conf={
                    "serial_port": os.path.join(
                        os.path.expanduser('~'),
                        'vmodem1'
                    )
                },
                serial_test={
                    "PIDTest": {
                        "typeTest": "value",
                        "key": "PID",
                        "value": "0x203"
                    }
                },
                source_name="PyTest",
                auto_start=False,
                wait_connection=True,
                wait_timeout=5
            )

        def read_serial_data(self):
            """Read Serial Data"""
            assert self.obj.ve.try_serial_connection(  # type: ignore
                "PyTest"
            ) is True
            assert self.obj.ve.has_data_cache() is False  # type: ignore
            result, is_cache = self.obj.ve.read_data(  # type: ignore
                caller_name="PyTest",
                timeout=2
            )
            assert Ut.is_dict(result, eq=26)
            assert is_cache is False
            assert self.obj.ve.has_data_cache() is True  # type: ignore

    return HelperManager()


class TestVedirectApp:
    """Test VedirectApp class."""

    def test_lock_serial(self, helper_manager):
        """Test lock_serial method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()
        # Test lock serial
        result = helper_manager.obj.lock_serial(
            caller_name="PyTest"
        )
        assert result is True

        # Test init lock serial
        result = helper_manager.obj.init_lock_serial(
            caller_name="PyTest"
        )
        assert result is True

        # Test is serial locked by actual caller
        result = helper_manager.obj.is_serial_locked_by_caller(
            caller_name="PyTest"
        )
        assert result is True
        # Test is serial locked by bad caller
        result = helper_manager.obj.is_serial_locked_by_caller(
            caller_name="BadCaller"
        )
        assert result is False

        # Test is serial locked
        result = helper_manager.obj.is_serial_locked()
        assert result is True

        # unlock serial
        helper_manager.obj.unlock_serial()

        # Test is serial locked by actual caller
        result = helper_manager.obj.is_serial_locked_by_caller(
            caller_name="PyTest"
        )
        assert result is False
        # Test is serial locked
        result = helper_manager.obj.is_serial_locked()
        assert result is False

        # Test init lock serial
        result = helper_manager.obj.init_lock_serial(
            caller_name="PyTest"
        )
        assert result is True

        # Test is serial locked
        result = helper_manager.obj.is_serial_locked()
        assert result is True

        # unlock serial
        helper_manager.obj.unlock_serial()

        # Test init lock serial with bad caller name
        with pytest.raises(SettingInvalidException):
            helper_manager.obj.init_lock_serial(
                caller_name=None
            )

    def test_read_data(self, helper_manager):
        """Test is_time_to_read_serial method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()
        # Read data from cache
        # Interval is less than 1s
        result = helper_manager.obj.read_data(
            caller_name="PyTest",
            timeout=2
        )
        time.sleep(1)
        # Read data from serial
        result = helper_manager.obj.read_data(
            caller_name="PyTest",
            timeout=2
        )
        assert Ut.is_dict(result, eq=26)
        time.sleep(1)
        # try exception by max read errors
        assert helper_manager.obj.ve.packets_stats.set_max_read_error(
            value=2
        ) is True
        helper_manager.obj.ve.packets_stats.reset_global_counters()
        assert helper_manager.obj.ve.packets_stats.add_serial_read_errors(
        ) == 1
        assert helper_manager.obj.ve.packets_stats.add_serial_read_errors(
        ) == 2
        with pytest.raises(InputReadException):
            helper_manager.obj.read_data(
                caller_name="PyTest",
                timeout=2
            )
