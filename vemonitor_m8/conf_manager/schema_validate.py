#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Used to load jsonschema and validate data with it.

Get data to test and jsonschema key,
Load the jsonschema file with the private class method _load_schema,
and validate the instance data.
If any validation error occurs, raise exception.
Or if no error occurs, return data tested object

:Example:
    > SchemaValidate.validate_data(
        data=appBlocks_data,
        shem_key_path="appBlocks"
    )
    > ...appBlocks_data...

 .. seealso:: ConfigLoader
 .. raises:: ValidationError, SchemaError, ErrorTree
"""
import inspect
import logging
from os import path as Opath
from jsonschema import validate
from jsonschema.exceptions import SchemaError

from ve_utils.ujson import UJson
from ve_utils.utype import UType as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class SchemaValidate():
    """Simple Class to load jsonschema file and validate data."""

    MAX_FILE_SIZE = 80000

    @classmethod
    def validate_data(cls, data: any, shem_key_path: str) -> None:
        """
        Validate data with loaded jsonschema.

        It will import json schema file from shem_key_path,
        and if json schema is a dict, use jsonschema.validate.
        If any validation error occurs, raise exception.
        Or if no error occurs, return None

        :param cls:
            Used to Refer to the class itself,
            so that we can call its methods.
        :param data:any:
            Data to test with the json schema loaded file.
        :param shem_key_path:str:
            Key of the json schema file to load.
        :return: None if no error occurs.

        :Example:

            > SchemaValidate.validate_data(
                data=appBlocks_data,
                shem_key_path="appBlocks"
            )

        .. seealso::  ConfigLoader
        .. raises:: ValidationError, SchemaError, ErrorTree
        .. warnings:: Class Method and Public
        """
        schema = SchemaValidate.load_schema(shem_key_path)
        if Ut.is_dict(schema, not_null=True):
            return SchemaValidate.validate_data_from_schema(data, schema)
        raise SchemaError(
            "Fatal error: "
            f"unable to load valid jsonschema for key {shem_key_path}"
        )

    @classmethod
    def validate_data_from_schema(cls, data: any, schema: dict) -> None:
        """
        Validate data with provided jsonschema.

        if json schema is a dict, use jsonschema.validate.
        If any validation error occurs, raise exception.
        Or if no error occurs, return None

        :param cls:
            Used to Refer to the class itself,
            so that we can call its methods.
        :param data:any:
            Data to test with the json schema loaded file.
        :param schema:dict:
            the json schema to validate data.
        :return: None if no error occurs.

        :Example:

            > SchemaValidate.validate_data_from_schema(
                data=appBlocks_data,
                schema={....}
            )

        .. seealso::  ConfigLoader
        .. raises:: ValidationError, SchemaError, ErrorTree
        .. warnings:: Class Method and Public
        """
        if Ut.is_dict(schema, not_null=True):
            validate(instance=data, schema=schema)
            return data
        raise SchemaError(
            f"Fatal error: invalid jsonschema : {schema}"
        )

    @classmethod
    def load_schema(cls,
                    file_key: str
                    ):
        """
        Load json schema from file_key, and return parsed content.

        First get the file name, adding "_schema.json"
        at the end of file_key value.
        Then use the current script path to locate the schema directory path.
        And finaly, if path is a file on disck,
        read and parse the file content.
            > ...vemonitor/conf_manager/schemas/[file_key]_schema.json

        If any error occurs, raise exception.
        Or if no error occurs, return parsed json schema.

        :param cls:
            Used to Refer to the class itself,
            so that we can call its methods.
        :param file_key:str:
            Key of the json schema file to load.
        :return: parsed json schema data or None if any error occurs.

        :Example:

            > SchemaValidate._load_schema(shem_key_path="appBlocks")
            > {my_schema_data}

        .. seealso::  ConfigLoader
        .. raises:: ValidationError, SchemaError, ErrorTree
        .. warnings:: Class Method and Private
        """
        if not Ut.is_str(file_key, not_null=True) or Opath.isabs(file_key):
            raise SchemaError(
                f"Fatal error, jsonschema for key {file_key}."
                "is not valid"
            )

        current_script_path = Opath.dirname(
            Opath.abspath(inspect.getfile(inspect.currentframe()))
        )
        file_path = f"{file_key}_schema.json"
        path = Opath.join(current_script_path, 'schemas', file_path)
        if not Opath.isfile(path):
            raise SchemaError(
                f"Fatal error, unable to load jsonschema for key {file_key}."
                f"Path : {path}"
            )

        file_size = Opath.getsize(path)
        if file_size > cls.MAX_FILE_SIZE:
            raise SchemaError(
                "Fatal error jsonschema file is too big, "
                f"file size : {file_size}/{cls.MAX_FILE_SIZE}"
            )

        data = None
        # load the yaml file
        with open(path, "r", encoding="utf-8") as f:
            data = UJson.load_json(f)

        return data
