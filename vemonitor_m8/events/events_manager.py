# -*- coding: utf-8 -*-
"""Vemonitor EventsManager Helper"""
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.events.event import Event


class EventsGroup:
    """Vemonitor EventsGroup Helper"""
    def __init__(self):
        self.events = {}

    def has_events(self) -> bool:
        """Test if instance has any event registered."""
        return Ut.is_dict(self.events, not_null=True)

    def reset_events(self) -> bool:
        """Reset all events."""
        self.events = {}
        return True

    def has_event(self, key: str) -> bool:
        """Test if instance has event key registered."""
        return self.has_events()\
            and isinstance(self.events.get(key), Event)

    def get_event(self,
                  key: str,
                  ) -> Optional[Event]:
        """Get all events from group."""
        result = None
        if self.has_event(key=key):
            result = self.events.get(key)
        return result

    def add_event(self,
                  key: str
                  ) -> bool:
        """Add Event."""
        result = False
        if Ut.is_str(key, not_null=True)\
                and not self.has_event(key=key):
            self.events[key] = Event()
            result = True
        return result

    def subscribe_event(self,
                        key: str,
                        callback: object
                        ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_event(key=key):
            self.events[key] += callback
            result = True
        return result

    def unsubscribe_event(self,
                          key: str,
                          callback: object
                          ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_event(key=key):
            self.events[key] -= callback
            result = True
        return result

    def trigger_event(self,
                      key: str
                      ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_event(key=key):
            self.events[key]()
            result = True
        return result


class EventsManager:
    """Vemonitor EventsManager Helper"""
    def __init__(self):
        self.groups = {}

    def has_groups(self) -> bool:
        """Test if instance has any group registered."""
        return Ut.is_dict(self.groups, not_null=True)

    def reset_groups(self) -> bool:
        """Reset all groups."""
        self.groups = {}
        return True

    def has_group_events(self, group: str) -> bool:
        """Test if instance has any group events registered."""
        return self.has_groups()\
             and isinstance(self.groups.get(group), EventsGroup)

    def reset_group_events(self, group: str) -> bool:
        """Reset all events from group."""
        if not Ut.is_dict(self.groups):
            self.reset_groups()
        self.groups[group] = EventsGroup()
        return True

    def get_group_events(self, group: str) -> Optional[dict]:
        """Get all events from group."""
        result = None
        if self.has_group_events(group):
            result = self.groups[group]
        return result

    def add_events(self,
                  group: str,
                  events: list
                  ) -> bool:
        """Add Event."""
        result = False
        if Ut.is_list(events, not_null=True):
            if not self.has_group_events(group=group):
                self.reset_group_events(group=group)
            nb_events = len(events)
            nb_init = 0
            for key in events:
                if self.groups[group].add_event(key=key):
                    nb_init += 1
            if nb_events == nb_init:
                result = True
        return result

    def subscribe_event(self,
                        group: str,
                        key: str,
                        callback: object
                        ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_group_events(group=group):
            result = self.groups[group].subscribe_event(
                key=key,
                callback=callback
            )
        return result

    def unsubscribe_event(self,
                          group: str,
                         key: str,
                         callback: object
                         ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_group_events(group=group):
            result = self.groups[group].unsubscribe_event(
                key=key,
                callback=callback
            )
        return result

    def trigger_event(self,
                      group: str,
                      key: str
                      ) -> bool:
        """Suscribe to an Event."""
        result = False
        if self.has_group_events(group=group):
            result = self.groups[group].trigger_event(
                key=key
            )
        return result
