#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Configuration AppBlock model Helper class
"""
from typing import Optional
from vemonitor_m8.models.conf_battery_banks import ConfigBatteryBanks


class ConfigSolarPlants(ConfigBatteryBanks):
    """
    Configuration App Connectors model Helper class
    """
    def __init__(self,
                 app_blocks: Optional[list] = None,
                 app_connectors: Optional[dict] = None):
        """
        Initialise Config model instance.

        :Example :
            >>> conf = Config(app_blocks=[...], app_connectors={...})
        :param app_blocks: App Blocks settings
        :param app_connectors: Output Api Connectors settings
        """
        ConfigBatteryBanks.__init__(
            self,
            app_blocks=app_blocks,
            app_connectors=app_connectors
        )
        self.solar_plants = None
