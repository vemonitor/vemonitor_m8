#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Emoncms api set Helper"""
import re
import logging
from typing import Optional, Union
from urllib.parse import quote

from ve_utils.utype import UType as Ut
from ve_utils.ujson import UJson
from vemonitor_m8.workers.emoncms.emoncms_api import EmoncmsApi
from vemonitor_m8.workers.emoncms.emon_data_helper import EmoncmsHelper

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.1.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class EmoncmsSetApi(EmoncmsApi):
    """
    Emoncms api set Helper.
    Used to update emoncms Inputs/Feeds structure.
    """

    def __init__(self,
                 name: str = None,
                 active: bool = True,
                 addr: str = None,
                 apikey: str = None):
        """
        :param name: str: name of emoncms server
        :param active: bool: name of emoncms server
        :param addr: str: emoncms server host
        :param apikey: str: emoncms server apikey
        """
        EmoncmsApi.__init__(self,
                            name=name,
                            active=active,
                            addr=addr,
                            apikey=apikey
                            )

    def _execute_simple_request(self,
                                item_type: str,
                                action: str,
                                item_id: Optional[int] = None
                                ) -> Union[str, dict]:
        """
        Execute a request on feed .

        :Example :
            >>> self._execute_simple_request(item_type="feed", action="clear", item_id=14)
            >>> True
        :param action: str: The action id to execute
        :param item_type: str: The item_type to select (input or feed)
        :param item_id: int or str: The input/feed id
        :return: bool: True if action executed on feed with success.
        """
        result = None
        item_id = Ut.get_int(item_id, default=0)
        actions = {
            'input': {
                'clean': {
                    'uri': '/input/clean.json',
                    'params': None,
                    'response_type': "text"
                },
                'delete': {
                    'uri': '/input/delete.json',
                    'params': {"inputid": item_id},
                    'response_type': "text"
                },
            },
            'feed': {
                'clear': {
                    'uri': '/feed/clear.json',
                    'params': {"id": item_id},
                    'response_type': "json"
                },
                'delete': {
                    'uri': '/feed/delete.json',
                    'params': {"id": item_id},
                    'response_type': "json"
                },
            }
        }
        data_req = EmoncmsSetApi._get_request_params(
            actions=actions,
            item_type=item_type,
            action=action
        )

        if Ut.is_tuple(data_req, eq=3):
            uri, params, response_type = data_req
            result = self._execute_request(
                uri,
                req_type='get',
                params=params,
                response_type=response_type
            )
        else:
            logger.debug(
                "[EmoncmsSetApi] Unable to execute request, Bad params, "
                "required action : %s"
                "required item_type : %s"
                "item_id : %s.",
                action,
                item_type,
                item_id
            )
        return result

    def _execute_simple_json_request(self,
                                     item_type: str,
                                     action: str,
                                     item_id: Optional[int] = None
                                     ) -> bool:
        """
        Execute a request on emoncms with json responce .

        :Example :
            >>> self._execute_simple_json_request(item_type="feed", action="clear", item_id=14)
            >>> True
        :param action: str: The action id to execute
        :param item_type: str: The item_type to select (input or feed)
        :param item_id: int or str: The input/feed id
        :return: bool: True if action executed with success.
        """
        result = False
        response = self._execute_simple_request(item_type=item_type,
                                                action=action,
                                                item_id=item_id)
        if EmoncmsHelper.is_request_success(response):
            result = True
        else:
            logger.debug(
                "[EmoncmsSetApi] Unable to Execute request on emoncms. "
                "item_type: %s - action: %s, item_id: %s"
                "Response : %s",
                item_type, action, item_id,
                response)
        return result

    def set_input_fields(self,
                         input_id: Union[str, int],
                         name: Optional[str] = None,
                         description: Optional[str] = None
                         ) -> bool:
        """
        Set input fields on emoncms server.

        :Example :
            >>> self.set_input_fields(input_id=14, name="NewName")
            >>> True
            >>> self.set_input_fields(input_id=14, description="New Input Description")
            >>> True
        :param input_id: int or str: The input id to update
        :param name: Optional[str]: The new input name to update
        :param description: Optional[str]: The new input description to update
        :return: bool: True if input updated with success.
        """
        result, params = False, dict()
        input_id = Ut.get_int(input_id, default=0)
        if Ut.is_int(input_id, positive=True):
            params['inputid'] = input_id

        if Ut.is_str(name, not_null=True):
            Ut.init_dict_key(params, 'fields', dict())
            params['fields']['name'] = name
        if Ut.is_str(description, not_null=True):
            Ut.init_dict_key(params, 'fields', dict())
            params['fields']['description'] = description

        if Ut.is_dict(params)\
                and 'inputid' in params\
                and Ut.is_dict(params.get('fields'), not_null=True):
            params['fields'] = quote(
                UJson.dumps_json(params.get('fields'), raise_errors=False)
            )
            response = self._execute_request(
                '/input/set.json',
                req_type='get',
                params=params,
                response_type="json"
            )
            # Response if success return : 'Field updated'
            if Ut.is_dict(response, not_null=True)\
                    and response.get('success') is True\
                    and response.get('message') == "Field updated":
                result = True
            else:
                logger.debug(
                    "[EmoncmsSetApi] Set input fields for id %s from emoncms api fail "
                    "Response : %s",
                    input_id,
                    response)
        else:
            logger.debug(
                "[EmoncmsSetApi] Unable to Set input fields, "
                "required input_id and name or description."
                "input_id : %s -- name : %s -- description : %s",
                input_id,
                name,
                description
            )
        return result

    def set_input_process_list(self, input_id: int, process_list: Union[str, list]) -> bool:
        """
        Set input process list on emoncms for input_id.

        :Example :
            >>> self.set_input_process_list(input_id=14, process_list=["1:14"])
            >>> True
        :param input_id: int or str: The input id to update
        :param process_list: list: The input process list to add
        :return: bool: True if input updated with success.
        """
        result, params, data = False, None, None
        input_id = Ut.get_int(input_id, default=0)
        if Ut.is_int(input_id, positive=True):
            params = {'inputid': input_id}
        if Ut.is_list(process_list):
            data = {
                'processlist': EmoncmsHelper.get_list_to_comma_separated_values(process_list)
            }
        elif Ut.is_str(process_list):
            data = {
                'processlist': process_list
            }

        if Ut.is_dict(params, not_null=True) \
                and Ut.is_dict(data, not_null=True):
            response = self._execute_request(
                '/input/process/set.json',
                params=params,
                data=data,
                req_type="post",
                response_type="json"
            )
            if EmoncmsHelper.is_request_success(response):
                # Response contain process lists
                result = True
            else:
                logger.debug(
                    "[EmoncmsSetApi] Set input process list from emoncms api fail "
                    "Response : %s",
                    response
                )
        else:
            logger.debug(
                "[EmoncmsSetApi] Set input process list from emoncms api fail "
                "Required input id : %s and process_list : %s",
                input_id,
                process_list
            )
        return result

    def delete_input(self, input_id: int) -> bool:
        """
        Delete an input on emoncms server.

        :Example :
            >>> self.delete_input(input_id=14)
            >>> True
        :param input_id: int or str: The input id to delete
        :return: bool: True if input deleted with success.
        """
        result = False
        response = self._execute_simple_request(item_type="input",
                                                action="delete",
                                                item_id=input_id)
        if response == '"input deleted"':
            result = True
        else:
            logger.debug(
                "[EmoncmsSetApi] Unable to Delete input for id %s on emoncms. "
                "Response : %s",
                input_id,
                response)
        return result

    def delete_inputs_by_node(self, node: str) -> bool:
        """
        Delete all inputs by node name on emoncms server.

        :Example :
            >>> self.delete_inputs_by_node(node="MyNode")
            >>> True
        :param node: str: The node inputs to delete
        :return: bool: True if all node inputs deleted with success.
        """
        result = False
        inputs = self.get_inputs_conf(node)
        if Ut.is_dict(inputs, not_null=True):
            errs, result = 0, True
            for item in inputs.values():
                if Ut.is_dict(item, not_null=True):
                    input_id = Ut.get_int(item.get('id'), 0)
                    if not Ut.is_int(input_id, positive=True)\
                            or not self.delete_input(input_id):
                        errs = errs + 1
                        result = False
            if errs > 0:
                logger.debug(
                    "[EmoncmsSetApi] Unable to delete '%s' inputs for node '%s'...",
                    errs,
                    node
                )
        else:
            logger.debug(
                "[EmoncmsSetApi] Unable to delete node '%s' inputs, bad inputs list returned : %s",
                node,
                inputs
            )
        return result

    def clean_inputs(self) -> int:
        """
        Clean inputs without process list registered.

        :Example :
            >>> self.delete_inputs_by_node()
            >>> 0
        :return: int: The number of inputs without process list deleted from server.
        """
        result = -1
        response = self._execute_simple_request(item_type="input",
                                                action="clean")
        # Response if success return : 'Deleted x inputs'
        if Ut.is_str(response, not_null=True) and response[:7] == "Deleted":
            nb_deleted = re.findall(r'^Deleted (\d+) inputs$', response)
            if Ut.is_list(nb_deleted, eq=1):
                result = Ut.get_int(nb_deleted[0], 0)
        else:
            logger.debug(
                "[EmoncmsSetApi] Clean inputs without process list from emoncms api fail "
                "Response : %s",
                response)
        return result

    def create_feed(self, data: dict) -> Optional[int]:
        """
        Create new feed on emoncms server.

        Data dictonary parameter can contain :
            - tag : str: The feed node (required)
            - name : str: The feed name (required)
            - unit : str: The feed unit
            - public : int: Public status of the feed
            - datatype : int: The feed datatype
            - engine : int: The feed engine (required)
            - interval : int: The feed interval in sec
        :Example :
            >>> self.create_feed(data={"tag": "Node", "name": "MyName", "engine": 1})
            >>> True
        :param data: dict: The feed data dictionary.
        :return: Optional[int]: The feed id, created or None if error occurs.
            ToDo:
                - what is datatype on emoncms?
                - string values must be tested or sanitized.
        """
        result, params = None, EmoncmsHelper.prepare_feed_data(data)

        if Ut.is_dict(params, not_null=True) \
                and 'tag' in params \
                and 'name' in params \
                and 'engine' in params:
            response = self._execute_request(
                '/feed/create.json',
                params=params,
                response_type="json"
            )
            if EmoncmsHelper.is_request_success(response):
                result = Ut.get_int(response.get('feedid'))
            else:
                logger.debug(
                    "[EmoncmsSetApi] Create new feed from emoncms api fail "
                    "Response : %s",
                    response
                )
        else:
            logger.debug(
                "[EmoncmsSetApi] Create new feed from emoncms api fail "
                "Required tag, name and engine : %s",
                params,
            )
        return result

    def clear_process_feeds(self,
                            feed_id: int
                            ) -> bool:
        """
        Clear feed from inputs processes lists on emoncms server.

        :Example :
            >>> self.clear_process_feeds(feed_id=14)
            >>> True
        :param feed_id: int or str: The feed id to clear process list from inputs
        :return: bool: True if feed cleared with success.
        """
        result = False
        feed_id = Ut.get_int(feed_id, 0)
        if Ut.is_int(feed_id, positive=True):
            # get inputs list
            inputs = self.get_inputs_list()
            to_update = EmoncmsHelper.remove_feed_from_processes(
                inputs=inputs,
                feed_id=feed_id
            )
            result = True
            if Ut.is_list(to_update, not_null=True):

                for item in to_update:
                    if Ut.is_dict(item, not_null=True):
                        input_id = item.get('input_id')
                        process = item.get('process_list')
                        if not self.set_input_process_list(
                                    input_id=input_id,
                                    process_list=process
                                    ):
                            result = False
        return result

    def clear_feed(self, feed_id: int) -> bool:
        """
        Clear feed data on emoncms server.

        First clear all data and then delete the feed.

        :Example :
            >>> self.clear_feed(feed_id=14)
            >>> True
        :param feed_id: int or str: The feed id to clear
        :return: bool: True if feed cleared with success.
        """
        return self._execute_simple_json_request(item_type="feed",
                                                 action="clear",
                                                 item_id=feed_id)

    def delete_feed(self, feed_id: int) -> bool:
        """
        Delete a feed on emoncms server.

        First clear all data, then reset the inputs processes
        and finally delete the feed.

        :Example :
            >>> self.delete_feed(feed_id=14)
            >>> True
        :param feed_id: int or str: The feed id to delete
        :return: bool: True if feed deleted with success.
        """
        result = False
        if self.clear_feed(feed_id=feed_id):
            if self.clear_process_feeds(feed_id=feed_id):
                if self._execute_simple_json_request(item_type="feed",
                                                     action="delete",
                                                     item_id=feed_id):
                    result = True
                else:
                    logger.warning(
                        "[EmoncmsSetApi] "
                        "Unable to delete feed id %s ",
                        feed_id
                    )
            else:
                logger.warning(
                    "[EmoncmsSetApi] "
                    "Unable to clear process list for feed id %s ",
                    feed_id
                )
        else:
            logger.warning(
                "[EmoncmsSetApi] Unable to clear data for feed id %s ",
                feed_id
            )

        return result

    def update_feed_field(self, feed_id: int, data: dict) -> bool:
        """
        Update feed field from emoncms server.

        Data dictonary parameter can contain :
            - tag : str: The feed node
            - name : str: The feed name
            - unit : str: The feed unit
            - public : int: Public status of the feed
        :Example :
            >>> self.update_feed_field(feed_id=18, data={"tag": "Node"})
            >>> True
        :param feed_id: int: The feed id to update.
        :param data: dict: The feed data dictionary.
        :return: bool: True on feed update success.
            ToDo:
                - what is datatype on emoncms?
                - string values must be tested or sanitized.
        """
        result, fields = False, EmoncmsHelper.prepare_feed_data(data)

        if Ut.is_int(feed_id, positive=True) \
                and Ut.is_dict(fields, not_null=True):

            params = {
                'id': feed_id,
                'fields': UJson.dumps_json(fields)
            }

            response = self._execute_request(
                '/feed/set.json',
                params=params,
                response_type="json"
            )

            if EmoncmsHelper.is_request_success(response):
                result = True
            else:
                logger.debug(
                    "[EmoncmsSetApi] Update feed field from emoncms api fail "
                    "Response : %s",
                    response
                )
        else:
            logger.debug(
                "[EmoncmsSetApi] Update feed field from emoncms api fail "
                "Required feed_id : %s or fields : %s",
                feed_id,
                fields,
            )
        return result

    @staticmethod
    def _get_request_params(actions: dict,
                            item_type: str,
                            action: str
                            ) -> Optional[tuple]:
        """
        Get request parameters from global dictionary.

        :Example :
            >>> EmoncmsSetApi._get_request_params(item_type="feed", action="clear", item_id=14)
            >>> True
        :param actions: dict: The global dictionary contening all request parameters
        :param action: str: The action id to execute
        :param item_type: str: The item_type to select (input or feed)
        :return: Optional[tuple]: Tuple (uri, params, response_type) of request parameters<br>
            or None
        """
        result = None
        if Ut.is_dict(actions, not_null=True) \
                and Ut.is_str(item_type, not_null=True) \
                and Ut.is_str(action, not_null=True):
            item_actions = actions.get(item_type)
            if Ut.is_dict(item_actions, not_null=True):
                item_action = item_actions.get(action)
                if Ut.is_dict(item_action, not_null=True) \
                        and Ut.is_str(item_action.get('uri'), not_null=True) \
                        and Ut.is_str(item_action.get('response_type'), not_null=True):
                    result = (
                        item_action.get('uri'),
                        item_action.get('params'),
                        item_action.get('response_type'),
                    )
        return result
