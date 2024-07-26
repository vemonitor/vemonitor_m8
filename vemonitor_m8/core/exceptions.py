# -*- coding: utf-8 -*-
"""
Exceptions classes
"""


class VeMonitorError(Exception):
    """
    Settings file has not been found
    """

# ----------------
# Settings Loader Conf
# ----------------


class SettingsError(VeMonitorError):
    """
    Settings Error
    """


class SettingFileNotFound(SettingsError):
    """
    Settings file has not been found
    """


class SettingInvalidException(SettingsError):
    """
    Some data must match the expected value/type

    .. seealso:: Settings
    """


class NullSettingException(SettingsError):
    """
    Some Attributes can not be Null

    .. seealso:: Settings
    """


class SettingNotFound(SettingsError):
    """
    Some Attributes are missing

    .. seealso:: Settings
    """

# ----------------
# YAML Loader Conf
# ----------------


class LoadYamlError(VeMonitorError):
    """
    Settings Error
    """


class YAMLFileNotFound(LoadYamlError):
    """
    YAML file has not been found
    """


class YAMLFileEmpty(LoadYamlError):
    """
    YAML file empty
    """


class YAMLFileError(LoadYamlError):
    """
    YAML file empty
    """

# ----------------
# Device data check configuration
# ----------------


class DeviceDataError(VeMonitorError):
    """
    Device data check error
    """


class DeviceDataConfError(DeviceDataError):
    """
    Device data check configuration error
    """


class DeviceInputValueError(DeviceDataError):
    """
    Device Input Value Error
    """


class DeviceOutputValueError(DeviceDataError):
    """
    Device Output Value Error
    """

# ----------------
# Serial Com
# ----------------


class DataCacheError(VeMonitorError):
    """
    DataCache error
    """

# ----------------
# Serial Com
# ----------------


class SerialError(VeMonitorError):
    """
    Serial error
    """


class SerialConnectionException(SerialError):
    """
    Serial Connection error
    """


class SerialWriteException(SerialError):
    """
    VeDirect data conversion error
    """


# ----------------
# Redis
# ----------------
class RedisVeError(VeMonitorError):
    """
    Redis error
    """


class RedisConnectionException(RedisVeError):
    """
    Redis Connection error
    """


# ----------------
# Workers
# ----------------
class WorkerException(VeMonitorError):
    """
    Worker error
    """
