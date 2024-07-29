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
from vemonitor_m8.conf_manager.yaml_loader import YmlConfLoader
from vemonitor_m8.core.exceptions import YAMLFileNotFound

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class Loader():
    """
    This Class is used to be
    """
    def __init__(self,
                 file_names: Union[str, list, tuple],
                 file_path: Optional[str] = None
                 ):
        self.settings = None
        self.file_path = None
        self.set_file_path(
            file_name=file_names,
            base_path=file_path
        )

    def set_file_path(self,
                      file_name: Union[str, list, tuple],
                      base_path: Optional[str] = None
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
        if not Ut.is_str(base_path, not_null=True)\
                or not os.path.isdir(base_path):
            base_path = None

        if Ut.is_str(file_name):
            if Ut.is_str(base_path):
                gpath = os.path.join(base_path, file_name)
                if os.path.isfile(gpath):
                    self.file_path = gpath

            if self.file_path is None:
                self.file_path = Loader.get_real_file_path(file_name)

        elif Ut.is_tuple(file_name) or Ut.is_list(file_name):
            tmp = None
            for name in file_name:
                if Ut.is_str(base_path):
                    tmp = os.path.join(base_path, name)
                    if os.path.isfile(tmp):
                        self.file_path = tmp
                        break

                if tmp is None:
                    tmp = Loader.get_real_file_path(name)

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
        Loads the provided YAML file from self.file_path
        and return it as a dict or list.

        In the main configuration file, child import can be done.
        Result is list or dict of configuration files content
        and batteryBank.yaml content if exist on same path.

        :Example :
            >>> config_yaml = self.get_yaml_config(
                child_list=['batteryBank.yaml']
            )
            >>> {...} # Content of yaml files (result can be a list)
        :param child_list: list or None: List of yaml file names to import,
            others are not.
        :return: list dict or None: The loaded YAML data
        """
        return YmlConfLoader.get_config(self.file_path, child_list)

    @staticmethod
    def get_real_file_path(file_path: Optional[str]) -> Optional[str]:
        """
            Try to return a full path from a given <file_path>
            If the path is an absolute on, we return it directly.

            If the path is relative, we try to get the full path in this order:
            - from the current directory where vemonitor has been called
                + the file_path.
            Eg: /home/me/Documents/vemonitor_config
            - from /etc/vemonitor + file_path
            - from the default file passed as <file_name>
                at the root of the project

            :param file_path file path to test
            :type file_path: str
            :return: absolute path to the file file_path
                or None if is doen't exist
        """
        result = None
        # ToDo: data must be sanitized
        if not os.path.isabs(file_path):

            paths_order = Loader.get_paths_order()

            for current_path in paths_order:
                sel_path = os.path.join(current_path, file_path)
                if os.path.isfile(sel_path):
                    logger.debug("File found in %s", current_path)
                    result = sel_path
                    break

        else:
            if os.path.isfile(file_path):
                result = file_path
        return result

    @staticmethod
    def get_current_script_path() -> str:
        """Get Current script path"""
        return os.path.dirname(
            os.path.abspath(
                inspect.getfile(inspect.currentframe())
            )
        )

    @staticmethod
    def get_paths_order() -> list:
        """Get Paths order to load config."""
        return [
            # Only linux
            os.path.join(os.path.sep, "opt", "vemonitor_m8", "conf"),
            os.path.join(os.path.sep, "opt", "vemonitor", "conf"),
            # Linux  and/or windows
            Usys.get_current_file_parent_parent_path(
                Loader.get_current_script_path()
            ),
            os.path.join(
                os.path.abspath(
                    os.path.expanduser("~")
                ),
                ".vemonitor"
            ),
            os.path.abspath(os.getcwd()),
        ]
