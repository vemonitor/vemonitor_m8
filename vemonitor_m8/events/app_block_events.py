# -*- coding: utf-8 -*-
"""App block run events Helper"""
import logging
from vemonitor_m8.core.event import Event

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AppBlockEvents:
    """App block run events Helper"""
    def __init__(self):
        self.on_worker_data_ready = Event()
        self.on_worker_init_error = Event()

    def worker_data_ready(self):
        """Raise on_worker_data_ready event."""
        self.on_worker_data_ready()

    def subscribe_worker_data_ready(self, obj_method):
        """Subscribe on_worker_data_ready event."""
        self.on_worker_data_ready += obj_method

    def unsubscribe_worker_data_ready(self, obj_method):
        """UnSubscribe on_worker_data_ready event."""
        self.on_worker_data_ready -= obj_method

    def worker_init_error(self):
        """Raise on_worker_init_error event."""
        self.on_worker_init_error()

    def subscribe_worker_init_error(self, obj_method):
        """Subscribe on_worker_init_error event."""
        self.on_worker_init_error += obj_method

    def unsubscribe_worker_init_error(self, obj_method):
        """UnSubscribe on_worker_init_error event."""
        self.on_worker_init_error -= obj_method
