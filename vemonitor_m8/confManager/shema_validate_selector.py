"""
Used to select and load particular jsonschema and validate data with it.

Get data to test and jsonschema key,
Load the jsonschema file with the private class method _load_schema,
and validate the instance data.
If any validation error occurs, raise exception.
Or if no error occurs, return data tested object

:Example:
    > SchemaValidate.validate_data(data=appBlocks_data, shem_key_path="appBlocks")
    > ...appBlocks_data...

 .. seealso:: ConfigLoader
 .. raises:: ValidationError, SchemaError, ErrorTree
"""

import logging
from typing import Union
from vemonitor_m8.confManager.schema_validate import SchemaValidate

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class SchemaValidateSelector(SchemaValidate):
    """Simple Class to load jsonschema file and validate data."""

    @classmethod
    def is_valid_app_blocks_conf(cls, conf_item: Union[dict, list]) -> bool:
        """Test if is valid App Blocks configuration"""
        return SchemaValidateSelector.validate_data(
            conf_item,
            'appBlocks'
        ) is not None

    @classmethod
    def is_valid_app_connectors_conf(cls, conf_item: Union[dict, list]) -> bool:
        """Test if is valid App Connectors configuration"""
        return SchemaValidateSelector.validate_data(
            conf_item,
            'appConnectors'
        ) is not None

    @classmethod
    def is_valid_battery_banks_conf(cls, conf_item: Union[dict, list]) -> bool:
        """Test if is valid Battery Banks configuration"""
        return SchemaValidateSelector.validate_data(
            conf_item,
            'batteryBanks'
        ) is not None

    @classmethod
    def is_valid_data_structure_conf(cls, conf_item: Union[dict, list]) -> bool:
        """Test if is valid Data Structure configuration"""
        return SchemaValidateSelector.validate_data(
            conf_item,
            'data_structure'
        ) is not None
