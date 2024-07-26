"""Test AppBlockRun method."""

import inspect
import time
from os import path as Opath
import pytest
from vemonitor_m8.conf_manager.config_loader import ConfigLoader
from vemonitor_m8.core.async_app_run import AppBlockRun


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
            self.loader = ConfigLoader(self.test_path)

    return HelperManager()


class TestAppBlockRun:
    """Test AppBlockRun method."""

    def test_run_block(self, helper_manager):
        """Test subscribe_worker_data_ready method."""
        conf = helper_manager.loader.get_settings_from_schema(
            block_name=None,
            app_name="batSerialMonitor",
        )
        obj = AppBlockRun(
            conf=conf
        )

        assert obj.is_ready()

        # inputs workers blocks run on background (Threads),
        # executed by a timer
        obj.add_input_items_timer()
        # inputs workers blocks run
        obj.setup_outputs_workers()

        assert obj.workers.has_input_workers()
        assert obj.workers.has_output_workers()

        time.sleep(5)
        obj.cancel_all_timers()
