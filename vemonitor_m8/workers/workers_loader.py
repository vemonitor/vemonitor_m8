"""Workers manager helper"""
import logging
from typing import Optional
from vemonitor_m8.models.workers import OutputWorker, Worker, WorkersHelper
from vemonitor_m8.workers.redis.redis_worker import RedisInputWorker
from vemonitor_m8.workers.redis.redis_worker import RedisOutputWorker
from vemonitor_m8.workers.vedirect.vedirect_worker import VedirectWorker
from vemonitor_m8.core.exceptions import VeMonitorError
try:
    from emon_worker_m8.emoncms_worker import EmoncmsWorker  # type: ignore
except ImportError:
    class EmoncmsWorker(BaseException):
        """Dummy EmoncmsWorker class"""

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class WorkersLoader:
    """Workers manager helper"""

    @staticmethod
    def get_input_worker_by_key(worker_key: str,
                                connector: dict,
                                enum_key: int,
                                item: dict
                                ) -> Optional[Worker]:
        """Get Input worker by key."""
        worker = None
        # init worker type
        if worker_key == "serial":
            worker = WorkersLoader.init_vedirect_worker(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        elif worker_key == "redis":
            worker = WorkersLoader.init_redis_input_worker(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        elif worker_key == "influxDb2":
            pass
        elif worker_key == "tuya":
            pass

        return worker

    @staticmethod
    def get_output_worker_by_key(worker_key: str,
                                 connector: dict,
                                 enum_key: int,
                                 item: dict
                                 ) -> Optional[Worker]:
        """Get Output worker by key."""
        worker = None
        if worker_key == "redis":
            worker = WorkersLoader.init_redis_output_worker(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        elif worker_key == "influxDb2":
            pass
        elif worker_key == "emoncms":
            worker = WorkersLoader.init_emoncms_worker(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        elif worker_key == "tuya":
            pass

        return worker

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
    def init_redis_input_worker(connector: dict,
                                worker_key: str,
                                enum_key: int,
                                item: dict) -> RedisInputWorker:
        """Initialise Serial vedirect worker."""
        return RedisInputWorker(
            WorkersHelper.format_worker_conf(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        )

    @staticmethod
    def init_redis_output_worker(connector: dict,
                                 worker_key: str,
                                 enum_key: int,
                                 item: dict) -> RedisOutputWorker:
        """Initialise Serial vedirect worker."""
        return RedisOutputWorker(
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
        if not isinstance(EmoncmsWorker, OutputWorker):
            raise VeMonitorError(
                "Fatal Error: "
                "EmoncmsWorker is unreachable. "
                "Please install emon_worker_m8 package."
            )

        return EmoncmsWorker(
            WorkersHelper.format_worker_conf(
                connector=connector,
                worker_key=worker_key,
                enum_key=enum_key,
                item=item
            )
        )
