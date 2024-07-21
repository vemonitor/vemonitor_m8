"""Test AppBlock jsonschema."""
import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import SchemaError
from vemonitor_m8.conf_manager.schema_validate import SchemaValidate
from vemonitor_m8.conf_manager.loader import Loader
from .schema_test_helper import SchemaTestHelper


@pytest.fixture(name="schema_manager", scope="class")
def schema_manager_fixture():
    """Json Schema test manager fixture"""
    class SchemaManager(SchemaTestHelper):
        """Json Schema test manager fixture Class"""
        def __init__(self):
            SchemaTestHelper.__init__(self)
            self.init_data()

        def init_data(self):
            """Init data"""
            self.schema = SchemaValidate.load_schema("emoncms")
            loader = Loader("test/conf/emoncmsTest.yaml")
            self.obj = loader.get_yaml_config()
            self.obj = self.obj.get("Structure")

        @staticmethod
        def get_string_description_values_helper(choice: str) -> list:
            """
            Return a list of string_auth values to test jsonschema validation.

            The function returns different lists depending on the choice parameter,
            which is either good or bad.
            If choice is set to good,
            then strings that are expected to be valid will be returned.
            If choice is set to bad,
            then strings that are expected not to be valid will be returned
            :param choice: Determine which list of values to return
            :return: A list of values that are bad or good string_auth.
            """
            if choice == "good":
                return ["h_ello", "H,eLlO", "H1.eL2lO", "0H1eL2lO.dev", "0H1e_L2lO@.-"]

            return [0, -1, -0.1, 0.1, 2.2, "_hel?lo", "_hel$lo", "_hel#lo", "_hel&lo",
                    False, None, dict(), tuple()
                    ]


        def get_values_helper(self, key: str, choice: str) -> list:
            """
            Return a list of values to test json schema validation.

            Accepts two parameters, key and choice.
            - 'key' is a string that specifies the type of value to be returned.
            - 'choice' is also a string that specifies whether
                to return good or bad values for the specified key.

            :param self: Access variables that belongs to the class
            :param key: Determine which type of values to return
            :param choice: Determine which values to return
            :return: A list of values for the given key and choice
            :doc-author: Trelent
            """
            result = None
            if Ut.is_str(key) and choice in ['good', 'bad']:
                if key == "string_key":
                    result = self.get_string_key_values_helper(choice)
                elif key == "string_column":
                    result = self.get_string_columns_values_helper(choice)
                elif key == "string_text":
                    result = self.get_string_text_values_helper(choice)
                elif key == "string_description":
                    result = SchemaManager.get_string_description_values_helper(choice)
                elif key == "positive_number":
                    result = self.get_positive_number_values_helper(choice)
                elif key == "positive_integer":
                    result = self.get_positive_integer_values_helper(choice)
            return result

        def run_test_values(self, datas: list, key: str):
            """Run test values helper"""
            self.run_test_values_data(
                datas=datas,
                list_values=self.get_values_helper(key, 'good'),
                choice='good'
            )

            self.run_test_values_data(
                datas=datas,
                list_values=self.get_values_helper(key, 'bad'),
                choice='bad'
            )

    return SchemaManager()


class TestEmoncmsSchemas:
    """Test AppBlock jsonschema."""
    @staticmethod
    def test_bad_file_key():
        """Test load_schema method."""
        with pytest.raises(SchemaError):
            SchemaValidate.load_schema("hallo")

    def test_data_validation(self, schema_manager):
        """Test validate_data method."""
        assert Ut.is_dict(schema_manager.obj, not_null=True)
        assert Ut.is_dict(
            SchemaValidate.validate_data(schema_manager.obj, "emoncms"),
            not_null=True
        )

    def test_string_description_pattern(self, schema_manager):
        """Test string_description values to validate patterns."""
        datas = [
                ('description', schema_manager.obj['unittest_api']['V']),
            ]
        schema_manager.run_test_values(datas=datas, key="string_description")

    def test_positive_integer_pattern(self, schema_manager):
        """Test positive_integer values to validate patterns."""
        datas = [
                ('process', schema_manager.obj['unittest_api']['V']['feeds']['V']),
                ('engine', schema_manager.obj['unittest_api']['V']['feeds']['V']),
                ('time_interval', schema_manager.obj['unittest_api']['V']['feeds']['V'])
            ]
        schema_manager.run_test_values(datas=datas, key="positive_integer")
