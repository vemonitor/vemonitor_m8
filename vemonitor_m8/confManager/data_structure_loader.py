"""
Used to load Data Structure configuration from yaml file.

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
from typing import Optional, Union
from os import path as Opath
from ve_utils.utype import UType as Ut
from vemonitor_m8.confManager.yaml_loader import YmlConfLoader
from vemonitor_m8.confManager.loader import Loader
from vemonitor_m8.core.exceptions import YAMLFileNotFound


logging.basicConfig()
logger = logging.getLogger("vemonitor")



class DataStructureLoader(Loader):
    """
    Used to load Data Structure configuration from yaml file.

    :Example:

        # Initialize ConfigLoader class
        >data_structure = DataStructureLoader(
            file_path="/opt/vemonitor/"
        )

        # get data from files, test the data and return Config class
        >conf = data_structure._get_settings()

    .. seealso:: Loader
    .. raises:: YAMLFileNotFound, NullSettingException, SettingFileNotFound
    """
    def __init__(self,
                  file_names: Optional[Union[str, list, tuple]],
                  file_path: Optional[str]=None
                 ):
        Loader.__init__(self, file_names, file_path)

    def get_yaml_data_structure(self,
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
            current_script_path = Loader.get_current_script_path()
            path = Opath.join(current_script_path, 'confFiles', file_path)
        elif file_path == "userDeviceData.yaml":
            user_path = Opath.dirname(Opath.abspath(self.file_path))
            path = Opath.join(user_path, file_path)

        if Ut.is_str(path) and Opath.isfile(path):
            return YmlConfLoader.get_config(path)
        else:
            raise YAMLFileNotFound(
                "[Loader::get_yaml_data_structure] Fatal Error: "
                "Unable to load columns check configuration file path "
                f"{file_path}"
                )
