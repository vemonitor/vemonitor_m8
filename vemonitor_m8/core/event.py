# -*- coding: utf-8 -*-
"""Vemonitor Event Helper"""


class Event(object):
    """Vemonitor Event Helper"""
    def __init__(self):
        self.__event_handlers = []

    def __iadd__(self, handler):
        """Add an event handler."""
        self.__event_handlers.append(handler)
        return self

    def __isub__(self, handler):
        """Remove an event handler."""
        self.__event_handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        """Call registered event handlers."""
        for eventhandler in self.__event_handlers:
            eventhandler(*args, **kwargs)
