#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Config Model Class
"""
from typing import Optional

from vemonitor_m8.models.conf_solar_plants import ConfigSolarPlants


class Config(ConfigSolarPlants):
    """
    Config Model Class
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
        ConfigSolarPlants.__init__(
            self,
            app_blocks=app_blocks,
            app_connectors=app_connectors
        )

    def is_valid(self):
        """Test if is valid Config Data"""
        return self.has_app_blocks()\
            and self.has_app_connectors()\
            and self.has_data_structures()

    def __str__(self):
        """__str__"""
        return str(self.serialize())

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of order
        :rtype: Dict
        """

        return {
            'app_blocks': self.app_blocks,
            'app_connector': self.app_connectors,
            'battery_banks': self.battery_banks,
            'solar_plants': self.solar_plants,
            'data_structures': self.data_structures
        }
