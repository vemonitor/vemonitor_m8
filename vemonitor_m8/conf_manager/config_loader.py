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
import time
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.models.settings.config import Config
from vemonitor_m8.conf_manager.schema_validate import SchemaValidate as sValid
from vemonitor_m8.conf_manager.config_loader_helper import ConfigLoaderHelper as cHelp
from vemonitor_m8.conf_manager.data_structure_loader import DataStructureLoader
from vemonitor_m8.core.exceptions import NullSettingException, YAMLFileNotFound

logging.basicConfig()
logger = logging.getLogger("vemonitor")



class ConfigLoader(DataStructureLoader):
    """Used to get the Config settings as an object."""

    FILE_NAMES = ("vm_conf.yaml", "dummy_g_conf.yaml", "vemonitor.yaml")

    def __init__(self, file_path=None):
        DataStructureLoader.__init__(self, self.FILE_NAMES, file_path)

    def _get_settings_from_file(self,
                                child_list: Optional[list] = None,
                                keys_list: Optional[list] = None,
                                ) -> dict:
        """Load config from file"""
        # Import the configuration from yaml files
        imp_conf = self.get_yaml_config(child_list)
        # Remove unused configuration keys
        if Ut.is_list(keys_list, not_null=True):
            imp_conf = Ut.get_items_from_dict(imp_conf, keys_list)

        return imp_conf

    def set_settings_from_files(self,
                                child_list: Optional[list] = None,
                                keys_list: Optional[list] = None,
                                app_name: Optional[str] = None,
                                block_name: Optional[str] = None
                                ):
        """Set configuration settings from files."""
        # Import the configuration from yaml files
        imp_conf = self._get_settings_from_file(child_list, keys_list)

        output = Config()
        if Ut.is_list(imp_conf.get('Imports'), not_null=True):
            sValid.validate_data(imp_conf.get('Imports'), "imports")

        if Ut.is_list(imp_conf.get('appBlocks'), not_null=True):
            output.set_app_blocks(
                cHelp.get_app_blocks_by_app_or_name(
                    imp_conf.pop('appBlocks'),
                    block_name = block_name,
                    app_name = app_name
                )
            )

        if Ut.is_dict(imp_conf.get('appConnectors'), not_null=True):
            output.set_app_connectors(
                cHelp.get_app_connectors_from_sources(
                    imp_conf.pop('appConnectors'),
                    output.get_app_blocks_sources()
                    )
            )

        output.set_battery_banks(
            cHelp.get_app_blocks_args_objects(
                app_blocks=output.app_blocks,
                conf=imp_conf
            )
        )

        return output

    def get_settings_from_schema(self,
                                 child_list: Optional[list] = None,
                                 keys_list: Optional[list] = None,
                                 app_name: Optional[str] = None,
                                 block_name: Optional[str] = None
                                 ) -> Config:
        """
        Get, validate and compile configuration settings.

        Obtain the main configuration yaml file, whose :
            - name is defined in the global variable FILE_NAMES
            - a path can be defined in file_path ConfigLoader constructor properties.
              if file_path is absolute, then we try to get the full path from
              file_path + FILE_NAMES.
              Eg: /file_path/vm_conf.yaml
              else we try to get the full path in this order :
                - from the current directory where vemonitor has been called,
                  + the file_path + FILE_NAMES
                  Eg: /home/me/Documents/vm_conf.yaml
                - from /etc/vemonitor + file_path + FILE_NAMES
                  Eg: /etc/vemonitor/vm_conf.yaml
                - from the root of the project + FILE_NAMES
                  Eg: /project_root/vm_conf.yaml

        Use child_list to filter which secondary files to import, and
        keys_list to filter root keys in the imported dictionary.

        Data from yaml files is validated using jsonschema.
        Then the filtered and compiled data is validated a second time,
        with the jsonschema.

        The returned Config object contains :
            - appBlocks, filtered with app_name and block_name.
            - appConnectors, present on the appBlocks inputs/outputs.
            - compiled appBlocks args objects.
            - columns Checkers filtered from appBlocks inputs/outputs columns.


        :param child_list: used to filter which secondary files to import
        :param keys_list: used to filter root keys on imported dictionary data
        :param app_name: used to filter appBlocks
        :param block_name: used to filter appBlocks
        :return: Config object with all configuration settings compiled.

        .. raises:: YAMLFileNotFound, YAMLFileEmpty, YAMLFileError,
                    SettingInvalidException, NullSettingException, YAMLFileNotFound
        """
        now = time.time()
        logger.debug("Start loading configuration from yaml.")

        output = self.set_settings_from_files(
            child_list=child_list,
            keys_list=keys_list,
            app_name=app_name,
            block_name=block_name
        )

        data_structure = self.get_yaml_data_structure(file_path="victronDeviceData.yaml")
        app_blocks_columns = output.get_app_blocks_columns()
        filtered_checks = cHelp.get_data_structure(
            data_structure=data_structure,
            points = app_blocks_columns
            )

        try:
            # get columns checks from user file
            data_structure = self.get_yaml_data_structure(file_path="userColumnsChecks.yaml")
            filtered_checks.update(cHelp.get_data_structure(
                data_structure=data_structure,
                points=app_blocks_columns
                ))
        except NullSettingException:
            pass
        except YAMLFileNotFound:
            pass

        output.set_data_structures(filtered_checks)
        logger.info(
            "Load and validate, configuration data, completed in %ss.",
            round(time.time()-now, 6)
        )
        return output
