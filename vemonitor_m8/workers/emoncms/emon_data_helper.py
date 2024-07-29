#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Emoncms data Helper"""
import logging
from typing import Optional, Union
from ve_utils.utype import UType as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.1.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class EmoncmsHelper:
    """Emoncms data Helper"""

    @staticmethod
    def is_request_success(result) -> bool:
        """
        Test if emoncms request result is success.

        :Example :
            >>> EmoncmsHelper.is_request_success(result={"success": "true"})
            >>> True
        :param result: dict: The request json response.
        :return: bool: True if the request return success.
        """
        return Ut.is_dict(result) and Ut.str_to_bool(result.get('success'))

    @staticmethod
    def get_data_key_from_input_item(input_data: Union[list, dict],
                                     key: str
                                     ) -> any:
        """
        Get data key inputs list from emoncms Api.


        Response if success return for all inputs :
                                    'input id',
                                    'node id' ,
                                    'input name' ,
                                    'input description' ,
                                    'input process list',
                                    'last time input',
                                    'last value input'
        """
        result = None
        if Ut.is_list(input_data, eq=1):
            input_data = input_data[0]

        if Ut.is_dict(input_data, not_null=True) \
                and key in input_data:
            result = input_data.get(key)
        return result

    @staticmethod
    def get_sorted_keys(sort_data: dict) -> list:
        """
        Get sorted feed list data from emoncms Api.
        """
        result = list()
        keys = ['feed_id', 'name', 'tag', 'public', 'engine', 'interval']
        for key_item in keys:
            if key_item in sort_data:
                if key_item == 'name' \
                        and 'tag' in sort_data:
                    result.append(key_item)
                elif key_item != 'name':
                    result.append(key_item)
        return result

    @staticmethod
    def get_formatted_feed_name(node: str, name: str) -> Optional[str]:
        """
        Get the formatted feed name with emoncms format.

         -> node:NodeName:FeedName
        :param node: str: The emoncms node name
        :param name: str: The emoncms feed name
        :return: Optional[str]: Emoncms formatted feed name as :<br>
            'node:NODE:FEED'
            or None if parameters are not strings
        """
        if Ut.is_str(node) and Ut.is_str(name):
            return f'node:{node}:{name}'
        return None

    @staticmethod
    def is_process_feed(process: Union[str, list], feed_id: int) -> bool:
        """
        Test if feed_id is in input process list.

        :Example :
            >>> EmoncmsHelper.is_process_feed(process="1:12,1:13", feed_id=13)
            >>> True
        :param process: int: The input process list.
        :param feed_id: int: The feed id.
        :return: bool: True if feed_id is in input process list
        """
        result = False
        feed_id = Ut.get_int(feed_id, 0)
        if Ut.is_str(process, not_null=True):
            process = EmoncmsHelper.get_process_to_list(
                process=process
            )

        if Ut.is_int(feed_id, positive=True)\
                and Ut.is_list(process, not_null=True):
            for item in process:
                if Ut.is_tuple(item, eq=2) and item[1] == feed_id:
                    result = True
                    break
        return result

    @staticmethod
    def remove_feed_from_process(process: Union[str, list],
                                 feed_id: int
                                 ) -> str:
        """
        Remove process feed from input process list.

        :Example :
            >>> EmoncmsHelper.remove_feed_from_process(
                process="1:12,1:13",
                feed_id=13
            )
            >>> "1:12"
        :param process: str or list: The input process list.
        :param feed_id: int: The feed id.
        :return: bool: The input process list without process with feed_id
        """
        result = ""
        feed_id = Ut.get_int(feed_id, 0)
        if Ut.is_str(process, not_null=True):
            process = EmoncmsHelper.get_process_to_list(
                process=process
            )

        if Ut.is_int(feed_id, positive=True) \
                and Ut.is_list(process, not_null=True):
            tmp = list()
            for item in process:
                if Ut.is_tuple(item, eq=2)\
                        and not item[1] == feed_id:
                    tmp.append(item)
            if Ut.is_list(tmp, not_null=True):
                result = EmoncmsHelper.get_list_to_comma_separated_values(tmp)
        else:
            result = EmoncmsHelper.get_list_to_comma_separated_values(process)
        return result

    @staticmethod
    def remove_feed_from_processes(inputs: list,
                                   feed_id: int
                                   ) -> Optional[list]:
        """
        Remove feed from inputs processes.

        :Example :
            >>> EmoncmsHelper.remove_feed_from_processes(
                inputs={...},
                feed_id=13
            )
            >>> [{'input_id': 18, "process_list": ""}]
        :param inputs: list: The inputs list.
        :param feed_id: int: The feed id.
        :return: Optional[list]:
            The inputs list to update processes with new ones
        """
        result = None
        if Ut.is_list(inputs, not_null=True)\
                and Ut.is_int(feed_id, positive=True):
            result = list()
            for input_item in inputs:
                # if input has a process list
                if Ut.is_dict(input_item, not_null=True) \
                        and Ut.is_str(
                        input_item.get('processList'),
                        not_null=True):
                    # get process formatted to list of tuples
                    process_list = EmoncmsHelper.get_process_to_list(
                        input_item.get('processList')
                    )
                    # get process list with feed_id removed
                    process = EmoncmsHelper.remove_feed_from_process(
                        process=process_list,
                        feed_id=feed_id
                    )
                    nb_process = len(process_list)
                    #
                    if (nb_process > 1
                        and Ut.is_str(process, not_null=True)) \
                            or (nb_process == 1
                                and Ut.is_str(process)) \
                            and process != input_item.get('processList'):
                        result.append({
                            "input_id": Ut.get_int(input_item.get('id')),
                            "process_list": process
                        })
            if not Ut.is_list(result, not_null=True):
                result = None
        return result

    @staticmethod
    def format_process_list(process: int, feed_id: int) -> str:
        """
        Format process list data.

        :Example :
            >>> EmoncmsHelper.format_process_list(process=1, feed_id=18)
            >>> "1:18"
        :param process: int: The feed process.
        :param feed_id: int: The feed id.
        :return: str: Formated process list as string "process:feed_id".
        """
        if Ut.is_int(process) and Ut.is_int(feed_id):
            return f"{process}:{feed_id}"
        return ""

    @staticmethod
    def get_comma_separated_values_to_list(process: str) -> Optional[list]:
        """
        Format string input process list to list.

        :Example :
            >>> EmoncmsHelper.get_comma_separated_values_to_list(
                process="1:18,
                1:19, 1:20"
            )
            >>> ["1:18", "1:19", "1:20"]
        :param process: str: The input process list.
        :return: list: Formated process list as list of strings.
        """
        result = None
        if Ut.is_str(process, not_null=True):
            process = process.replace(" ", "")
            result = process.split(',')
            if not Ut.is_list(result, not_null=True):
                result = None
        return result

    @staticmethod
    def split_process(process: str) -> tuple:
        """Split string process list in tuple of integers."""
        result = None
        if Ut.is_str(process, not_null=True):
            tmp = process.split(':')
            if Ut.is_list(tmp, eq=2):
                proc, feed_id = Ut.get_int(tmp[0], 0), Ut.get_int(tmp[1], 0)
                if Ut.is_int(proc, positive=True)\
                        and Ut.is_int(feed_id, positive=True):
                    result = (proc, feed_id)
        return result

    @staticmethod
    def get_process_to_list(process: str) -> list:
        """
        Format string input process list to list of tuples.

        :Example :
            >>> EmoncmsHelper.get_process_to_list(process="1:18, 1:19, 1:20")
            >>> [(1, 18), (1, 19), (1, 20)]
        :param process: str: The input process list.
        :return: list: Formated process list as list of tuples.
        """
        result = None
        if Ut.is_str(process, not_null=True):
            process_list = EmoncmsHelper.get_comma_separated_values_to_list(
                process
            )
            if Ut.is_list(process_list, not_null=True):
                result = list()
                for item in process_list:
                    values = EmoncmsHelper.split_process(item)
                    if Ut.is_tuple(values, eq=2):
                        result.append(values)
        return result

    @staticmethod
    def get_list_to_comma_separated_values(process: list) -> str:
        """
        Format process list from list to string.

        :Example :
            >>> EmoncmsHelper.get_list_to_comma_separated_values(
                process=["1:18", "1:19", "1:20"]
            )
            >>> "1:18,1:19,1:20"
            >>> EmoncmsHelper.get_list_to_comma_separated_values(
                process=[(1, 18), (1,19), (1, 20)]
            )
            >>> "1:18,1:19,1:20"
        :param process: list: The input process list.
        :return: Optional[str]: Formated process list as string.
        """
        result = ""
        if Ut.is_list(process, not_null=True):
            result = ''
            for key, item in enumerate(process):
                if Ut.is_str(item, not_null=True):
                    if key == 0:
                        result = f'{item}'
                    else:
                        result = f'{result},{item}'
                elif Ut.is_tuple(item, eq=2):
                    tmp = EmoncmsHelper.format_process_list(
                        process=item[0],
                        feed_id=item[1]
                    )
                    if key == 0:
                        result = f'{tmp}'
                    else:
                        result = f'{result},{tmp}'
        return result

    @staticmethod
    def prepare_feed_data(data: dict,
                          is_create: bool = True
                          ) -> Optional[dict]:
        """
        Prepare feed data to create or update feed.

        Data dictonary parameter can contain :
            - tag : str: The feed node
            - name : str: The feed name
            - unit : str: The feed unit
            - public : int: Public status of the feed
            - datatype : int: The feed datatype (Only for new feeds)
            - engine : int: The feed engine (Only for new feeds)
            - interval : int: The feed interval in sec (Only for new feeds)
        :Example :
            >>> EmoncmsHelper.prepare_feed_data(
            >>>     data={"tag": "Node", "name": "MyName", "engine": 1}
            >>> )
            >>> {"tag": "Node", "name": "MyName", "engine": 1}
        :param data: dict: The feed data dictionary
        :param is_create: bool: Is feed creation
        :return: int or None: The feed id, created or None if error occurs.
        """
        result = None
        if Ut.is_dict(data, not_null=True):
            result = dict()
            if Ut.is_str(data.get('tag'), not_null=True):
                result['tag'] = data.get('tag')
            if Ut.is_str(data.get('name'), not_null=True):
                result['name'] = data.get('name')
            if Ut.is_str(data.get('unit'), not_null=True):
                result['unit'] = data.get('unit')
            if Ut.is_int(data.get('public')):
                result['public'] = data.get('public')
            if Ut.is_int(data.get('datatype')) and is_create:
                result['datatype'] = data.get('datatype')
            if Ut.is_int(data.get('engine')) and is_create:
                result['engine'] = data.get('engine')
            if Ut.is_int(data.get('interval'), not_null=True) and is_create:
                result['options'] = '{"interval":%s}' % data.get('interval')
        return result
