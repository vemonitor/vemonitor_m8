# -*- coding: utf-8 -*-
"""Vedirect api Helper"""
import logging
import time
from typing import Union
from vedirect_m8.exceptions import SerialVeTimeoutException
from vedirect_m8.packet_stats import PacketStats
from vedirect_m8.ve_controller import VedirectController
from vedirect_m8.ve_controller import InputReadException
from vedirect_m8.exceptions import VedirectException
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


class VedirectApp:
    """This class is a shared VeDirect Controller Helper."""
    def __init__(self,
                 serial_conf: dict,
                 serial_test: dict,
                 source_name: str = 'VedirectController',
                 auto_start: bool = True,
                 wait_connection: bool = True,
                 wait_timeout: Union[int, float] = 3600):
        self.ve = VedirectController(
            serial_conf=serial_conf,
            serial_test=serial_test,
            source_name=source_name,
            auto_start=auto_start,
            wait_connection=wait_connection,
            wait_timeout=wait_timeout
        )
        self._data_cache = None
        self._serial_lock = False
        self._lock_caller = None
        self._min_source_interval = 1
        self._nb_packets = 4
        self.packets_stats = PacketStats()

    def has_data_cache(self):
        """Test if instance has data_cache"""
        return Ut.is_tuple(self._data_cache)\
            and Ut.is_numeric(self._data_cache[0], not_null=True)\
            and Ut.is_dict(self._data_cache[1], not_null=True)

    def get_time_cache(self):
        """Get data_cache time value"""
        result = None
        if self.has_data_cache():
            result = self._data_cache[0]
        return result

    def get_data_cache(self):
        """Get data_cache value"""
        result = None
        if self.has_data_cache():
            result = self._data_cache[1]
        return result

    def is_time_to_read_serial(self, now: float, min_interval: int = 1):
        """Test if is time to read from serial"""
        result = False
        if self.has_data_cache():
            min_i = Ut.get_int(now)
            max_i = min_i + min_interval
            result = min_i <= self.get_time_cache() <= max_i
            logger.debug(
                "[VedirectApp::is_time_to_read_serial] Evaluate cache validity: %s.\n"
                "%s <= %s < %s",
                result,
                min_i,
                self.get_time_cache(),
                max_i
            )

        return result

    def reset_data_cache(self):
        """Reset data_cache"""
        self._data_cache = None

    def init_data_cache(self,
                        data: dict
                        ) -> bool:
        """Init cache tuple values."""
        result = False
        self._data_cache = None
        if Ut.is_dict(data, not_null=True):
            self._data_cache = (time.time(), data)
            result = True
        return result

    def add_data_cache(self,
                       data: dict
                       ) -> bool:
        """Add data to cache."""
        result = False
        if self.has_data_cache():
            if Ut.is_dict(data, not_null=True):
                self._data_cache[1].update(data)
                result = True
        else:
            result = self.init_data_cache(data)
        return result

    def is_serial_locked(self):
        """Test if serial connexion is locked."""
        return self._serial_lock is True

    def is_serial_locked_by_caller(self, caller_name: str):
        """Test if serial connexion is locked by caller name."""
        return self.is_serial_locked() and self._lock_caller == caller_name

    def lock_serial(self, caller_name):
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

    def init_lock_serial(self, caller_key):
        """Init lock status for serial connexion."""
        result = False
        if not self.is_serial_locked():
            if not self.lock_serial(caller_key):
                raise SettingInvalidException(
                    "[VedirectHelper:init_lock_serial] "
                    "Invalid Caller key. Unable to lock serial port."
                )
            result = True
        elif self.is_serial_locked_by_caller(caller_key):
            result = True
        return result

    def try_serial_connection(self, caller_key: str) -> bool:
        """
        Try to connect to serial port, and run a serial test on it.
        """
        result = False
        if self.init_lock_serial(caller_key):

            try:
                if self.ve.connect_to_serial()\
                        and self.ve.test_serial_port(
                            port=self.ve.get_serial_port()
                        ):
                    logger.info(
                        "Serial port %s is ready. ",
                        self.ve.get_serial_port()
                    )
                    result = True
                    self.unlock_serial()
                else:
                    raise VedirectException
            except VedirectException as ex:
                logger.debug(
                    "[VedirectApp::try_serial_connection] Unable to connect to serial port %s.\n"
                    "ex: %s",
                    self.ve.get_serial_port(),
                    ex
                )
                logger.info("Searching for available serial port.")
                if self.ve.search_serial_port():
                    logger.info(
                        "Find serial port %s. Connected and ready.",
                        self.ve.get_serial_port()
                    )
                    result = True
                    self.unlock_serial()
        else:
            logger.debug(
                "[VedirectApp::try_serial_connection]Serial port is locked by node %s. ",
                self._lock_caller
            )
        return result

    def read_serial_data(self,
                         caller_key: str,
                         timeout: int = 2
                         ) -> dict:
        """
        Get input data from VeDirect controller.
        ToDo:
            - Remove last changes.
            - self.columns may removed :
                - worker may get data at once on serial port
                - then data columns may be chained for every node
                - no one worker by node but one worker by source
        """
        result = None
        read_errors = 0
        max_read_error = 30
        if self.ve.is_ready():
            try:
                timeout = Ut.get_int(timeout, default=2)
                result = self.ve.read_data_single(timeout=timeout)

            except InputReadException as ex:
                if read_errors >= max_read_error:
                    raise VedirectException(
                        "[Vedirect::input_read] "
                        "Serial input read error"
                    ) from ex
                else:
                    logger.debug(
                        "[VedirectApp::read_data] "
                        "Serial read Error n° %s ex : %s",
                        read_errors,
                        ex
                    )
                read_errors += 1

            except (
                    VedirectException,
                    SerialVeTimeoutException
            ) as ex:
                if self.try_serial_connection(caller_key):
                    logger.warning(
                        "[VedirectApp::read_data] "
                        "Serial port disconnected and updated to %s. ex : %s",
                        self.ve.get_serial_port(),
                        ex
                    )
                else:
                    logger.debug(
                        "[VedirectApp::read_data] "
                        "Serial port disconnected, waiting for connection."
                    )
            except Exception as ex:
                logger.error(
                    "[VedirectApp::read_data] Fatal error: "
                    "unable to read data. ex: %s.",
                    ex
                    )
        else:
            self.try_serial_connection(caller_key)
            logger.debug(
                "[VedirectApp::read_data] "
                "Serial port not ready, waiting for connection. name: %s",
                caller_key
            )
        return result

    def get_all_packets(self,
                        caller_key: str,
                        timeout: int = 2
                        ) -> dict:
        """Get packets from serial"""
        result = False
        errors, blocks = 0, []
        self.reset_data_cache()

        for i in range(self.packets_stats.get_nb_packets()):
            self.ve.init_data_read()
            tmp = self.read_serial_data(caller_key, timeout)

            if self.add_data_cache(tmp):
                self.packets_stats.set_loop_packet_stats(i, tmp)
                blocks.append(len(tmp))
                time.sleep(0.005)
            else:
                errors = errors + 1

        if self.has_data_cache():
            self.packets_stats.init_nb_packets()
            result = True
            logger.debug(
                "[VedirectApp::get_serial_packet] Read %s blocks from serial. "
                "len: %s - blocks: %s - errors: %s - time ref: %s \n"
                "result: %s",
                i+1,
                len(self.get_data_cache()),
                blocks,
                errors,
                self.get_time_cache(),
                self.get_data_cache()
            )
        return result

    def read_data(self,
                  caller_key: str,
                  timeout: int = 2
                  ) -> dict:
        """Read data"""
        result = None
        now = time.time()
        logger.debug(
            "[VedirectApp::read_data] Read vedirect data."
            "worker: %s - time: %s",
            caller_key,
            now
        )
        if self.is_time_to_read_serial(now):
            result = self.get_data_cache()
            logger.debug(
                "[VedirectApp::read_data] Read data from cache."
                "worker: %s - time: %s  \n"
                "Time packet: %s \n"
                "Time diff: %s \n",
                caller_key,
                now,
                self.get_time_cache(),
                (self.get_time_cache() - now)
            )
        else:
            self.ve.init_data_read()
            if self.get_all_packets(caller_key, timeout):
                result = self.get_data_cache()
                if 0 < len(result):
                    logger.debug(
                        "[VedirectApp::read_data] Read data from serial. "
                        "worker: %s - time: %s  \n"
                        "Time packet: %s \n"
                        "Time diff: %s \n"
                        "Data Dict: %s \n",
                        caller_key,
                        now,
                        self.get_time_cache(),
                        self.get_time_cache() - now,
                        self.get_data_cache()
                    )
                else:
                    logger.debug(
                        "[VedirectApp::read_data] Success read from serial. "
                        "Time packet: %s \n"
                        "Time diff: %s \n",
                        self.get_time_cache(),
                        self.get_time_cache() - now
                    )
        return result
