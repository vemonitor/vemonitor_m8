# -*- coding: utf-8 -*-
"""Vedirect api Helper"""
import logging
import time
from typing import NamedTuple, Optional, Union
from vedirect_m8.packet_stats import PacketStats
from vedirect_m8.vepackets_app import VePacketsApp
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.exceptions import SettingInvalidException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class WorkerConf(NamedTuple):
    serial_conf: dict
    serial_test: dict
    source_name: str = 'VePackets'
    auto_start: bool = True
    wait_connection: bool = True
    wait_timeout: Union[int, float] = 3600
    max_packet_blocks: Optional[int] = 18
    nb_packets: int = 10
    accepted_keys: Optional[list] = None
    min_interval: int = 1
    max_read_error: int = 30


class VedirectApp:
    """This class is a shared VeDirect Controller Helper."""
    def __init__(self,
                 serial_conf: dict,
                 serial_test: dict,
                 source_name: str = 'VePackets',
                 auto_start: bool = True,
                 wait_connection: bool = True,
                 wait_timeout: Union[int, float] = 3600,
                 max_packet_blocks: Optional[int] = 18,
                 nb_packets: int = 10,
                 accepted_keys: Optional[list] = None,
                 min_interval: int = 1,
                 max_read_error: int = 30,
                 **kwargs: WorkerConf
                 ):
        self.ve = VePacketsApp(
            serial_conf=serial_conf,
            serial_test=serial_test,
            source_name=source_name,
            auto_start=auto_start,
            wait_connection=wait_connection,
            wait_timeout=wait_timeout,
            max_packet_blocks=max_packet_blocks,
            nb_packets=nb_packets,
            accepted_keys=accepted_keys,
            min_interval=min_interval,
            max_read_error=max_read_error
        )
        self._serial_lock = False
        self._lock_caller = None
        self._min_source_interval = 1
        self._nb_packets = 4
        self.packets_stats = PacketStats()

    def is_ready(self) -> bool:
        """Test if worker is ready."""
        return isinstance(self.ve, VePacketsApp)\
            and self.ve.is_ready()

    def is_serial_locked(self) -> bool:
        """Test if serial connexion is locked."""
        return self._serial_lock is True

    def is_serial_locked_by_caller(self, caller_name: str) -> bool:
        """Test if serial connexion is locked by caller name."""
        return self.is_serial_locked() and self._lock_caller == caller_name

    def lock_serial(self, caller_name: str) -> bool:
        """Lock serial connexion for caller_name node."""
        result = False
        self._lock_caller = None
        if Ut.is_str(caller_name):
            self._lock_caller = caller_name
            self._serial_lock = True
            result = True
        return result

    def unlock_serial(self):
        """Unlock serial connexion."""
        self._lock_caller = None
        self._serial_lock = False

    def init_lock_serial(self, caller_name):
        """Init lock status for serial connexion."""
        result = False
        if not self.is_serial_locked():
            if not self.lock_serial(caller_name):
                raise SettingInvalidException(
                    "[VedirectHelper:init_lock_serial] "
                    "Invalid Caller key. Unable to lock serial port."
                )
            result = True
        elif self.is_serial_locked_by_caller(caller_name):
            result = True
        return result

    def try_serial_connection(self, caller_name: str):
        """Try serial connection."""
        return self.ve.try_serial_connection(
            caller_name=caller_name
        )

    def read_data(self,
                  caller_name: str,
                  timeout: int = 2
                  ) -> Optional[dict]:
        """Read data"""
        result = None
        now = time.time()
        self.init_lock_serial(
            caller_name=caller_name
        )
        result, is_cache = self.ve.read_data(
            caller_name=caller_name,
            timeout=timeout
        )
        self.unlock_serial()
        nb_data = 0
        if Ut.is_dict(result, not_null=True):
            nb_data = len(result)
        logger.debug(
            "[VedirectApp::read_data] Read vedirect data."
            "worker: %s - time: %s  - is cache: %s "
            "- data len: %s",
            caller_name,
            now,
            is_cache,
            nb_data
        )
        return result
