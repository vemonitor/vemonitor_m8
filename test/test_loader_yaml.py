#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
import os
import inspect
from vemonitor_m8.confManager.loaderYaml import YmlConfLoader
from vemonitor_m8.core.exceptions import YAMLFileNotFound, YAMLFileEmpty, YAMLFileError
from ve_utils.utype import UType as Ut


class TestLoaderYaml():

    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        current_script_path = os.path.dirname(
            os.path.abspath(
                inspect.getfile(inspect.currentframe())
            )
        )
        self.test_path = os.path.join(
            current_script_path,
            "conf"
        )

    def test_file_not_found(self):
        with pytest.raises(YAMLFileNotFound):
            YmlConfLoader.get_config(
                os.path.join(self.test_path, "not_exist.yaml")
            )
    
    def test_file_error(self):
        with pytest.raises(YAMLFileError):
            YmlConfLoader.get_config(
                os.path.join(self.test_path, "dummy_conf_dict_error.yaml")
            )

    def test_get_config(self):
        """"""
        current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        current_script_path = current_script_path + os.sep + "conf" + os.sep
        # test importing all child configuration
        conf = YmlConfLoader.get_config(
            os.path.join(self.test_path, "dummy_conf_dict.yaml")
        )
        assert Ut.is_dict(conf) and len(conf) == 7 and \
               len(conf.get('Imports')) == 2 and \
               len(conf.get('Dummy_1')) == 2 and\
               len(conf.get('Dummy_2')) == 2 and\
               len(conf.get('Dummy_3')) == 2 and\
               len(conf.get('Dummy_4')) == 2 and\
               len(conf.get('Dummy_5')) == 2 and\
               len(conf.get('Dummy_6')) == 2
        
        # test importing all child configuration
        conf = YmlConfLoader.get_config(
            os.path.join(self.test_path, "dummy_conf_dict.yaml"),
            ['dummy_conf_dict1.yaml']
        )
        assert Ut.is_dict(conf) and len(conf) == 5 and \
               len(conf.get('Imports')) == 2 and \
               len(conf.get('Dummy_1')) == 2 and\
               len(conf.get('Dummy_2')) == 2 and\
               len(conf.get('Dummy_3')) == 2 and\
               len(conf.get('Dummy_4')) == 2 and\
               conf.get('Dummy_5') is None and\
               conf.get('Dummy_6') is None

