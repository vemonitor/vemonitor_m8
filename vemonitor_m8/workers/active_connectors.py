"""ActiveConnectors model helper"""
import logging
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.models.item_dict import DictOfObject



__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class ActiveConnectors(DictOfObject):
    """ActiveConnectors model helper"""
    def __init__(self):
        DictOfObject.__init__(self)

    def has_item_key(self, key: tuple) -> bool:
        """Test if instance has item key defined."""
        return self.has_items()\
            and ActiveConnectors.is_valid_item_type(key)\
            and ActiveConnectors.is_valid_item_type(self.items.get(key))

    def add_item(self,
                 key: tuple,
                 value: tuple
                 ) -> bool:
        """Add item item."""
        result = False
        if ActiveConnectors.is_valid_item_type(key)\
                and ActiveConnectors.is_valid_item_type(value):
            self.init_item()
            self.items[key] = value
            result = True
        return result

    def get_item(self, key: tuple) -> Optional[object]:
        """Get item key."""
        result = None
        if self.has_item_key(key):
            result = self.items.get(key)
        return result

    @staticmethod
    def is_valid_item_type(item: tuple):
        """Test if is valid item type"""
        return Ut.is_tuple(item, eq=2)\
            and Ut.is_str(item[0], not_null=True) \
            and Ut.is_str(item[1], not_null=True)
