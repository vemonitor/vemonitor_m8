# -*- coding: utf-8 -*-
"""
Exceptions classes
"""
# ----------------
# Settings Loader Conf
# ----------------
class SettingFileNotFound(Exception):
    """
    Settings file has not been found
    """

class SettingInvalidException(Exception):
    """
    Some data must match the expected value/type

    .. seealso:: Settings
    """


class NullSettingException(Exception):
    """
    Some Attributes can not be Null

    .. seealso:: Settings
    """


class SettingNotFound(Exception):
    """
    Some Attributes are missing

    .. seealso:: Settings
    """

# ----------------
# YAML Loader Conf
# ----------------
class YAMLFileNotFound(Exception):
    """
    YAML file has not been found
    """


class YAMLFileEmpty(Exception):
    """
    YAML file empty
    """

class YAMLFileError(Exception):
    """
    YAML file empty
    """

# ----------------
# Serial Com
# ----------------
class SerialConnectionException(Exception):
    """
    Serial Connection error
    """

class SerialWriteException(Exception):
    """
    VeDirect data conversion error
    """


# ----------------
# Redis
# ----------------
class RedisConnectionException(Exception):
    """
    Redis Connection error
    """


# ----------------
# Workers
# ----------------
class WorkerException(Exception):
    """
    Worker error
    """
