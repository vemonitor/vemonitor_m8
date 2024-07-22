"""
YmlConfLoader Unit Tests class
"""
import os
import inspect
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.conf_manager.yaml_loader import YmlConfLoader
from vemonitor_m8.core.exceptions import YAMLFileEmpty, YAMLFileNotFound, YAMLFileError


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
        # test main file not found
        with pytest.raises(YAMLFileNotFound):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "not_found.yaml"
                )
            )

        # test import file not found
        with pytest.raises(YAMLFileNotFound):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "import_not_found.yaml"
                )
            )

        # test import file exist but empty
        with pytest.raises(YAMLFileNotFound):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "import_empty.yaml"
                )
            )

    def test_file_error(self):
        """Test get_config method YAMLFileError Error."""
        # test import yaml file with list of data
        # when the main file config has dict of data
        with pytest.raises(YAMLFileError):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "dummy_conf_dict_error.yaml"
                )
            )

        # test import file with bad extension
        with pytest.raises(YAMLFileError):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "import_bad_ext.yaml"
                )
            )

        # Test get existing config file with bad extension
        with pytest.raises(YAMLFileError):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "bad_ext.ymld"
                )
            )

        # Test get existing but empty config file
        with pytest.raises(YAMLFileEmpty):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "empty.yaml"
                )
            )

    def test_get_dict_main_config(self):
        """Test get_config method with dict content ."""
        # test importing main dict configuration
        # with some child configuration
        conf = YmlConfLoader.get_config(
            os.path.join(
                TestYmlConfLoader.get_dummy_conf_path(),
                "dummy_conf_dict.yaml"
                )
        )
        assert Ut.is_dict(conf) and len(conf) == 7
        assert len(conf.get('Imports')) == 2
        assert len(conf.get('Dummy_1')) == 2
        assert len(conf.get('Dummy_2')) == 2
        assert len(conf.get('Dummy_3')) == 2
        assert len(conf.get('Dummy_4')) == 2
        assert len(conf.get('Dummy_5')) == 2
        assert len(conf.get('Dummy_6')) == 2

        # test importing main dict configuration
        # with only content of dummy_conf_dict1.yaml.
        # do not import content of dummy_conf_dict2.yaml
        conf = YmlConfLoader.get_config(
            os.path.join(
                TestYmlConfLoader.get_dummy_conf_path(),
                "dummy_conf_dict.yaml"
            ),
            ['dummy_conf_dict1.yaml']
        )
        assert Ut.is_dict(conf) and len(conf) == 5
        assert len(conf.get('Imports')) == 2
        assert len(conf.get('Dummy_1')) == 2
        assert len(conf.get('Dummy_2')) == 2
        assert len(conf.get('Dummy_3')) == 2
        assert len(conf.get('Dummy_4')) == 2
        assert conf.get('Dummy_5') is None
        assert conf.get('Dummy_6') is None

    # Test dict conf with bad import type
        with pytest.raises(YAMLFileError):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "dummy_conf_list_bad_imports.yaml"
                )
            )

    def test_get_list_main_config(self):
        """Test get_config method with list content ."""
        conf = YmlConfLoader.get_config(
            os.path.join(
                TestYmlConfLoader.get_dummy_conf_path(),
                "dummy_conf_list.yaml"
                )
        )
        assert Ut.is_list(conf) and len(conf) == 7
        assert len(conf[0].get('Imports')) == 2
        assert len(conf[1].get('Dummy_1')) == 2
        assert len(conf[2].get('Dummy_2')) == 2
        assert len(conf[3].get('Dummy_3')) == 2
        assert len(conf[4].get('Dummy_4')) == 2
        assert len(conf[5].get('Dummy_5')) == 2
        assert len(conf[6].get('Dummy_6')) == 2

        # test importing main list configuration
        # with only content of dummy_conf_dict1.yaml.
        # do not import content of dummy_conf_dict2.yaml
        conf = YmlConfLoader.get_config(
            os.path.join(
                TestYmlConfLoader.get_dummy_conf_path(),
                "dummy_conf_list.yaml"
            ),
            ['dummy_conf_list1.yaml']
        )
        assert Ut.is_list(conf) and len(conf) == 5
        assert len(conf[0].get('Imports')) == 2
        assert len(conf[1].get('Dummy_1')) == 2
        assert len(conf[2].get('Dummy_2')) == 2
        assert len(conf[3].get('Dummy_3')) == 2
        assert len(conf[4].get('Dummy_4')) == 2

        # Test list conf with bad import type
        with pytest.raises(YAMLFileError):
            YmlConfLoader.get_config(
                os.path.join(
                    TestYmlConfLoader.get_dummy_conf_path(),
                    "dummy_conf_list_bad_imports.yaml"
                )
            )
