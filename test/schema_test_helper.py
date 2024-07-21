#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Helper class to test json schemas validation."""
from typing import Optional, Union
import pytest
from ve_utils.utype import UType as Ut
from jsonschema.exceptions import ValidationError
from vemonitor_m8.conf_manager.schema_validate import SchemaValidate


class SchemaTestHelper:
    """Helper class to test json schemas validation."""

    def __init__(self):
        self.schema = None
        self.obj = None

    def get_values_helper(self, key: str, choice: str) -> Optional[list]:
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
            elif key == "positive_number":
                result = self.get_positive_number_values_helper(choice)
            elif key == "positive_integer":
                result = self.get_positive_integer_values_helper(choice)
        return result

    def get_string_text_values_helper(self, choice: str) -> list:
        """
        Return a list of string_text values to test json schema validation.

        The function returns different lists depending on the choice parameter,
        which is either good or bad.
        If choice is set to good,
        then strings that are expected to be valid will be returned.
        If choice is set to bad,
        then strings that are expected not to be valid will be returned.

        :param self: Allow a function to refer to itself
        :param choice: Determine which list of values to return
        :return: A list of values that are bad or good string_text
        """
        #
        if choice == "good":
            return[
                "hello", "HeLlO", "H1eL2lO", "0H1eL2lO", "0H1e_L2lO",
                "H1_eL 2-l/O", "0H1e-L2lO", "0H1e_L2lO", "0H1e L2lO"
            ]
        else:
            return[
                1, 0, None, "_hello", "hello_", "a&",
                "c^", "m%", "Ad8M.s+dsd", "Ad8M$ sdsd",
                "[a-z]", "%shello", "hello%sworld"
            ]

    def get_string_key_values_helper(self, choice: str) -> list:
        """
        Return a list of string_key values to test json schema validation.

        The function returns different lists depending on the choice parameter,
        which is either good or bad.
        If choice is set to good,
        then strings that are expected to be valid will be returned.
        If choice is set to bad,
        then strings that are expected not to be valid will be returned.

        :param self: Allow a function to refer to itself
        :param choice: Determine which list of values to return
        :return: A list of values that are bad or good string_key
        """
        if choice == "good":
            return[
                "hello", "HeLlO", "H1eL2lO", "0H1eL2lO", "0H1e_L2lO"
            ]
        else:
            return[
                1, 0, None, "_hello", "hello_", "hello#", "a&",
                "c$", "m%", "Ad8M.sdsd", "Ad8M sdsd", "[a-z]",
                "%shello"
            ]

    def get_string_columns_values_helper(self, choice: str) -> list:
        """
        Return a list of string_columns values to test json schema validation.

        The function returns different lists depending on the choice parameter,
        which is either good or bad.
        If choice is set to good,
        then strings that are expected to be valid will be returned.
        If choice is set to bad,
        then strings that are expected not to be valid will be returned.

        :param self: Allow a function to refer to itself
        :param choice: Determine which list of values to return
        :return: A list of values that are bad or good string_columns
        """
        if choice == "good":
            return[
                "hello", "HeLlO", "H1eL2lO", "0H1eL2lO", "0H1e_L2lO",
                "#H1eL2lO", "0H1e#L2lO", "0H1e_L2lO#",
            ]
        else:
            return[
                1, 0, None, "_hello", "hello_", "a&",
                "c^", "m%", "Ad8M.sdsd", "Ad8M sdsd",
                "[a-z]", "%shello", "hello%sworld"
            ]

    def get_positive_number_values_helper(self, choice: str) -> list:
        """
        Return a list of positive_number values to test jsonschema validation.

        The function returns different lists depending on the choice parameter,
        which is either good or bad.
        If choice is set to good,
        then strings that are expected to be valid will be returned.
        If choice is set to bad,
        then strings that are expected not to be valid will be returned.

        :param self: Allow a function to refer to itself
        :param choice: Determine which list of values to return
        :return: A list of values that are bad or good positive_number
        """
        if choice == "good":
            return[1, 3, 10, 1.2]
        else:
            return[
                0, -1, -0.1, "_hel lo",
                False, None, dict(), tuple()
            ]

    def get_positive_integer_values_helper(self, choice: str) -> list:
        """
        Return a list of positive_integer values to test jsonschema validation.

        The function returns different lists depending on the choice parameter,
        which is either good or bad.
        If choice is set to good,
        then strings that are expected to be valid will be returned.
        If choice is set to bad,
        then strings that are expected not to be valid will be returned.

        :param self: Allow a function to refer to itself
        :param choice: Determine which list of values to return
        :return: A list of values that are bad or good positive_integer
        """
        result = None
        if choice == "good":
            result = [1, 3, 10]
        else:
            result = [
                0, -1, -0.1, 0.1, 2.2, "_hel lo",
                False, None, dict(), tuple()
            ]
        return result

    def _run_test_bad_value_data(self,
                                 key: Union[str, int],
                                 data: any,
                                 new_val: any
                                 ) -> None:
        val = data[key]
        data[key] = new_val
        with pytest.raises(ValidationError):
            SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        data[key] = val
        return data[key] == val

    def _run_test_good_value_data(self,
                                  key: Union[str, int],
                                  data: any,
                                  new_val: any
                                  ) -> None:
        val = data[key]
        data[key] = new_val
        SchemaValidate.validate_data_from_schema(self.obj, self.schema)
        data[key] = val
        return data[key] == val

    def _run_assert_values_data(self,
                               key: Union[str, int],
                               item: Union[dict, list],
                               list_values: list,
                               choice: str,
                               restrict: str
                               ):
        if Ut.is_str(key) or Ut.is_int(key) \
                and (Ut.is_dict(item, not_null=True) or Ut.is_list(item, not_null=True))\
                and Ut.is_list(list_values, not_null=True):

            for val_tst in list_values:
                if choice == "good" and restrict != "bad":
                    assert self._run_test_good_value_data(key, item, val_tst)
                elif choice == "bad" and restrict != "good":
                    assert self._run_test_bad_value_data(key, item, val_tst)
                else:
                    if not ((choice == "good" and restrict == "bad") \
                            or (choice == "bad" and restrict == "good")):
                        raise ValueError(
                            f"Fatal error: Unable to evaluate {choice} value "
                            f"on key {key}. With restriction value {restrict}"
                        )
        else:
            raise ValueError(
                "Fatal error: Unable to evaluate good values "
                f"on key {key}"
            )

    def run_test_values_data(self,
                             datas: list,
                             list_values: list,
                             choice: str
                             ):
        """Apply and test values."""
        if Ut.is_list(datas, not_null=True) and Ut.is_list(list_values, not_null=True):
            for data_item in datas:
                key, item, restrict = None, None, None
                if Ut.is_tuple(data_item):
                    if len(data_item) == 2:
                        key, item = data_item
                    elif len(data_item) == 3:
                        key, item, restrict = data_item
                    else:
                        raise ValueError(
                        "Fatal error: Unable to evaluate good values "
                        f"on key {key}, items tuple must have a length of 2 or 3. "
                        "( key: str or int, data: list or dict )"
                    )
                    self._run_assert_values_data(key, item, list_values, choice, restrict)
                else:
                    raise ValueError(
                        "Fatal error: Unable to evaluate good values "
                        f"on key {key}, items must be a tuple. "
                        "( key: str or int, data: list or dict )"
                    )
        else:
            raise ValueError(
                "Fatal error: Unable to evaluate good values "
                f"on list values {list_values}"
            )

    def run_test_values(self, datas: list, key: str):
        """Apply and test all values."""
        self.run_test_values_data(
            datas = datas,
            list_values = self.get_values_helper(key, 'good'),
            choice='good'
        )

        self.run_test_values_data(
            datas = datas,
            list_values = self.get_values_helper(key, 'bad'),
            choice='bad'
        )
