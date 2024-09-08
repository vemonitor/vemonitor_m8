#!/usr/bin/python
# -*- coding: utf-8 -*-
"""AsyncMiddlewaresRun Helper"""
import logging
from typing import Optional
from vemonitor_m8.core.utils import Utils as Ut
from vemonitor_m8.middlewares.batteries.battery_mid import BatteryMid
from vemonitor_m8.middlewares.batteries.battery_mid_min import BatteryMidMin

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__license__ = "Apache"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class MiddlewaresLoader:
    """MiddlewaresLoader Helper"""

    @staticmethod
    def get_battery_monitor_mid(battery_bank: Optional[dict]) -> dict:
        """Get battery monitor middleware."""
        result = None
        if Ut.is_dict(battery_bank, not_null=True):
            result = BatteryMid(
                battery_bank=battery_bank
            )
        else:
            result = BatteryMidMin()
        return result
