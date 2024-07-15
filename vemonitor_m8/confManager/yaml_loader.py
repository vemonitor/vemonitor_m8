"""
Used to load yaml configuration file.

 The module contain two classes:
     - YmlConfLoader: The main class of this module.
     - IncludeImport: Helper used by YmlConfLoader to execute the job.

 It was inspired from part of kaliope project.
     - Project url:
         https://github.com/kalliope-project/kalliope
     - Licence:
         https://github.com/kalliope-project/kalliope/blob/master/LICENSE.md

 .. seealso:: Loader
 .. raises:: YAMLFileNotFound, YAMLFileEmpty, YAMLFileError
"""
import logging
import os
from typing import Optional, Union
import yaml
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.exceptions import \
    YAMLFileNotFound, YAMLFileEmpty, YAMLFileError

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class YmlConfLoader:
    """Simple Class to Verify / Load a YAML file."""

    @classmethod
    def get_config(cls,
                   yaml_file: Optional[str],
                   child_list: Optional[list] = None):
        """
        Load the configuration file.

        It will import all or selected childs configuration files on same path.
        This method is called by the main script and
        it returns a dictionary with all loaded data.

        :param cls:
            Used to Refer to the class itself,
            so that we can call its methods.
        :param yaml_file:strorNone:
            Used to Specify the path to the main configuration file.
        :param child_list:listorNone=None:
            Used to Import only the list of childs
            from a parent configuration file.
        :return: The content of the configuration file.

        :Example:

            YAMLLoader.get_config(file_path)

        .. seealso::  Loader, ConfigLoader
        .. raises:: YAMLFileNotFound
        .. warnings:: Class Method and Public

        :doc-author: Trelent
        """
        cls.file_path_to_load = yaml_file
        logger.debug(
            "File path to load: %s",
            cls.file_path_to_load
        )
        if os.path.isfile(cls.file_path_to_load):
            # import the main configuration file content
            inc_import = IncludeImport(cls.file_path_to_load)
            # import all or selected childs configuration files on same path
            inc_import.import_from_included_files(
                cls.file_path_to_load,
                child_list)

            return inc_import.get_data()
        else:
            raise YAMLFileNotFound(f"File {cls.file_path_to_load} not found")


class IncludeImport:
    """
    Manage the Include Import statement in the brain.yml file.

    To be continued..
    """

    def __init__(self, file_path: Optional[str]) -> None:
        """
        Create object from the IncludeImport class.

        Which is used to initialize two instance variables:
            - data property: store content from yaml configuration files.
            - cumuled_size: property store the cumuled size
              of all configuration files.

        This method run self.get_master_conf(file_path)
        to import the content of master configuration file.

        If master configuration file contains some includes,
        and you want import them content,
        you may call self.get_included_files() method separatly.

        Args:  file_path - The path of the yaml file to load
        Returns: The data attribute of the class

        :param self: Used to Access variables that belongs to the class.
        :param file_path:strorNone: Used to Indicate the path to a file.
        :return: The data attribute of the class.

        :Example:

            > obj = IncludeImport.get_config('/var/lib/config.yaml')
            > obj.get_data()
            > {"KeyConf1": {'childKey1': 'childValue2'} ....}

        .. seealso::  Loader, ConfigLoader, YmlConfLoader
        .. raises:: YAMLFileError, YAMLFileEmpty
        .. warnings:: Class Method and Public

        :doc-author: Trelent
        """
        self.cumuled_size = 0
        self.data = None
        self.get_master_conf(file_path)

    MAX_FILE_SIZE, MAX_TOTAL_SIZE = 500000, 500000

    def get_master_conf(self, file_path: Optional[str]) -> Optional[Union[dict, list]]:
        """
        Take in a file path and returns the loaded data.

        It does this by loading the yaml file into memory,
        checking if it is too big or has an invalid extension,
        and then returning either:
            None,
            a dictionary or
            a list containing all of the data from each section.

        :param self: Used to Access variables that belongs to the class.
        :param file_path:strorNone:
            Used to Specify the path to the file that is going to be loaded.
        :return: None or dictionary or a list.

        :Example:

            > obj = self.get_master_conf('/var/lib/config.yaml')
            > obj.get_data()
            > {"KeyConf1": {'childKey1': 'childValue2'} ....}

        .. seealso::  Loader, ConfigLoader, YmlConfLoader
        .. raises:: YAMLFileError, YAMLFileEmpty
        .. warnings:: Class Method and Public
        :doc-author: Trelent
        """
        self.cumuled_size = 0
        self.data = None
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)

            if file_size <= self.MAX_FILE_SIZE and IncludeImport.is_yaml_ext(file_path):
                self.cumuled_size = file_size
                # load the yaml file
                with open(file_path, "r", encoding="utf-8") as f:
                    self.data = yaml.safe_load(f)
            else:
                raise YAMLFileError(
                    f"[YAMLLoader] File {file_path} is too big ( > 500Mb ) "
                    "and/or have bad file extension ( != .yaml or .yml )."
                )

        if not Ut.is_dict(self.data) and not Ut.is_list(self.data, not_null=True):
            raise YAMLFileEmpty("[YAMLLoader] File {file_path} is empty")

    def _get_included_file_conf(self,
                                file_path: Optional[str],
                                main_path: Optional[str]
                                ) -> Optional[Union[dict, list]]:
        """
        Load the configuration from file_path.

        It takes two arguments:
            - file_path:
                The path of the included file,
                relative to the current configuration file.
            - main_path:
                The path of the current configuration file,
                relative or absolute.

        :param self:
            Used to Reference the class instance from within the class.
        :param file_path:
            Path of the child configuration file that is included.
        :param main_path:
            Path of the main configuration file.
        :return:
            The content of the file included in the main configuration file.

        :Example:

            self._get_included_file_conf(
                'child_conf.yaml',
                '/var/temp/master_conf.yaml')
            > {"KeyConf1": {'childKey1': 'childValue2'} ....}

            'child_conf.yaml' must be in same path of
            '/var/temp/master_conf.yaml'

        .. seealso::  Loader, ConfigLoader, YmlConfLoader
        .. raises:: YAMLFileError
        .. warnings:: Protected

        :doc-author: Trelent
        """
        conf = None
        if Ut.is_str(file_path) and os.path.isfile(main_path):
            # if the path is relative, we add the root path
            # os.path.isabs returns True if the path is absolute
            if not os.path.isabs(file_path):
                # get the parent dir. will be used in case of relative path
                parent_dir = os.path.normpath(main_path + os.sep + os.pardir)
                logger.debug(
                   "File path %s is relative, adding the root path",
                   parent_dir
                )
                file_path = os.path.join(parent_dir, file_path)
                # logger.debug("New path: %s" % inc)

            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)

                if os.path.getsize(file_path) <= self.MAX_FILE_SIZE and\
                        self.cumuled_size < self.MAX_TOTAL_SIZE and\
                        IncludeImport.is_yaml_ext(file_path):

                    self.cumuled_size = self.cumuled_size + file_size

                    with open(file_path, "r", encoding="utf-8") as f:
                        conf = yaml.safe_load(f)
                else:
                    raise YAMLFileError(
                        f"[YAMLLoader] File {file_path} is too big, "
                        "or cumuled files size too big ( < 500Mb ) "
                        "and/or have bad file extension "
                        "( != .yaml or .yml )."
                        )
        return conf

    def get_included_files(self) -> Optional[list]:
        """
        Return a list of files included by the current file.

        The function is intended to be used in conjunction
        with the get_file_data function,
        which returns a dictionary containing data about the current file.
        The returned list contains strings that are names of files
        included by this one.

        :param self: Used to Access variables that belongs to the class.
        :return: A list of files included by the current file.

        :Example:

            self.get_included_files()
            > ['child_conf1.yaml', 'child_conf2.yaml', 'child_conf3.yaml']

        .. seealso::  SettingLoader, BrainLoader, YmlConfLoader
        .. raises:: YAMLFileError
        .. warnings:: Public
        :doc-author: Trelent
        """
        imports = None
        if Ut.is_dict(self.data) and\
                Ut.is_list(self.data.get('Imports'), not_null=True):

            imports = self.data.get('Imports')

        elif Ut.is_list(self.data, not_null=True):
            imports = list()
            for el in self.data:
                if "includes" in el:
                    for inc in el["includes"]:
                        imports.append(inc)

            if not Ut.is_list(imports, not_null=True):
                imports = None

        return imports

    def import_from_included_files(self,
                                   main_path: Optional[str],
                                   child_list: Optional[list] = None
                                   ) -> bool:
        """
        Import the content of a YAML file from another one.

        It is useful when you want to split your configuration
        in multiple files and have some shared data between them.

        The included_files parameter is a list of files that will be imported
        if they exist, it can be either relative or absolute paths.

        The main_path parameter is the path of the main configuration file
        (the one you call import_from_included_files() on).

        :param self:
            Used to Access to the attributes and methods of the class.
        :param main_path:
            Path of the main configuration file
        :param child_list:listorNone=None:
            Used to select the child configuartion files to import.
        :return:
            True if child confifuration file was imported or False.

        :Example:

            > self.import_from_included_files(
                '/var/temp/master_conf.yaml',
                ['child_conf_1.yaml',
                 'child_conf_2.yaml'])
            > obj.get_data()
            > {"KeyConf1": {'childKey1': 'childValue2'} ....}

        .. seealso::  SettingLoader, BrainLoader, YmlConfLoader
        .. raises:: YAMLFileError
        .. warnings:: Public

        :doc-author: Trelent
        """
        imports = self.get_included_files()
        tst = False
        if Ut.is_list(imports, not_null=True):

            logger.info(
                "List of files ready to import : %s", imports)
            for f in imports:
                if not Ut.is_list(child_list, not_null=True) or \
                        (Ut.is_list(child_list, not_null=True) and f in child_list):

                    conf = self._get_included_file_conf(f, main_path)
                    if isinstance(conf, type(self.data)):
                        logger.info(
                            "importing %s conf data in global configuration.",
                            f)
                        tst = True
                        self.update(conf)
                    else:
                        if conf is None:
                            raise YAMLFileNotFound(
                                f"[YAMLLoader] Unable to load child file {f}. "
                                "File don't exist or contain bad content."
                            )
                        raise YAMLFileError(
                            f"[YAMLLoader] the child file {f},"
                            "don't return same data type of father conf."
                            f"child type : {type(conf)}, base : {type(self.data)}"
                        )
        return tst

    def get_data(self) -> Optional[Union[dict, list]]:
        """
        Return the data attribute of the instance.

        :param self:
            Used to Access the class variables from within the function.
        :return:
            The data attribute of the instance.

        :doc-author: Trelent
        """
        return self.data

    def update(self, conf: Optional[Union[dict, list]]) -> bool:
        """
        Add an other Include statement to the original yml file.

        :param conf: the data to add to the current configuration data.
        :return: True id data was update or False
        """
        # we add each conf inside the extended conf data
        if isinstance(conf, type(self.data)) and len(conf) > 0:
            if Ut.is_dict(self.data):
                self.data.update(conf)
                return True

            elif Ut.is_list(self.data):
                self.data = self.data + conf
                return True
        return False

    @staticmethod
    def is_yaml_ext(file_name: str) -> bool:
        """Test if file has yaml extension."""
        f_split = os.path.splitext(file_name)
        return Ut.is_tuple(f_split) and f_split[1] in ['.yaml', '.yml']
