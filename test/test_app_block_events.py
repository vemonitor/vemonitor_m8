"""Test AppBlockEvents method."""
import pytest
from vemonitor_m8.events.app_block_events import AppBlockEvents


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            self.obj = AppBlockEvents()
            self.worker_ready_event = 0
            self.worker_error_event = 0

        def init_data(self):
            """On data ready callback event."""
            self.obj = AppBlockEvents()
            self.worker_ready_event = 0
            self.worker_error_event = 0

        def on_data_ready_callback(self):
            """On data ready callback event."""
            self.worker_ready_event += 1

        def on_data_error_callback(self):
            """On data ready callback event."""
            self.worker_error_event += 1

    return HelperManager()


class TestAppBlockEvents:
    """Test AppBlockEvents method."""

    def test_worker_data_ready(self, helper_manager):
        """Test subscribe_worker_data_ready method."""
        events = helper_manager.obj
        # suscribe to event
        events.subscribe_worker_data_ready(
            obj_method=helper_manager.on_data_ready_callback
        )
        # worker_ready event counter must be equal to 0
        assert helper_manager.worker_ready_event == 0

        # trigger event on_worker_data_ready 2 times
        helper_manager.obj.worker_data_ready()
        helper_manager.obj.worker_data_ready()

        # Now worker_ready event counter must be equal to 2
        # We have triggered the event two times
        assert helper_manager.worker_ready_event == 2

        # unsuscribe to event
        events.unsubscribe_worker_data_ready(
            obj_method=helper_manager.on_data_ready_callback
        )

        # trigger event on_worker_data_ready 2 more times
        helper_manager.obj.worker_data_ready()
        helper_manager.obj.worker_data_ready()

        # worker_ready event counter must be equal to 2
        # The events triggered after unsuscribed has not effect
        assert helper_manager.worker_ready_event == 2

    def test_worker_data_error(self, helper_manager):
        """Test subscribe_worker_init_error method."""
        events = helper_manager.obj
        # suscribe to event
        events.subscribe_worker_init_error(
            obj_method=helper_manager.on_data_error_callback
        )
        # worker_error event counter must be equal to 0
        assert helper_manager.worker_error_event == 0

        # trigger event on_worker_data_ready 2 times
        helper_manager.obj.worker_init_error()
        helper_manager.obj.worker_init_error()

        # Now worker_ready event counter must be equal to 2
        # We have triggered the event two times
        assert helper_manager.worker_error_event == 2

        # unsuscribe to event
        events.unsubscribe_worker_init_error(
            obj_method=helper_manager.on_data_error_callback
        )

        # trigger event on_worker_data_ready 2 more times
        helper_manager.obj.worker_init_error()
        helper_manager.obj.worker_init_error()

        # worker_ready event counter must be equal to 2
        # The events triggered after unsuscribed has not effect
        assert helper_manager.worker_error_event == 2
