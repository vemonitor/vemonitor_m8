"""
YmlConfLoader Unit Tests class
"""
import os
import inspect
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.confManager.yaml_loader import YmlConfLoader
from vemonitor_m8.core.exceptions import YAMLFileNotFound, YAMLFileError


class TestYmlConfLoader():
    """YmlConfLoader Unit Tests class"""

    @staticmethod
    def get_dummy_conf_path():
        """Get dummy configuration files path for tests."""
        current_script_path = os.path.dirname(
            os.path.abspath(
                inspect.getfile(inspect.currentframe())
            )
        )
        return os.path.join(
            current_script_path,
            "conf"
        )

    def test_file_not_found(self):
        """Test get_config method YAMLFileNotFound Error."""
        with pytest.raises(YAMLFileNotFound):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "not_exist.yaml"
                )
            )

    def test_file_error(self):
        """Test get_config method YAMLFileError Error."""
        with pytest.raises(YAMLFileError):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "dummy_conf_dict_error.yaml"
                )
            )

    def test_get_config(self):
        """Test get_config method."""
        # test importing all child configuration
        conf = YmlConfLoader.get_config(
            os.path.join(
                TestYmlConfLoader.get_dummy_conf_path(),
                "dummy_conf_dict.yaml"
                )
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
            os.path.join(
                TestYmlConfLoader.get_dummy_conf_path(),
                "dummy_conf_dict.yaml"
            ),
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
