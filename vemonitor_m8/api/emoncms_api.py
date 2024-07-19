#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Emoncms api Helper"""
import logging
from typing import Optional
import requests
from ve_utils.utype import UType as Ut
from ve_utils.ujson import UJson
from vemonitor_m8.api.emon_data_helper import EmoncmsHelper

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class EmoncmsApi:
    """Emoncms api Helper"""
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
        self.active = Ut.str_to_bool(active)
        self.name = Ut.get_str(name)
        self.addr = Ut.get_str(addr)
        self.apikey = Ut.get_str(apikey)

    def is_ready(self) -> bool:
        """Test if is ready."""
        return Ut.is_str(self.addr, not_null=True)\
            and Ut.is_str(self.apikey, not_null=True) \
            and Ut.is_str(self.name, not_null=True)

    def _execute_request(self,
                         address: str,
                         req_type: str = 'get',
                         params: Optional[dict] = None,
                         data: Optional[dict] = None,
                         response_type: str = "text"
                         ) -> any:
        """
        Execute request to emoncms server.
        :Example :
            >>> self._execute_request(result={"success": "true"})
            >>> True
        :param address: str: The request route without domain and port
        :param req_type: str: The request type GET or POST
        :param params: Optional[dict]: The request parameters included on url
        :param data: Optional[dict]: The request data to send only for post request
        :param response_type: str: The response type (text or json)
        :return: any: <br>
            - Return string if response_type is text.<br>
            - Return dict or list if response_type is json.<br>
            - Return None if error occurs.
        """
        result = None
        if self.is_ready() and Ut.is_str(address, not_null=True):
            req = "%s%s" % (self.addr, address)
            if Ut.is_dict(params, not_null=True):
                params['apikey'] = self.apikey
            else:
                params = {'apikey': self.apikey}

            try:
                response = None
                if req_type == 'get':
                    response = requests.get(req, params=params)
                elif req_type == 'post':
                    response = requests.post(req, params=params, data=data)
                else:
                    logger.debug(
                        "[EmoncmsApi] Invalid request type %s, must be get or post.",
                        Ut.get_str(req_type))

                if response is not None and response.status_code in [200, 201]:
                    if response_type == "text":
                        result = response.text
                    elif response_type == "json":
                        result = response.json()
            except Exception as ex:
                logger.debug(
                    "[EmoncmsApi] %s Request fails with exception : %s",
                    Ut.get_str(req_type),
                    ex)

        else:
            logger.debug(
                "[EmoncmsApi] Invalid parameters to execute %s request or module not ready.",
                Ut.get_str(req_type)
            )
        return result

    def post_inputs(self,
                    node: str,
                    data: dict,
                    timestamp: float or None = None
                    ) -> Optional[dict]:
        """
        Post inputs using fulljson request on emoncms.

        """
        result, params = False, None
        if Ut.is_str(node, not_null=True)\
                and Ut.is_dict(data, not_null=True):
            params = {
                'node': node,
                'fulljson': UJson.dumps_json(data)
            }
            if timestamp is not None:
                timestamp = Ut.get_int(timestamp, 0)
                if Ut.is_int(timestamp, not_null=True):
                    params.update({"time": Ut.get_int(timestamp)})

        if Ut.is_dict(params, not_null=True):
            response = self._execute_request(
                '/input/post',
                req_type='post',
                params=params,
                response_type="json"
            )

            if EmoncmsHelper.is_request_success(response):
                result = True
            else:
                logger.debug(
                    "[EmoncmsApi] Post input fields for node %s from emoncms api fail "
                    "Response : %s",
                    node,
                    response)
        else:
            logger.debug(
                "[EmoncmsApi] Unable to Set input fields, "
                "required node : %s.",
                node
            )
        return result

    def input_bulk(self,
                   data: list,
                   timestamp: int or None = None,
                   sentat: int or None = None,
                   offset: int or None = None,
                   ) -> Optional[dict]:
        """Post inputs using bulk request on emoncms"""
        result, params = False, None
        if Ut.is_list(data, not_null=True):
            params = dict()  # {"data": UJson.dumps_json(data)}
            if Ut.is_int(timestamp, not_null=True):
                params.update({"time": timestamp})
            elif Ut.is_int(sentat, not_null=True):
                params.update({"sentat": sentat})
            elif Ut.is_int(offset):
                params.update({"offset": offset})

        if Ut.is_dict(params, not_null=True):

            response = self._execute_request(
                '/input/bulk',
                req_type='post',
                params=params,
                data={"data": UJson.dumps_json(data)},
                response_type="text"
            )

            if response == 'ok':
                result = True
            else:
                logger.debug(
                    "[EmoncmsApi] Post input fields from emoncms api fail "
                    "Data: %s - Response : %s",
                    data,
                    response)
        else:
            logger.debug(
                "[EmoncmsApi] Unable to Set input fields, "
                "required data(list) : %s.",
                data
            )
        return result

    def get_input(self,
                  node: Optional[str] = None,
                  name: Optional[str] = None
                  ) -> Optional[dict]:
        """
            Get input(s) data from emoncms Api.
                - all nodes and associated inputs
                    -> if node = None and inputName = None
                    -> {'Node': {'Input': {'data 1': 'value 1', ...}, ...}, ...}
                - inputs from specific node
                    -> if node value passed and inputName = None
                    -> {'Input': {'data 1': 'value 1', ...}, ...}
                - specific input from specific node
                    -> if node value passed and inputName passed
                    -> {'Input': {'data 1': 'value 1', ...}}

            Response if success return for all inputs
            'last time input', 'last value input', 'input process list'
        """
        result = None
        params = dict()
        if Ut.is_str(node, not_null=True):
            params['node'] = node
        if Ut.is_str(name, not_null=True):
            params['name'] = name

        response = self._execute_request('/input/get.json', params=params, response_type="json")

        if Ut.is_dict(response, not_null=True):
            result = response
        else:
            logger.debug(
                "[EmoncmsApi] Get input(s) from emoncms api fail "
                "Response : %s",
                response)
        return result

    def get_inputs_list(self,
                        node: Optional[str] = None,
                        name: Optional[str] = None
                        ) -> Optional[list]:
        """
        Get inputs list data from emoncms Api.


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
        response = self._execute_request('/input/list.json', response_type="json")
        if Ut.is_list(response, not_null=True):

            if Ut.is_str(node, not_null=True)\
                    or (Ut.is_str(node, not_null=True)
                        and Ut.is_str(name, not_null=True)):
                result = list()
                for item in response:
                    if Ut.is_dict(item)\
                            and item.get('nodeid') == node\
                            and ((Ut.is_str(name, not_null=True)
                                  and item.get('name') == name)
                                 or not Ut.is_str(name, not_null=True)):
                        result.append(item)
            else:
                result = response
        else:
            logger.debug(
                "[EmoncmsApi] Get inputs list from emoncms api fail "
                "Response : %s",
                response)
        return result

    def get_inputs_conf(self,
                        node: Optional[str] = None,
                        name: Optional[str] = None
                        ) -> Optional[dict]:
        """
        Get inputs list data from emoncms Api.

        Response if success return for all inputs :
                                    'input id',
                                    'input process list'
        """
        result = None
        response = self._execute_request('/input/get_inputs.json', response_type="json")
        if Ut.is_dict(response, not_null=True):
            result = response
            if Ut.is_str(node, not_null=True):
                result = response.get(node)

                if Ut.is_str(name, not_null=True):
                    result = result.get(name)

        else:
            logger.debug(
                "[EmoncmsApi] Get inputs configuration from emoncms api fail "
                "Response : %s",
                response)
        return result

    def get_input_process_list(self, input_id: int):
        """
            Get input process list

            Response if success return
            comma separated process list with format :
            'type process':'feed id'
        """
        result, params = None, None
        input_id = Ut.get_int(input_id, default=0)
        if Ut.is_int(input_id, positive=True):
            params = {'inputid': input_id}
        if Ut.is_dict(params, not_null=True):
            response = self._execute_request(
                '/input/process/get',
                params=params,
                response_type="text"
            )
            if Ut.is_str(response):
                result = response
            else:
                logger.debug(
                    "[EmoncmsApi] Get input process list from emoncms api fail "
                    "Response : %s",
                    response
                )
        else:
            logger.debug(
                "[EmoncmsApi] Get input process list from emoncms api fail "
                "Required input id : %s",
                input_id
            )
        return result

    def get_feeds_list(self,
                       user_id: int or None = None
                       ):
        """
        Get feed list data from emoncms Api.
        if id_user is set get all feeds for this user.
        Else get all feeds for authenticated user

        Response if success return for all feeds :
                                    'feed id',
                                    'feed name' ,
                                    'user id' ,
                                    'tag (node name)' ,
                                    'datatype' ,
                                    'public',
                                    'size',
                                    'engine',
                                    'time',
                                    'value',
                                    'processList',
                                    'unit'
        """
        result, params = None, None
        user_id = Ut.get_int(user_id, default=0)
        if Ut.is_int(user_id, positive=True):
            params = {'userid': user_id}

        response = self._execute_request('/feed/list.json', params=params, response_type="json")
        if Ut.is_list(response, not_null=True):
            result = response
        else:
            logger.debug(
                "[EmoncmsApi] Get inputs list from emoncms api fail "
                "Response : %s",
                response)
        return result

    def get_feed(self,
                 feed_id: int,
                 req_type: str = "fields",
                 field: Optional[str] = None
                 ):
        """
            Get feed fields data from emoncms Api for feed with id id_feed.
            If field is set get only this field
            Else get all feed fields

            Response if success return for requested feed field : "string"

            Response if success return for all feed fields  : dict
                                        'feed id',
                                        'feed name' ,
                                        'user id' ,
                                        'tag (node name)' ,
                                        'datatype' ,
                                        'public',
                                        'size',
                                        'engine',
                                        'processList',
                                        'time',
                                        'value'
        """
        result, params = None, dict()
        feed_id = Ut.get_int(feed_id, default=0)
        if Ut.is_int(feed_id, not_null=True):
            response = None
            params.update({'id': feed_id})
            if req_type == "fields":
                if Ut.is_str(field, not_null=True):
                    params.update({'field': field})
                response = self._execute_request('/feed/get.json',
                                                 params=params,
                                                 response_type="json")
            elif req_type == "meta":
                response = self._execute_request('/feed/getmeta.json',
                                                 params=params,
                                                 response_type="json")
            elif req_type == "timevalue":
                response = self._execute_request('/feed/timevalue.json',
                                                 params=params,
                                                 response_type="json")
            elif req_type == "value":
                response = self._execute_request('/feed/value.json',
                                                 params=params,
                                                 response_type="json")

            if response is not None:
                result = response
            else:
                logger.debug(
                    "[EmoncmsApi] Get feed : request: %s - field : %s from emoncms api fail "
                    "Response : %s",
                    req_type,
                    field,
                    response)
        return result

    def get_sorted_feeds_list(self,
                              sort_data: dict,
                              user_id: int or None = None,
                              ) -> Optional[list]:
        """
        Get sorted feed list data from emoncms Api.
        """
        result = None
        feeds = self.get_feeds_list(user_id)
        sorted_keys = EmoncmsHelper.get_sorted_keys(sort_data)
        if Ut.is_list(feeds, not_null=True) \
                and Ut.is_dict(sort_data, not_null=True) \
                and Ut.is_list(sorted_keys, not_null=True):
            result = list()
            for item in feeds:
                if Ut.is_dict(item, not_null=True):
                    test = True
                    for key in sorted_keys:
                        if key in item \
                                and sort_data.get(key) != item.get(key):
                            test = False
                    if test is True:
                        result.append(item)
        return result
