"""ActiveConnectors model helper"""
import logging
from ve_utils.utype import UType as Ut
from vemonitor_m8.models.item_dict import DictOfObject

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class ActiveConnectors(DictOfObject):
    """ActiveConnectors model helper"""
    def __init__(self):
        DictOfObject.__init__(self)

    @staticmethod
    def is_valid_item_key(key: tuple):
        """Test if is valid item type"""
        return ActiveConnectors.is_valid_item_type(key)

    @staticmethod
    def is_valid_item_value(value: tuple):
        """Test if is valid item type"""
        return ActiveConnectors.is_valid_item_type(value)

    @staticmethod
    def is_valid_item_type(item: tuple):
        """Test if is valid item type"""
        return Ut.is_tuple(item, eq=2)\
            and Ut.is_str(item[0], not_null=True) \
            and Ut.is_str(item[1], not_null=True)
