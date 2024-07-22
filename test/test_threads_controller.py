"""Test ThreadsController method."""


import time
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.threads_controller import ThreadsController

def timers_callback(**kwargs):
    """Timer callback function"""
    time_call = time.time()
    timer_list = kwargs.get('timer_list')
    timer_list.append(time_call)


class TestThreadsController:
    """Test ThreadsController method."""

    def test_run_timers(self):
        """Test validate_data method."""
        obj = ThreadsController()
        timer_list = []
        obj.add_timer_key(
            key="Timer1",
            interval=1,
            callback=timers_callback,
            kwargs={'timer_list': timer_list}
        )

        assert obj.has_timer_key("Timer1") is True

        obj.add_timer_key(
            key="Timer2",
            interval=2,
            callback=timers_callback,
            kwargs={'timer_list': timer_list}
        )
        assert obj.has_timer_key("Timer2") is True
        assert obj.can_add_threads() is True
        obj.start_timers()
        time.sleep(5)
        obj.cancel_all_timers()

        assert Ut.is_list(timer_list, not_null=True)
        assert round(timer_list[1] - timer_list[0], 0) == 1.0
        assert round(timer_list[2] - timer_list[1], 0) == 0.0
        assert round(timer_list[3] - timer_list[1], 0) == 1.0
        assert round(timer_list[4] - timer_list[3], 0) == 1.0
        assert round(timer_list[5] - timer_list[4], 0) == 0.0
