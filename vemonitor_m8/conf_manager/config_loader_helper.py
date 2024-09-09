#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Used to load configuration from yaml file.

 :Example:

    # Initialize ConfigLoader class
    >loader = ConfigLoader(
        file_path="/opt/vemonitor/"
     )

    # get data from files, test the data and return Config class
    >conf = loader._get_settings()

 .. seealso:: Loader
 .. raises:: YAMLFileNotFound, NullSettingException, SettingFileNotFound
"""


import logging

from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.shema_validate_selector import SchemaValidateSelector as jValid
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.core.exceptions import NullSettingException

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class ConfigLoaderHelper:
    """Used to get the Config settings as an object."""

    @classmethod
    def get_app_blocks_by_app_or_name(cls,
                                      app_blocks: list,
                                      block_name: Optional[str] = None,
                                      app_name: Optional[str] = None
                                      ) -> Optional[dict]:
        """Get AppBlocks from config by app or by name."""
        res = None
        if Ut.is_list(app_blocks, not_null=True)\
                and jValid.is_valid_app_blocks_conf(app_blocks):
            res = []
            for block in app_blocks:
                if Ut.is_dict(block, not_null=True):
                    if Ut.is_str(block_name)\
                            and Ut.is_str(app_name)\
                            and block.get('name') == block_name\
                            and block.get('app') == app_name:
                        res.append(block)
                    elif Ut.is_str(block_name)\
                            and not Ut.is_str(app_name)\
                            and block.get('name') == block_name:
                        res.append(block)
                    elif Ut.is_str(app_name)\
                            and not Ut.is_str(block_name)\
                            and block.get('app') == app_name:
                        res.append(block)
                    elif not Ut.is_str(block_name) and not Ut.is_str(app_name):
                        res.append(block)
        return res

    @classmethod
    def get_middlewares_objects_from_conf(cls,
                                   middlewares: dict,
                                   conf: dict
                                   ) -> Optional[dict]:
        """Get middlewares data from config."""
        obj = None
        if Ut.is_dict(middlewares, not_null=True) and Ut.is_dict(conf, not_null=True):
            obj = {}
            for key, arg in middlewares.items():
                if Ut.is_str(key) and Ut.is_str(arg):
                    if key == 'batteryBanks':
                        obj[arg] = cls.get_battery_bank_from_mid(
                            arg,
                            conf.get(key)
                        )

        return obj

    @classmethod
    def get_app_blocks_middlewares_objects(cls,
                                    app_blocks: list,
                                    conf: dict
                                    ) -> Optional[dict]:
        """Get App Blocks middlewares data from config."""
        obj = None
        if jValid.is_valid_app_blocks_conf(app_blocks)\
                and Ut.is_dict(conf, not_null=True):
            obj = {}
            for block in app_blocks:
                if Ut.is_dict(block, not_null=True):
                    obj.update(
                        cls.get_middlewares_objects_from_conf(block.get('middlewares'), conf)
                    )
        return obj

    @classmethod
    def get_app_conector_from_source(cls,
                                     conector: dict,
                                     sources: list
                                     ) -> Optional[dict]:
        """Get App Connector Item data from config."""
        res = None
        if Ut.is_dict(conector, not_null=True)\
                and Ut.is_list(sources, not_null=True):
            res = {}
            for item_key, item in conector.items():
                if Ut.is_dict(item) and\
                        item_key in sources:  # and key == item_key:
                    res[item_key] = item
            if not Ut.is_dict(res, not_null=True):
                raise SettingInvalidException(
                    "Fatal Error: unable to get appConnectors from sources, "
                    "validation fails or bad root key. ")
        else:
            raise SettingInvalidException(
                "Fatal Error: unable to get appConnectors from sources, "
                "conectors and/or sources list are empty. "
            )
        return res

    @classmethod
    def get_app_connectors_from_sources(cls,
                                        app_conectors: dict,
                                        sources: Optional[dict] = None
                                        ) -> Optional[dict]:
        """Get App Connectors data from config."""
        res = None
        if jValid.is_valid_app_connectors_conf(app_conectors):
            if Ut.is_dict(sources, not_null=True):
                sources_keys = list(sources.keys())
                res = {}
                for key, conector in app_conectors.items():
                    if not Ut.is_dict(conector, not_null=True):
                        raise SettingInvalidException(
                            "Fatal Error: "
                            "unable to get appConnectors from sources, "
                            "conector key {key} is not valid. "
                        )

                    if key in sources_keys:
                        res[key] = cls.get_app_conector_from_source(
                            conector,
                            sources.get(key)
                        )
            else:
                return app_conectors
        else:
            pass

        sources_keys = None
        return res

    @classmethod
    def is_battery_banks(cls, battery_bank: dict) -> bool:
        """Test if is valid battery banks data."""
        return Ut.is_dict(battery_bank, not_null=True) and \
            Ut.is_dict(battery_bank.get('batteryDatas'), not_null=True)

    @classmethod
    def is_battery_banks_items(cls, battery_bank: dict) -> bool:
        """Test if is valid battery banks items data."""
        return cls.is_battery_banks(battery_bank)\
            and Ut.is_dict(
                battery_bank['batteryDatas'].get('bankItems'),
                not_null=True)

    @classmethod
    def is_battery_banks_items_key(cls,
                                   key: str,
                                   battery_bank: dict
                                   ) -> bool:
        """Test if is valid battery banks items key."""
        return cls.is_battery_banks_items(battery_bank) and \
            Ut.is_str(key) and\
            Ut.is_dict(
                battery_bank['batteryDatas']['bankItems'].get(key),
                not_null=True)

    @classmethod
    def get_battery_banks_items_key(cls,
                                    key: str,
                                    battery_bank: dict
                                    ) -> Optional[dict]:
        """Get battery banks items key."""
        result = None
        if cls.is_battery_banks_items_key(key, battery_bank):
            result = battery_bank['batteryDatas']['bankItems'].get(key)
        return result

    @classmethod
    def is_battery_items(cls, battery_bank: dict) -> bool:
        """Test if is valid battery items."""
        return cls.is_battery_banks(battery_bank)\
            and Ut.is_dict(
                battery_bank['batteryDatas'].get('batteries'),
                not_null=True)

    @classmethod
    def is_battery_items_key(cls,
                             key: str,
                             battery_bank: dict
                             ) -> bool:
        """Test if is valid battery items key."""
        return cls.is_battery_items(battery_bank) and \
            Ut.is_str(key) and\
            Ut.is_dict(
                battery_bank['batteryDatas']['batteries'].get(key),
                not_null=True)

    @classmethod
    def get_battery_items_key(cls,
                              key: str,
                              battery_bank: dict
                              ) -> dict:
        """Get battery items key."""
        if cls.is_battery_items_key(key, battery_bank):
            return battery_bank['batteryDatas']['batteries'].get(key)

    @classmethod
    def set_battery_item(cls,
                         key: str,
                         battery: dict,
                         battery_bank: dict
                         ) -> dict:
        """Set battery item."""
        return {
            **battery_bank,
            'name': key,
            'battery': battery
        }

    @classmethod
    def get_battery_bank_from_mid(cls,
                                  arg: str,
                                  battery_bank: dict
                                  ) -> Optional[dict]:
        """Get battery banks from middlewares data config."""
        if jValid.is_valid_battery_banks_conf(battery_bank):
            bank = cls.get_battery_banks_items_key(arg, battery_bank)
            if Ut.is_dict(bank, not_null=True)\
                    and Ut.is_str(bank.get('battery_key')):

                battery = cls.get_battery_items_key(
                    bank.get('battery_key'),
                    battery_bank
                )
                if Ut.is_dict(battery, not_null=True):
                    return cls.set_battery_item(arg, battery, bank)
                else:
                    raise SettingInvalidException(
                        "Fatal Error: unable to get battery data, "
                        f"from arg {bank.get('battery_key')} "
                        f"in batteryBank key {arg}."
                    )
            else:
                raise SettingInvalidException(
                    "Fatal Error: unable to get batteryBank data, "
                    f"from arg {arg}."
                )
        else:
            raise SettingInvalidException(
                "Fatal Error: unable to get batteryBank data, "
                "validation fails or bad root key. "
                f"arg: {arg}."
            )

    @classmethod
    def _is_filtered_key(cls,
                         key: str,
                         check_keys: Optional[list] = None
                         ) -> bool:
        """Test if is filtered key."""
        return not Ut.is_list(check_keys, not_null=True)\
            or (
                Ut.is_list(check_keys, not_null=True)
                and Ut.is_str(key, not_null=True)
                and key in check_keys)

    @classmethod
    def _check_column_keys(cls,
                           data: dict,
                           check_keys: Optional[list] = None
                           ) -> bool:
        """Check columns keys."""
        res = None
        if Ut.is_dict(data):
            res = {}
            for key, item in data.items():
                if Ut.is_list(item, not_null=True):

                    if not Ut.is_list(res.get(key)) and\
                            cls._is_filtered_key(key, check_keys):
                        res[key] = []

                    for item_key in item:
                        if cls._is_filtered_key(key, check_keys):
                            res[key].append(item_key)
                        else:
                            raise SettingInvalidException(
                                "Error on Device Data Structure configuration,"
                                f" checks Key {key} is not valid: {item}"
                            )
                else:
                    raise SettingInvalidException(
                            "Error on Device Data Structure configuration, "
                            f"column key {key} is not valid"
                            "and/or check keys not a list. "
                            f"type(checksKeys): {type(item)}"
                        )
        else:
            raise SettingInvalidException(
                "Error on Device Data Structure configuration, "
                "empty columns keys data: "
            )

        return res

    @classmethod
    def _check_column_points(cls,
                             data: dict,
                             points: Optional[list] = None
                             ) -> Optional[dict]:
        """
            Helper function that checks the input configuration for appBlocks.
            It is called by the _is_app_blocks method
            and takes two arguments: key, data.
            The key argument is a string
            containing the name of an input connector
            (i.e., serial or redis).
            The data argument is a dictionary containing all of the settings
            for that specific input connector.

            :param self: Reference the class instance
            :param key: Check if the input is valid
            :param data: Check the data in the input key
            :return:
                True if the key is a valid app connector and the data is a dict
            :doc-author: Trelent
        """
        res = None
        if Ut.is_dict(data, not_null=True):
            res = {}
            for key, item in data.items():
                if Ut.is_dict(item, not_null=True)\
                        and cls._is_filtered_key(key, points):
                    res[key] = item
        else:
            raise SettingInvalidException(
                "Error on checkColumns configuration, "
                "empty columns keys data: "
            )

        return res

    @classmethod
    def get_data_structure(cls,
                           data_structure: dict,
                           check_keys: Optional[list] = None,
                           points: Optional[list] = None
                           ) -> Optional[dict]:
        """Get Data Structure Config."""
        res = None
        if jValid.is_valid_data_structure_conf(data_structure):
            res = {}
            res['devices'] = cls._check_column_keys(
                data=data_structure.get('devices'),
                check_keys=check_keys
            )

            res['points'] = cls._check_column_points(
                data=data_structure.get('points'),
                points=points
            )
        else:
            raise NullSettingException(
                "Error on appBlocks configuration settings, "
                f"data must be a dict. type(appBlocks): {type(data_structure)}"
            )
        return res
