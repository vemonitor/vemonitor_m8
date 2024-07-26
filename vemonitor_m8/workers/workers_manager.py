"""Workers manager helper"""
import logging
from typing import Optional
from vemonitor_m8.models.workers import InputWorker, OutputWorker
from vemonitor_m8.models.workers import Workers
from vemonitor_m8.models.workers import WorkersHelper
from vemonitor_m8.workers.active_connectors import ActiveConnectors
from vemonitor_m8.core.exceptions import WorkerException
from vemonitor_m8.workers.workers_loader import WorkersLoader


__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class WorkersManager(Workers):
    """Workers model helper"""

    def __init__(self):
        Workers.__init__(self)
        self.active_connectors = ActiveConnectors()
        self._inputs_status = {}
        self._output_status = {}
        self._workers_status = True

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

    def add_active_connector(self, key: str, value: tuple)-> bool:
        """Add Worker status error"""
        return self.active_connectors.add_item(
            key=key,
            value=value
        )

    def get_workers_status(self)-> bool:
        """Add Worker status error"""
        return self._workers_status is True

    def set_workers_status(self, status: bool):
        """Add Worker status error"""
        if self._workers_status is True and status is False:
            self._workers_status = False

    def get_input_workers_status(self)-> dict:
        """Add Worker status error"""
        return self._inputs_status

    def add_input_worker_status(self,
                                      worker_name: str,
                                      worker_status: bool):
        """Add Input Worker status error"""
        self._inputs_status[worker_name] = worker_status
        self.set_workers_status(worker_status)

    def get_output_workers_status(self)-> dict:
        """Add Worker status error"""
        return self._output_status

    def add_output_worker_status(self,
                                       worker_name: str,
                                       worker_status: bool):
        """Add Output Worker status error"""
        self._output_status[worker_name] = worker_status
        self.set_workers_status(worker_status)

    def init_input_worker(self,
                          connector: dict,
                          worker_key: str,
                          enum_key: int,
                          item: dict
                          ) -> Optional[InputWorker]:
        """Initialise input worker."""
        result = None
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
                self.add_active_connector(
                    key=connector_key,
                    value=('input', worker_name)
                )
            # init worker
            worker = WorkersLoader.get_input_worker_by_key(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )

            if not WorkersHelper.is_input_worker(worker):
                raise WorkerException(
                    """Fatal Error: "
                    f"Unable to Initialyse Input Worker {worker_name}"""
                )

            self.add_input_worker(
                key=worker_name,
                worker=worker
            )
            result = worker
            self.add_input_worker_status(
                worker_name=worker_name,
                worker_status=worker.get_worker_status()
            )

        else:
            result = self.get_input_worker(worker_name)
            self.add_input_worker_status(
                worker_name=worker_name,
                worker_status=result.get_worker_status()
            )
        return result

    def init_output_worker(self,
                           connector: dict,
                           worker_key: str,
                           enum_key: int,
                           item: dict
                           ) -> Optional[OutputWorker]:
        """Initialise output worker."""
        result = None
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
                self.add_active_connector(
                    key=connector_key,
                    value=('output', worker_name)
                )

            # init worker
            worker = WorkersLoader.get_output_worker_by_key(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )

            if not WorkersHelper.is_output_worker(worker):
                raise WorkerException(
                    """Fatal Error: "
                    f"Unable to Initialyse Output Worker {worker_name}"""
                )
            self.add_output_worker(
                key=worker_name,
                worker=worker
            )
            result = worker
            self.add_output_worker_status(
                worker_name=worker_name,
                worker_status=result.get_worker_status()
            )

        else:
            result = self.get_output_worker(worker_name)
            self.add_output_worker_status(
                worker_name=worker_name,
                worker_status=result.get_worker_status()
            )
        return result
