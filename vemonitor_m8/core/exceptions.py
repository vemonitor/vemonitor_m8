# -*- coding: utf-8 -*-

# ----------------
# Settings Loader Conf
# ----------------
class SettingFileNotFound(Exception):
    """
    Settings file has not been found
    """
    pass

class SettingInvalidException(Exception):
    """
    Some data must match the expected value/type

    .. seealso:: Settings
    """
    pass


class NullSettingException(Exception):
    """
    Some Attributes can not be Null

    .. seealso:: Settings
    """
    pass


class SettingNotFound(Exception):
    """
    Some Attributes are missing

    .. seealso:: Settings
    """
    pass

# ----------------
# YAML Loader Conf
# ----------------
class YAMLFileNotFound(Exception):
    """
    YAML file has not been found
    """
    pass


class YAMLFileEmpty(Exception):
    """
    YAML file empty
    """
    pass

class YAMLFileError(Exception):
    """
    YAML file empty
    """
    pass

# ----------------
# Serial Com
# ----------------
class SerialConnectionException(Exception):
    """
    Serial Connection error
    """
    pass

class SerialWriteException(Exception):
    """
    VeDirect data conversion error
    """
    pass