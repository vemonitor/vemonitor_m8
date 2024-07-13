#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Used to load yaml configuration from files.

 It was inspired from part of kaliope project.
     - Project url:
         https://github.com/kalliope-project/kalliope
     - Licence:
         https://github.com/kalliope-project/kalliope/blob/master/LICENSE.md

 .. seealso:: Loader
 .. raises:: YAMLFileNotFound, YAMLFileEmpty, YAMLFileError
"""
import os
import inspect
import logging
from typing import Optional, Union
from ve_utils.utype import UType as Ut
from ve_utils.usys import USys as Usys
from vemonitor_m8.confManager.loaderYaml import YmlConfLoader
from vemonitor_m8.core.exceptions import YAMLFileNotFound

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "GPLv3"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class Loader():
    """
    This Class is used to be 
    """
    def __init__(self,
                 file_names: Optional[Union[str, list, tuple]],
                 file_path: Optional[str]=None
                 ):
        self.settings = None
        self.file_path = None
        self.set_file_path(file_names, file_path)

    def get_real_file_path(self, file_path: Optional[str]) -> Optional[str]:
        """
            Try to return a full path from a given <file_path>
            If the path is an absolute on, we return it directly.

            If the path is relative, we try to get the full path in this order:
            - from the current directory where vemonitor has been called + the file_path.
            Eg: /home/me/Documents/vemonitor_config
            - from /etc/vemonitor + file_path
            - from the default file passed as <file_name> at the root of the project

            :param file_path file path to test
            :type file_path: str
            :return: absolute path to the file file_path or None if is doen't exist
        """
        if not os.path.isabs(file_path):
            current_script_path = os.path.dirname(
                os.path.abspath(
                    inspect.getfile(inspect.currentframe())
                )
            )

            path_order = {
                1: os.path.join(os.getcwd(), file_path),
                2: os.path.join("opt", "vemonitor", "conf", file_path),
                3: os.path.join("etc", "vemonitor", "conf", file_path),
                # In this case 'get_current_file_parent_parent_path' is corresponding
                # to vemonitor root path
                # from /an/unknown/path/vemonitor/vemonitor/confManager/loader
                # to /an/unknown/path/vemonitor/vemonitor
                4: os.path.join(
                    Usys.get_current_file_parent_parent_path(
                        current_script_path
                    ),
                    file_path
                )
            }

            for key in sorted(path_order):
                new_file_path = path_order[key]
                if os.path.isfile(new_file_path):
                    logger.debug("File found in %s", new_file_path)
                    return new_file_path

        else:
            if os.path.isfile(file_path):
                return file_path

    def set_file_path(self,
                      file_name: Optional[Union[str, list, tuple]],
                      path: Optional[str]=None
                      ):
        """
            Used to set the file path of a given file.
            The function takes one argument, which is either
            a string or list/tuple of strings.
            If the argument is a string, it will be interpreted
            as an absolute or relative path to a file that exists
            on disk. If the argument is a tuple/list,
            each item in that list must be either another tuple/list
            containing multiple strings
            (e.g., ['file_name', 'sub_dir', 'etc']), 
            or just one string (e.g., ['file_name']).
            The first item in this nested structure must be 
            the name of an existing file somewhere on disk;
            if there are more than one items in this nested
            structure then any number of them can be passed 
            and they will all attempt to be joined together
            into one full path by os-specific rules for joining paths together;
            if there are no items then only os-specific rules
            for joining paths together will apply and nothing else.
            
            :param self: Used to Access variables that belongs to the class.
            :param file_name: Used to Set the file path.
            :return: The file path of the file name that is passed in.
        
            :doc-author: Trelent
        """
        self.file_path = None
        if Ut.is_str(path) and not os.path.isdir(path):
            path = None

        if Ut.is_str(file_name):
            if Ut.is_str(path):
                gpath = os.path.join(path, file_name)
                if os.path.isfile(gpath):
                    self.file_path = gpath

            if self.file_path is None:
                self.file_path = self.get_real_file_path(file_name)

        elif Ut.is_tuple(file_name) or Ut.is_list(file_name):
            tmp = None
            for name in file_name:
                if Ut.is_str(path):
                    tmp = os.path.join(path, name)
                    if os.path.isfile(tmp):
                        self.file_path = tmp
                        break

                if tmp is None:
                    tmp = self.get_real_file_path(name)

                    if Ut.is_str(tmp) and os.path.isfile(tmp):
                        self.file_path = tmp
                        break

        # if the returned file path is none, the file doesn't exist
        if self.file_path is None:
            raise YAMLFileNotFound(
                "[Loader::set_file_path] Fatal Error: "
                "Unable to set configuration file path "
                f"for file_name {file_name}"
                )

    def get_yaml_config(self,
                        child_list: Optional[list] = None
                        ) -> Optional[Union[dict, list]]:
        """
            Class Methods which loads the provided YAML file
            from self.file_path and return it as a dict or list.
            In the main configuaration file, child import can be done.

            :return: The loaded config YAML
            :rtype: list dict or None

            :Example:
                config_yaml = Loader.get_yaml_config(['batteryBank.yaml'])
                Result is list or dict of main configuartion file
                content and batteryBank.yaml content if exist on same path.
            .. warnings:: Class Method
        """
        return YmlConfLoader.get_config(self.file_path, child_list)

    def get_yaml_columns_check(self,
                               file_path: Optional[str]=None
                               ) -> Optional[Union[dict, list]]:
        """
            Class Methods which loads the provided YAML 
            file from self.file_path and return it as a dict or list.
            In the main configuaration file, child import can be done.

            :return: The loaded config YAML
            :rtype: list dict or None

            :Example:
                config_yaml = Loader.get_yaml_config(['batteryBank.yaml'])
                Result is list or dict of main configuartion file content
                and batteryBank.yaml content if exist on same path.
            .. warnings:: Class Method
        """
        main_files = ['victronDeviceData.yaml']
        path = None
        if file_path is None:
            file_path = 'victronDeviceData.yaml'

        if file_path in main_files:
            current_script_path = os.path.dirname(
                os.path.abspath(
                    inspect.getfile(inspect.currentframe())
                )
            )
            path = os.path.join(current_script_path, 'confFiles', file_path)
        elif file_path == "userColumnsChecks.yaml":
            user_path = os.path.dirname(os.path.abspath(self.file_path))
            path = os.path.join(user_path, file_path)

        if Ut.is_str(path) and os.path.isfile(path):
            return YmlConfLoader.get_config(path)
        else:
            raise YAMLFileNotFound(
                "[Loader::get_yaml_columns_check] Fatal Error: "
                "Unable to load columns check configuration file path "
                f"{file_path}"
                )
