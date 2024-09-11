#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Enums core helper module
"""
from enum import Enum, Flag


class BaseEnum(Enum):
    """
    Enums base class
    """

    def describe(self):
        """Describe Enum"""
        return self.name, self.value

class BaseFlag(Flag):
    """
    Flag base class
    """

    def describe(self):
        """Describe Enum"""
        return self.name, self.value

    @classmethod
    def iter_member_values(cls) -> bool:
        """Get list of Enum members and values (member, value)."""
        return [
            (member, member.value)
            for name, member in cls.__members__.items()
        ]
