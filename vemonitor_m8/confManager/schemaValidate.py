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
    > SchemaValidate.validate_data(data=appBlocks_data, shem_key_path="appBlocks")
    > ...appBlocks_data...

 .. seealso:: ConfigLoader
 .. raises:: ValidationError, SchemaError, ErrorTree
"""
import os
import inspect
import logging
from jsonschema import validate
from jsonschema.exceptions import SchemaError

from ve_utils.usys import USys as USys
from ve_utils.ujson import UJson as UJson
from ve_utils.utype import UType as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2022, Eli Serra"
__deprecated__ = False
__license__ = "GPLv3"
__status__ = "Dev" #Production
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

            > SchemaValidate.validate_data(data=appBlocks_data, shem_key_path="appBlocks")

        .. seealso::  ConfigLoader
        .. raises:: ValidationError, SchemaError, ErrorTree
        .. warnings:: Class Method and Public
        """
        schema = SchemaValidate._load_schema(shem_key_path)
        if Ut.is_dict(schema, not_null=True):
            return SchemaValidate.validate_data_from_schema(data, schema)
        raise SchemaError(
            "Fatal error unable to load valid jsonschema for key %s" %
            (shem_key_path)
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

            > SchemaValidate.validate_data_from_schema(data=appBlocks_data, schema={....})

        .. seealso::  ConfigLoader
        .. raises:: ValidationError, SchemaError, ErrorTree
        .. warnings:: Class Method and Public
        """
        if Ut.is_dict(schema, not_null=True):
            validate(instance=data, schema=schema)
            return data
        raise SchemaError(
            "Fatal error: invalid jsonschema : %s" %
            (schema)
            )

    @classmethod
    def _load_schema(cls,
                      file_key: str
                      ):
        """
        Load json schema from file_key, and return parsed content.

        First get the file name, adding "_schema.json" 
        at the end of file_key value.
        Then use the current script path to locate the schema directory path.
        And finaly, if path is a file on disck,
        read and parse the file content.
            > ...vemonitor/confManager/schemas/[file_key]_schema.json
        
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
        if Ut.is_str(file_key) and not os.path.isabs(file_key):
            current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            file_path = "%s_schema.json" % (file_key)
            path = os.path.join(current_script_path, 'schemas', file_path)
            if os.path.isfile(path):
                file_size = os.path.getsize(path)
                if file_size <= cls.MAX_FILE_SIZE:
                    data = None
                    # load the yaml file
                    with open(path, "r") as f:
                        data = UJson.load_json(f)
                    
                    return data
                else:
                    raise SchemaError(
                        "Fatal error jsonschema file is too big,"
                        "file size : %s/%s" %
                        (file_size, cls.MAX_FILE_SIZE)
                    )
            else:
                raise SchemaError(
                    "Fatal error, unable to load jsonschema for key %s."
                    "Path : %s" %
                    (file_key, path)
                )
        else:
            raise SchemaError(
                "Fatal error, jsonschema for key %s."
                "is not valid" %
                (file_key)
            )
        

    