# -*- coding: utf-8 -*-
"""Workers manager helper"""
import logging
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.models.settings.item_dict import DictOfObject
from vemonitor_m8.models.settings.workers import InputWorker
from vemonitor_m8.models.settings.workers import OutputWorker
from vemonitor_m8.models.settings.workers import Workers
from vemonitor_m8.models.settings.workers import WorkersHelper
from vemonitor_m8.workers.vedirect_worker import VedirectWorker
from vemonitor_m8.workers.emoncms_worker import EmoncmsWorker


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


class WorkersManager(Workers):
    """Workers model helper"""

    def __init__(self):
        Workers.__init__(self)
        self.active_connectors = ActiveConnectors()

    def get_active_connector(self, connector_key: tuple):
        """Get active connector from workers."""
        result = None
        if self.active_connectors.has_item_key(connector_key):
            active_connector = self.active_connectors.get_item(connector_key)
            if ActiveConnectors.is_valid_item_type(active_connector):
                from_type, worker_name = active_connector
                if from_type == "input":
                    worker = self.get_input_worker(worker_name)
                    result = worker.worker
                elif from_type == "output":
                    worker = self.get_output_worker(worker_name)
                    result = worker.worker
        return result

    def init_input_worker(self,
                          connector: dict,
                          worker_key: str,
                          enum_key: int,
                          item: dict
                          ) -> Optional[InputWorker]:
        """Initialise input worker."""
        worker_name = WorkersHelper.get_worker_name(worker_key, item)
        if not self.has_input_worker_key(worker_name):
            logger.info("[WorkersManager]---> new input worker %s",
                         worker_name
            )
            worker = None
            connector_key = (worker_key, item.get("source"))
            active_connector = self.get_active_connector(connector_key)
            if active_connector is not None:
                connector = active_connector
            else:
                self.active_connectors.add_item(
                    key=connector_key,
                    value=('input', worker_name)
                )
            if worker_key == "serial":
                worker = WorkersManager.init_vedirect_worker(
                    connector=connector,
                    worker_key=worker_key,
                    enum_key=enum_key,
                    item=item
                )
            elif worker_key == "redis":
                pass
            elif worker_key == "influxDb2":
                pass
            elif worker_key == "tuya":
                pass

            if WorkersHelper.is_input_worker(worker):
                self.add_input_worker(
                    key=worker_name,
                    worker=worker
                )
                return worker
        else:
            return self.get_input_worker(worker_name)

    def init_output_worker(self,
                           connector: dict,
                           worker_key: str,
                           enum_key: int,
                           item: dict
                           ) -> Optional[OutputWorker]:
        """Initialise output worker."""
        worker_name = WorkersHelper.get_worker_name(worker_key, item)
        if not self.has_output_worker_key(worker_name):
            logger.info("[WorkersManager]---> new output worker %s",
                        worker_name
            )
            worker = None
            connector_key = (worker_key, item.get("source"))
            active_connector = self.get_active_connector(connector_key)
            if active_connector is not None:
                connector = active_connector
            else:
                self.active_connectors.add_item(
                    key=connector_key,
                    value=('input', worker_name)
                )
            if worker_key == "redis":
                pass
            elif worker_key == "influxDb2":
                pass
            elif worker_key == "emoncms":
                worker = WorkersManager.init_emoncms_worker(
                    connector=connector,
                    worker_key=worker_key,
                    enum_key=enum_key,
                    item=item
                )
            elif worker_key == "tuya":
                pass

            if WorkersHelper.is_output_worker(worker):
                self.add_output_worker(
                    key=worker_name,
                    worker=worker
                )
                return worker

        else:
            return self.get_output_worker(worker_name)

    @staticmethod
    def init_vedirect_worker(connector: dict,
                             worker_key: str,
                             enum_key: int,
                             item: dict) -> VedirectWorker:
        """Initialise Serial vedirect worker."""
        return VedirectWorker(
            WorkersHelper.format_worker_conf(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        )

    @staticmethod
    def init_emoncms_worker(connector: dict,
                            worker_key: str,
                            enum_key: int,
                            item: dict) -> EmoncmsWorker:
        """Initialise Serial vedirect worker."""
        return EmoncmsWorker(
            WorkersHelper.format_worker_conf(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        )