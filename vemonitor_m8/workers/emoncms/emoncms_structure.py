#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Emoncms api Helper"""
import logging
from typing import Optional
from ve_utils.utype import UType as Ut
from vemonitor_m8.workers.emoncms.emon_data_helper import EmoncmsHelper
from vemonitor_m8.workers.emoncms.emoncms_set_api import EmoncmsSetApi
from vemonitor_m8.workers.emoncms.delta_structure import DeltaStructure
from vemonitor_m8.conf_manager.loader import Loader
from vemonitor_m8.conf_manager.schema_validate import SchemaValidate as sValid

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "0.0.1"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class EmoncmsStructure:
    """Emoncms app Helper"""
    def __init__(self,
                 connector: dict,
                 ):
        """
        :param connector: dict: emoncms api connector parameters
        """
        self.api = EmoncmsSetApi(**connector)

    def init_inputs_structure(self,
                              node: str,
                              data: dict,
                              delta_structure: DeltaStructure,
                              global_priority: Optional[str] = None
                              ) -> bool:
        """Init inputs data structure."""
        result = False
        if Ut.is_str(node, not_null=True) \
                and Ut.is_dict(data, not_null=True) \
                and isinstance(delta_structure, DeltaStructure):
            delta_structure.add_inputs_conf_list(list(data.keys()))
            inputs = self.api.get_inputs_list(node=node)
            # if empty inputs from node
            if not Ut.is_list(inputs, not_null=True):
                delta_structure.add_inputs_to_set()
                if self.set_new_inputs(node=node,
                                       delta_structure=delta_structure
                                       ):
                    inputs = self.api.get_inputs_list(node=node)

            if Ut.is_list(inputs, not_null=True):

                inputs_get = list()
                result = True
                for input_item in inputs:
                    input_name = Ut.get_str(input_item.get('name'))
                    input_data = data.get(input_name)

                    if Ut.is_dict(input_item, not_null=True) \
                            and Ut.is_dict(input_data, not_null=True) \
                            and Ut.is_dict(
                                input_data.get('feeds'),
                                not_null=True) \
                            and EmoncmsStructure.set_input_data(
                                    input_item=input_item,
                                    data=input_data,
                                    delta_structure=delta_structure,
                                    global_priority=global_priority):
                        inputs_get.append(input_name)

                        process_list = EmoncmsStructure.get_process_to_list(
                            input_item.get('processList')
                        )
                        if not EmoncmsStructure.update_process_list_structure(
                                process_list=process_list,
                                input_name=input_name,
                                input_id=input_data.get('id'),
                                delta_structure=delta_structure):
                            result = False

                delta_structure.add_inputs_get_list(inputs_get)
                delta_structure.add_inputs_to_set()
        return result

    def init_feeds_structure(self,
                             node: str,
                             data: dict,
                             delta_structure: DeltaStructure,
                             global_priority: Optional[str] = None
                             ) -> bool:
        """Init feeds data structure."""
        result = False
        if Ut.is_str(node, not_null=True) \
                and Ut.is_dict(data, not_null=True) \
                and isinstance(delta_structure, DeltaStructure):
            feeds = self.api.get_sorted_feeds_list(
                {"tag": node}
            )
            result = True
            for input_name, input_data in data.items():
                if Ut.is_dict(input_data.get('feeds'), not_null=True):
                    if not EmoncmsStructure.get_feeds_data(
                            feeds=feeds,
                            input_name=input_name,
                            data=input_data.get('feeds'),
                            delta_structure=delta_structure,
                            global_priority=global_priority):
                        result = False
                    process_list = EmoncmsStructure.get_process_to_list(
                        input_data.get('process_list')
                    )
                    if not EmoncmsStructure.update_process_list_structure(
                            process_list=process_list,
                            input_name=input_name,
                            input_id=input_data.get('id'),
                            delta_structure=delta_structure):
                        result = False

        return result

    def init_input_feed_structure(self,
                                  data: dict,
                                  global_priority: Optional[str] = None
                                  ) -> bool:
        """
        Init Inputs/feeds data structure verification, and update if needed.
        """
        result = False
        if Ut.is_dict(data, not_null=True):
            result = True
            for node, input_items in data.items():
                if Ut.is_str(node, not_null=True):
                    node_delta = DeltaStructure()
                    is_init_inputs_structure = self.init_inputs_structure(
                        node=node,
                        data=input_items,
                        delta_structure=node_delta,
                        global_priority=global_priority
                    )

                    is_init_feeds_structure = self.init_feeds_structure(
                        node=node,
                        data=input_items,
                        delta_structure=node_delta,
                        global_priority=global_priority
                    )
                    if is_init_inputs_structure\
                            and is_init_feeds_structure:
                        if not self.init_structure(node=node,
                                                   data=input_items,
                                                   delta_structure=node_delta
                                                   ):
                            result = False
                    else:
                        result = False
        return result

    def init_structure(self,
                       node: str,
                       data: dict,
                       delta_structure: DeltaStructure
                       ) -> bool:
        """
        Run updates on inputs/feeds structure from DeltaStructure object.
        """
        result = False
        if Ut.is_dict(data, not_null=True) \
                and isinstance(delta_structure, DeltaStructure) \
                and Ut.is_str(node, not_null=True):
            # Add new inputs
            result = self.set_new_inputs(node=node,
                                         delta_structure=delta_structure
                                         )
            # Add new feeds
            if not self.set_new_feeds(
                    node=node,
                    delta_structure=delta_structure,
                    data=data
            ):
                result = False

            if delta_structure.has_inputs_to_update():
                if self.update_inputs(delta_structure.inputs_update):
                    logger.info(
                        "Data updated on emoncms inputs."
                    )
                else:
                    result = False

            if delta_structure.has_feeds_to_update():
                if self.update_feeds(delta_structure.feeds_update):
                    logger.info(
                        "Data updated on emoncms inputs."
                    )
                else:
                    result = False
        return result

    def set_new_inputs(self,
                       node: str,
                       delta_structure: DeltaStructure
                       ) -> bool:
        """Set new inputs on emoncms server."""
        result = True
        if delta_structure.has_inputs_to_set():
            if self._set_new_inputs_on_server(node=node,
                                              inputs=delta_structure.inputs_set
                                              ):
                logger.info(
                    "New inputs added to emoncms."
                )
            else:
                result = False
        return result

    def _set_new_inputs_on_server(self,
                                  node: str,
                                  inputs: list
                                  ) -> bool:
        """
        Set new inputs on emoncms server.
        """
        result = False
        if Ut.is_list(inputs, not_null=True)\
                and Ut.is_str(node, not_null=True):
            new_items = dict()
            for key in inputs:
                if Ut.is_str(key, not_null=True):
                    new_items[key] = 0
            if Ut.is_dict(new_items, not_null=True):
                result = self.api.post_inputs(node=node, data=new_items)
        return result

    def update_inputs(self,
                      updates: dict
                      ) -> bool:
        """Update inputs data on emoncms."""
        result = False
        if Ut.is_dict(updates, not_null=True):
            result = True
            for key, update in updates.items():
                input_id = Ut.get_int(update.get('id'), 0)
                if Ut.is_int(input_id, positive=True):
                    if Ut.is_str(update.get('description')):
                        if not self.api.set_input_fields(
                                input_id=input_id,
                                description=update.get('description')):
                            result = False
                    elif Ut.is_list(update.get('process_list'), not_null=True):
                        process_list = [
                            EmoncmsStructure.format_process_list(
                                process=x[0],
                                feed_id=x[1]
                            )
                            for x in update.get('process_list')
                            if Ut.is_tuple(x, eq=2)
                        ]
                        data = {
                            key: {
                                'input_id': input_id,
                                'process_list': process_list
                            }
                        }
                        if not self.set_process_list(data):
                            result = False
                else:
                    result = False
        return result

    def set_new_feeds(self,
                      node: str,
                      data: dict,
                      delta_structure: DeltaStructure,
                      ) -> bool:
        """
        Set new feeds on emoncms server.
        """
        result = False
        if Ut.is_dict(data, not_null=True) \
                and isinstance(delta_structure, DeltaStructure) \
                and Ut.is_str(node, not_null=True):
            result = True
            if delta_structure.has_feeds_to_set():
                process_list = self._set_new_feeds_on_server(
                    node=node,
                    feeds=delta_structure.feeds_set,
                    data=data
                )
                if not (Ut.is_dict(process_list, not_null=True)
                        and self.set_process_list(process_list)):
                    result = False
                else:
                    logger.info(
                        "New feeds added to emoncms, "
                        "and corresponding process list to inputs."
                    )
        return result

    def _set_new_feeds_on_server(self,
                                 node: str,
                                 feeds: dict,
                                 data: dict
                                 ) -> Optional[dict]:
        """
        Set new feeds on emoncms server.
        """
        result = None
        if Ut.is_dict(feeds, not_null=True)\
                and Ut.is_str(node, not_null=True)\
                and Ut.is_dict(data, not_null=True):
            result = dict()
            for key, feed_list in feeds.items():
                if Ut.is_str(key, not_null=True)\
                        and Ut.is_dict(data.get(key))\
                        and Ut.is_dict(data[key].get('feeds')):
                    for feed_name in feed_list:
                        if Ut.is_str(feed_name, not_null=True)\
                                and Ut.is_dict(
                                    data[key]['feeds'].get(feed_name)):
                            feed_data = {
                                'tag': node,
                                'name': feed_name
                            }
                            feed_data.update(
                                Ut.get_items_from_dict(
                                    data[key]['feeds'].get(feed_name),
                                    [
                                        'datatype',
                                        'engine',
                                        'unit',
                                        'public',
                                        'interval'
                                    ]
                                )
                            )
                            feed_id = self.api.create_feed(feed_data)
                            process = Ut.get_int(
                                data[key]['feeds'][feed_name].get('process'),
                                1
                            )
                            input_id = Ut.get_int(data[key].get('id'), 0)
                            if Ut.is_int(process, positive=True)\
                                    and Ut.is_int(input_id, positive=True) \
                                    and Ut.is_int(feed_id, positive=True):
                                data[key]['feeds'][feed_name].update({
                                    'id': feed_id
                                })
                                Ut.init_dict_key(result, key, dict())
                                if not EmoncmsStructure._set_process_list_data(
                                            process_list=result[key],
                                            input_id=data[key].get('id'),
                                            feed_id=feed_id,
                                            process=process
                                        ):
                                    logger.warning(
                                        "Error : "
                                        "Failed to set process list data "
                                        "for new feed."
                                        "Node : %s, feedName: %s, data: %s",
                                        node, feed_name, data[key]
                                    )
                            else:
                                logger.warning(
                                    "Error : "
                                    "Failed to set new feed on emoncms server."
                                    "Node : %s, feedName: %s, data: %s",
                                    node, feed_name, data[key]
                                )
        return result

    def update_feeds(self,
                     updates: dict
                     ) -> bool:
        """
        Update feeds data on emoncms from updates dictionary.

        :Example :
            >>> data = {'input_id': 26, 'process_list': ['1:23', '4:24']}
            >>> self.update_feeds(updates=data)
            >>> True
        :param updates: dict: The feeds updates to execute on emoncms api
        :return: bool: True if all feeds updated.
        """
        result = False
        if Ut.is_dict(updates, not_null=True):
            result = True
            for update in updates.values():
                feed_id = Ut.get_int(update.get('id'), 0)
                if Ut.is_int(feed_id, positive=True):
                    feed_data = Ut.get_items_from_dict(
                                    update,
                                    ['tag', 'name', 'unit', 'public']
                                )
                    if not self.api.update_feed_field(feed_id, feed_data):
                        logger.error(
                            "Error: Failed to update feed id %s on emoncms."
                            "data : %s.",
                            feed_id, feed_data
                        )
                        result = False
        return result

    def set_process_list(self, data: dict) -> bool:
        """
        Set input process list on emoncms Api.

        :Example :
            >>> process_data = {
                'input_id': 26,
                'process_list': ['1:23', '4:24']
            }
            >>> self.set_process_list(data=process_data)
            >>> True
        :param data: dict: The process list data to set on emoncms api
        :return: bool: True if all process list updated.
        """
        result = False
        if Ut.is_dict(data, not_null=True):
            result = True
            for process_list in data.values():
                if Ut.is_dict(process_list, not_null=True)\
                        and Ut.is_int(
                            process_list.get('input_id'),
                            positive=True)\
                        and Ut.is_list(
                            process_list.get('process_list'),
                            not_null=True):
                    if not self.api.set_input_process_list(
                                input_id=process_list.get('input_id'),
                                process_list=process_list.get('process_list')
                            ):
                        logger.error(
                            "Error: "
                            "Failed to update input process list on emoncms. "
                            "input id: %s - data : %s.",
                            process_list.get('input_id'),
                            process_list.get('process_list')
                        )
                        result = False
                else:
                    logger.error(
                        "Error: "
                        "Failed to update input process list on emoncms. "
                        "Bad format data : %s.",
                        process_list
                    )
                    result = False
        return result

    @staticmethod
    def is_master_data_conf_priority(local_priority: str,
                                     global_priority: str
                                     ) -> bool:
        """
        Test if is master data configuration priority.

        Define inputs/feeds structure priority over emoncms existent structure.
        local_priority define input/feed priority,
        and global_priority define global configuration priority.
        If one of them is master and global_priority is not slave, return True.

        :Example :
                >>> EmoncmsStructure.is_master_data_conf_priority("master", "")
                >>> True
                >>> EmoncmsStructure.is_master_data_conf_priority("", "")
                >>> False
        :param local_priority: str:
            Define local input/feed configuration priority
        :param global_priority: str:
            Define global structure configuration priority
        :return: bool: True If one of local or global priority is master.
        """
        return (local_priority == "master" or global_priority == "master") \
            and not global_priority == "slave"

    @staticmethod
    def set_input_data(input_item: dict,
                       data: dict,
                       delta_structure: DeltaStructure,
                       global_priority: Optional[str] = None
                       ) -> bool:
        """
        Set the input data from configuration and server sources.

        Combine input data from existing emoncms data, and configuration data.
        The Description field will be updated,
        depending on global or local data priority,
        and the description field values from existing emoncms data,
        and configuration data
        :param input_item: dict: The input data from emoncms server
        :param data: dict: The input data from vemonitor configuration
        :param delta_structure: DeltaStructure: The DeltaStructure object
        :param global_priority: Optional[str]: The global priority value
        :return: bool: Return True if input data
            from emoncms server and from vemonitor configuration is valid.
        """
        result = False
        if Ut.is_dict(input_item, not_null=True) \
                and Ut.is_dict(data, not_null=True):
            input_id = Ut.get_int(input_item.get('id'))
            input_name = Ut.get_str(input_item.get('name'))
            description = Ut.get_str(input_item.get('description'), "")
            process_list = Ut.get_str(input_item.get('processList'))
            last_time = Ut.get_int(input_item.get('time'))
            last_value = Ut.get_float(input_item.get('value'))

            if Ut.is_int(input_id, positive=True):
                data.update({
                    'id': input_id,
                    'process_list': process_list,
                    'last_time': last_time,
                    'last_value': last_value
                })
                data_conf_priority = EmoncmsStructure.is_master_data_conf_priority(
                    local_priority=data.get('data_priority'),
                    global_priority=global_priority
                )
                if not Ut.is_str(data.get('description'), not_null=True) \
                        or not data_conf_priority:
                    data.update({'description': description})
                elif data_conf_priority \
                        and data.get('description', "") != description:
                    delta_structure.add_inputs_update_item(
                        input_name=input_name,
                        input_id=input_id,
                        key='description',
                        value=Ut.get_str(data.get('description'), "")
                    )
                result = True
        return result

    @staticmethod
    def set_feed_data(input_name: str,
                      item: dict,
                      data: dict,
                      delta_structure: DeltaStructure,
                      global_priority: Optional[str] = None
                      ) -> bool:
        """
        Set the feed data from configuration and server sources.

        Combine feed data from existing emoncms data, and configuration data.
        The fields will be updated,
        depending on global or local data priority,
        and the field values from existing emoncms data,
        and configuration data
        :param input_name: str: The input name
        :param item: dict: The feed data from emoncms server
        :param data: dict: The feed data from vemonitor configuration
        :param delta_structure: DeltaStructure: The DeltaStructure object
        :param global_priority: Optional[str]: The global priority value
        :return: bool: Return True if feed data
            from emoncms server and from vemonitor configuration is valid.
        """
        result = False
        if Ut.is_dict(item, not_null=True) \
                and Ut.is_dict(data, not_null=True) \
                and isinstance(delta_structure, DeltaStructure):
            item_id = Ut.get_int(item.get('id'))
            user_id = Ut.get_int(item.get('userid'))
            public = Ut.get_int(item.get('public'), 0)
            size = Ut.get_int(item.get('size'))
            engine = Ut.get_int(item.get('engine'))
            unit = Ut.get_str(item.get('unit'))
            last_time = Ut.get_int(item.get('time'))
            last_value = Ut.get_float(item.get('value'))

            if Ut.is_int(item_id, positive=True):
                data.update({
                    'id': item_id,
                    'user_id': user_id,
                    'size': size,
                    'last_time': last_time,
                    'last_value': last_value
                })
                data_conf_priority = EmoncmsStructure.is_master_data_conf_priority(
                    local_priority=data.get('data_priority'),
                    global_priority=global_priority
                )
                if not Ut.is_int(data.get('public'), eq=1) \
                        or not data_conf_priority:
                    data.update({'public': public})
                elif data_conf_priority \
                        and data.get('public', 0) != public:
                    delta_structure.add_feeds_update_item(
                        input_name=input_name,
                        feed_id=item_id,
                        key='public',
                        value=Ut.get_str(data.get('public', ""))
                    )
                if not Ut.is_int(data.get('engine'), positive=True) \
                        or not data_conf_priority:
                    data.update({'engine': engine})
                elif data_conf_priority \
                        and data.get('engine', 0) != engine:
                    delta_structure.add_feeds_update_item(
                        input_name=input_name,
                        feed_id=item_id,
                        key='engine',
                        value=Ut.get_str(data.get('engine', ""))
                    )

                if not Ut.is_str(data.get('unit'), not_null=True) \
                        or not data_conf_priority:
                    data.update({'unit': unit})
                elif data_conf_priority \
                        and data.get('unit', "") != unit:
                    delta_structure.add_feeds_update_item(
                        input_name=input_name,
                        feed_id=item_id,
                        key='unit',
                        value=Ut.get_str(data.get('unit', ""))
                    )
                result = True
        return result

    @staticmethod
    def sort_process_list(data: tuple) -> int:
        """Return key for sorting process list data."""
        return data[1]

    @staticmethod
    def get_process_list_to_update(server: list, conf: list) -> Optional[list]:
        """
        Get combined feed data from input name.
        """
        result = None
        if Ut.is_list(conf, not_null=True):
            conf.sort(key=EmoncmsStructure.sort_process_list)

        if Ut.is_list(server, not_null=True):
            server.sort(key=EmoncmsStructure.sort_process_list)
        if not (Ut.is_list(conf, not_null=True)
                and server == conf):
            result = conf
        return result

    @staticmethod
    def get_feeds_data(feeds: list,
                       input_name: str,
                       data: dict,
                       delta_structure: DeltaStructure,
                       global_priority: Optional[str] = None
                       ) -> bool:
        """Get feed data from node and list of names."""
        result = False
        if Ut.is_str(input_name, not_null=True) \
                and Ut.is_dict(data, not_null=True) \
                and isinstance(delta_structure, DeltaStructure):

            feeds_get = list()
            feeds_conf = list(data.keys())
            process_list = list()
            if Ut.is_list(feeds, not_null=True):
                for feed_item in feeds:
                    feed_name = Ut.get_str(feed_item.get('name'))
                    feed_data = data.get(feed_name)
                    if Ut.is_dict(feed_item, not_null=True) \
                            and Ut.is_dict(feed_data, not_null=True) \
                            and EmoncmsStructure.set_feed_data(
                            input_name=input_name,
                            item=feed_item,
                            data=feed_data,
                            delta_structure=delta_structure,
                            global_priority=global_priority):
                        feeds_get.append(feed_name)
                        process_list.append(
                            (
                                Ut.get_int(feed_data.get('process'), 0),
                                Ut.get_int(feed_item.get('id'), 0)
                            )
                        )

            delta_structure.add_feeds_get_list(feeds_get)
            delta_structure.add_feeds_conf_list(feeds_conf)
            delta_structure.set_conf_process_list_item(
                input_name=input_name,
                process_list=process_list
            )
            delta_structure.add_feeds_to_set(
                input_name=input_name,
                feeds_get=feeds_get,
                feeds_conf=feeds_conf
            )
            result = True
        return result

    @staticmethod
    def update_process_list_structure(process_list: list,
                                      input_name: str,
                                      input_id: int,
                                      delta_structure: DeltaStructure
                                      ) -> bool:
        """Get and compare process list structure."""
        result = False
        process_update = EmoncmsStructure.get_process_list_to_update(
            server=process_list,
            conf=delta_structure.get_conf_process_list_key(input_name)
        )
        if Ut.is_list(process_update, not_null=True):
            if delta_structure.add_inputs_update_item(input_name=input_name,
                                                      input_id=input_id,
                                                      key='process_list',
                                                      value=process_update
                                                      ):
                result = True
        else:
            result = True
        return result

    @staticmethod
    def _load_structure_config(file_path: Optional[str] = None) -> dict:
        """
        Load the emoncms configuration file with the data structure.

        The file must be named emoncms.yaml.

        :Example :
            >>> EmoncmsStructure.update_feeds(file_path=None)
            >>> {
            >>> "node1": {
            >>>    "input1": {
            >>>         "description": "Input Description",
            >>>         "feeds": {
            >>>             "Feed1": {"process": 1, "engine": 1, "unit": "W",}
            >>>         }
            >>>     }
            >>> }
            >>>}
        :param file_path: Optional[str]:
            The feeds updates to execute on emoncms api.
        :return: dict: The dictionary read from emoncms yaml file.
        """
        loader = Loader(file_names="emoncms.yaml", file_path=file_path)
        data = loader.get_yaml_config()
        return sValid.validate_data(data.get('Structure'), "emoncms")

    @staticmethod
    def _set_process_list_data(process_list: dict,
                               input_id: int,
                               feed_id: int,
                               process: int
                               ) -> bool:
        """
        Set process list data to add on server.

        :Example :
            >>> EmoncmsStructure._set_process_list_data(
            >>>     process_list={},
            >>>     input_id=18,
            >>>     feed_id=17,
            >>>     process=1
            >>> )
            >>>
        :param process_list: dict:
        :param input_id: int: Input id to update the process list
        :param feed_id: int: Feed id to update the process list
        :param process: int: The process number
        :return: dict: A dictionary of formatted process list.
        """
        result = False
        process = Ut.get_int(process, 0)
        input_id = Ut.get_int(input_id, 0)
        feed_id = Ut.get_int(feed_id, 0)
        if Ut.is_int(process, positive=True) \
                and Ut.is_int(input_id, positive=True) \
                and Ut.is_int(feed_id, positive=True):
            Ut.init_dict_key(process_list, 'process_list', list())
            process_list.update({'input_id': input_id})
            process_list['process_list'].append(
                EmoncmsHelper.format_process_list(
                    process=process,
                    feed_id=feed_id
                )
            )
            result = True
        return result

    @staticmethod
    def format_process_list(process: int, feed_id: int) -> str:
        """Format process list data."""
        if Ut.is_int(process) and Ut.is_int(feed_id):
            return f"{process}:{feed_id}"
        return "0:0"

    @staticmethod
    def get_process_to_list(process: str) -> list:
        """Format process list data."""
        result = None
        if Ut.is_str(process, not_null=True):
            process_list = EmoncmsStructure.get_comma_separated_values_to_list(
                process
            )
            if Ut.is_list(process_list, not_null=True):
                result = list()
                for item in process_list:
                    if Ut.is_str(item, not_null=True):
                        tmp = item.split(':')
                        if Ut.is_list(tmp, eq=2):
                            proc = Ut.get_int(tmp[0], 0)
                            feed_id = Ut.get_int(tmp[1], 0)
                            if Ut.is_int(proc, positive=True)\
                                    and Ut.is_int(feed_id, positive=True):
                                result.append((proc, feed_id))
        return result

    @staticmethod
    def get_comma_separated_values_to_list(data: str) -> Optional[list]:
        """Format process list data."""
        result = None
        if Ut.is_str(data, not_null=True):
            result = data.split(',')
            if not Ut.is_list(result, not_null=True):
                result = None
        return result

    @staticmethod
    def get_list_to_comma_separated_values(data: list) -> Optional[str]:
        """Format process list data."""
        result = None
        if Ut.is_list(data, not_null=True):
            result = ''
            for key, item in enumerate(data):
                if key == 0:
                    result = f"'{item}'"
                else:
                    result = f'{result},{item}'
        return result
