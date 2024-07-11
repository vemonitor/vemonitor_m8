#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
import os
import inspect
from vemonitor_m8.confManager.loader import Loader
from vemonitor_m8.core.exceptions import YAMLFileNotFound
from ve_utils.utype import UType as Ut
from ve_utils.usys import USys as USys


class TestLoader():

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
        self.obj = None

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

    def test_file_not_found(self):
        file_names = ['nofile.yaml']
        with pytest.raises(YAMLFileNotFound):
            Loader(file_names)

    def test_get_yaml_config(self):
        """"""
        file_names = ['dummy_conf_dict.yaml']
        self.obj = Loader(file_names, file_path=self.test_path)
        self.obj.set_file_path(file_name=file_names, path=self.test_path)

        conf = self.obj.get_yaml_config()
        assert Ut.is_dict(conf) and len(conf) == 7 and \
            len(conf.get('Imports')) == 2 and \
            len(conf.get('Dummy_1')) == 2 and\
            len(conf.get('Dummy_2')) == 2 and\
            len(conf.get('Dummy_3')) == 2 and\
            len(conf.get('Dummy_4')) == 2 and\
            len(conf.get('Dummy_5')) == 2 and\
            len(conf.get('Dummy_6')) == 2

        conf = self.obj.get_yaml_config(['dummy_conf_dict1.yaml'])
        assert Ut.is_dict(conf) and len(conf) == 5 and \
            len(conf.get('Imports')) == 2 and \
            len(conf.get('Dummy_1')) == 2 and\
            len(conf.get('Dummy_2')) == 2 and\
            len(conf.get('Dummy_3')) == 2 and\
            len(conf.get('Dummy_4')) == 2 and\
            conf.get('Dummy_5') is None and\
            conf.get('Dummy_6') is None

    def test_get_yaml_columns_check(self):
        file_names = ['dummy_conf_dict.yaml']
        self.obj = Loader(file_names, file_path=self.test_path)

        assert Ut.is_dict(self.obj.get_yaml_columns_check())

        with pytest.raises(YAMLFileNotFound):
            self.obj.get_yaml_columns_check("userColumnsChecks.yaml")
