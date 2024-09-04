# -*- coding: utf-8 -*-
"""Vemonitor EventsManager Helper"""
from typing import Optional
from ve_utils.utype import UType as Ut


class EventsManager:
    """Vemonitor EventsManager Helper"""
    def __init__(self):
        self.events = {}

    def has_events(self) -> bool:
        """Test if instance has any event registered."""
        return Ut.is_dict(self.events, not_null=True)

    def reset_events(self) -> bool:
        """Reset all events."""
        self.events = {}
        return True

    def has_group_events(self, group: str) -> bool:
        """Test if instance has any group events registered."""
        return self.has_events()\
             and Ut.is_dict(self.events.get(group), not_null=True)

    def reset_group_events(self, group: str) -> bool:
        """Reset all events from group."""
        result = False
        if self.has_group_events(group):
            self.events[group] = {}
            result = True
        return result

    def get_group_events(self, group: str) -> Optional[dict]:
        """Get all events from group."""
        result = None
        if self.has_group_events(group):
            result = self.events[group]
        return result

    def has_event(self, group: str, key: str) -> bool:
        """Test if instance has event key registered."""
        return self.has_events()\
            and self.has_group_events(group=group)\
            and isinstance(self.events[group].get(key), Event)

    def get_event(self,
                  group: str,
                  key: str,
                  ) -> Optional[Event]:
        """Get all events from group."""
        result = None
        if self.has_event(group=group, key=key):
            result = self.events[group].get(key)
        return result

    def add_event(self,
                  group: str,
                  key: str
                  ) -> bool:
        """Add Event."""
        result = False
        if Ut.is_str(key, not_null=True)\
                and not self.has_event(group=group, key=key):
            self.events[group][key] = Event()
            result = True
        return result

    def subscribe_event(self,
                        group: str,
                        key: str,
                        callback: object
                        ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_event(group=group, key=key):
            self.events[group][key] += callback
            result = True
        return result

    def unsubscribe_event(self,
                          group: str,
                         key: str,
                         callback: object
                         ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_event(group=group, key=key):
            self.events[group][key] -= callback
            result = True
        return result

    def trigger_event(self,
                      group: str,
                      key: str
                      ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_event(group=group, key=key):
            self.events[group][key]()
            result = True
        return result
