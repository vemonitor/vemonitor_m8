# -*- coding: utf-8 -*-
"""Threads controller Helper"""
import time
import logging
import threading
from typing import Optional, Union
from ve_utils.utype import UType as Ut
from vemonitor_m8.events.events_manager import EventsGroup

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class RepeatTimer(threading.Timer):
    """Threading Timer Helper"""

    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Timer.__init__(self, interval, function, args, kwargs)
        self.last_exec = time.perf_counter()
        self.min_exec_diff = 0
        self.events = None

    def has_events(self):
        """Test if instance has events"""
        return isinstance(self.events, EventsGroup)

    def set_events(self, events: EventsGroup) -> bool:
        """Update last execution time value."""
        result = False
        if isinstance(events, EventsGroup):
            self.events = events
            result = True
        return result

    def update_last_exec(self) -> float:
        """Update last execution time value."""
        self.last_exec = time.perf_counter()
        return self.last_exec

    def update_min_exec_diff(self):
        """Update last execution diff time value."""
        now = time.perf_counter()
        last_value = self.min_exec_diff
        current_diff = round(now - self.last_exec, 6)
        if last_value == 0:
            self.min_exec_diff = current_diff
        else:
            self.min_exec_diff = min(last_value, current_diff)
        return self.min_exec_diff

    def set_exec_time(self):
        """Update last execution diff time value."""
        diff = self.update_min_exec_diff()
        self.update_last_exec()
        return diff

    def run(self):
        """Run Timer."""
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class ThreadsController:
    """Threads controller Helper"""

    def __init__(self):
        self._max_threads = 10
        self._timers = None
        self._threads = None
        self.lock = threading.Lock()

    def can_add_threads(self):
        """Test if instance has any timer registered."""
        return threading.active_count() <= self._max_threads

    def has_timers(self):
        """Test if instance has any timer registered."""
        return Ut.is_dict(self._timers, not_null=True)

    def init_timers(self):
        """Init _timers property."""
        if not Ut.is_dict(self._timers):
            self._timers = {}

    def has_timer_key(self, key: str):
        """Test if instance has timer key registered."""
        return self.has_timers()\
            and isinstance(self._timers.get(key), RepeatTimer)

    def cancel_all_timers(self):
        """Cancel all timers running"""
        if self.has_timers():
            for timer in self._timers.values():
                timer.cancel()

    def start_timers(self):
        """Test if instance has timer key registered."""
        result = False
        if self.has_timers():
            result = True
            ready = False
            for key, timer in self._timers.items():
                if isinstance(timer, RepeatTimer):
                    if not ready:
                        ready = ThreadsController.sleep_time_to_start()
                    timer.start()
                    logger.debug(
                        "[ThreadsController:start_timer_keys] "
                        "Starting timer %s at %s.",
                        key, time.time()
                    )
        return result

    def add_timer_key(self,
                      key: str,
                      interval: Union[int, float],
                      callback,
                      events: Optional[dict] = None,
                      args=None,
                      kwargs=None) -> bool:
        """Add RepeatTimer to _timers property."""
        result = False
        if Ut.is_str(key, not_null=True)\
                and Ut.is_numeric(interval, positive=True)\
                and self.can_add_threads():

            if not self.has_timer_key(key):
                self.init_timers()
                self._timers[key] = RepeatTimer(
                    interval,
                    callback,
                    args,
                    kwargs
                )
                self._timers[key].set_events(events)
                result = True
        elif not (Ut.is_str(key, not_null=True)
                  and Ut.is_numeric(interval, positive=True)):
            logger.error(
                "[ThreadsController:add_timer_key] "
                "Unable to add timer with key %s. "
                "No more threads can be added ",
                key
            )
        else:
            logger.error(
                "[ThreadsController:add_timer_key] "
                "Unable to add timer with key %s and interval %s. "
                "Bad key or interval type",
                key,
                interval
            )
        return result

    @staticmethod
    def sleep_time_to_start():
        """Sleep time before run thread."""
        now = time.time()
        time_sleep = 2 - (now % 2)
        logger.info(
            "[ThreadsController:sleep_time_to_start] "
            "sleeping %s before start timers. "
            "start time defined at : %s",
            time_sleep,
            now + time_sleep
        )
        time.sleep(time_sleep)
        return True
