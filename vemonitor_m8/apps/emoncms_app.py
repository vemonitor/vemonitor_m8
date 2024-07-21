#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Emoncms api Helper"""
import logging
import time

from ve_utils.utype import UType as Ut
from vemonitor_m8.api.emoncms_api import EmoncmsApi

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "Apache"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class EmoncmsApp:
    """Emoncms app Helper"""
    def __init__(self,
                 connector: dict,
                 ):
        """
        :param connector: dict: emoncms api connector parameters
        """
        self.api = EmoncmsApi(**connector)

    def is_ready(self):
        """Test if is ready."""
        return isinstance(self.api, EmoncmsApi) and self.api.is_ready()

    def ping(self):
        """Ping Emoncms Server."""
        result = False
        if self.is_ready():
            result = self.api.ping()
        return result

    @staticmethod
    def get_data_time(point: dict):
        """Get time from data point"""
        if Ut.is_dict(point, not_null=True) \
                and Ut.is_numeric(point.get("time"), not_null=True):
            return Ut.get_int(point.get("time"))
        return None

    @staticmethod
    def get_ordered_data_points(data: list):
        """Get time from data point"""
        if Ut.is_list(data, not_null=True):
            return sorted(data, key=lambda k: k.get('time'), reverse=True)
        return None

    @staticmethod
    def control_data_time(data: list):
        """Control data time."""
        result = None
        if Ut.is_list(data, not_null=True):
            tmp_times = list()

            result = {
                'avg_interval': 0,
                'intervals': list(),
                'min': 0,
                'max': 0,
            }
            for i, point in enumerate(data):
                point_time = Ut.get_int(EmoncmsApp.get_data_time(point))
                if Ut.is_int(point_time, not_null=True):
                    if i > 0:
                        result['intervals'].append(point_time - tmp_times[-1])
                    tmp_times.append(point_time)

                else:
                    result = None
                    break
            if Ut.is_dict(result, not_null=True)\
                    and Ut.is_list(result.get('intervals'), not_null=True):
                time_ref = Ut.get_int(round(time.time(), 0))
                result['min'] = min(tmp_times)
                result['max'] = max(tmp_times)
                result['offset'] = time_ref - result['max']
                result['len'] = len(tmp_times)
                result['interval_total'] = result['max'] - result['min']
                result['avg_interval'] = sum(result['intervals']) / len(result['intervals'])
        return result

    @staticmethod
    def prepare_input_bulk_data_point(node: str,
                                      cols: list,
                                      data: list,
                                      time_stats: dict
                                      ):
        """Prepare input bulk request data point."""
        result = None
        if Ut.is_str(node, not_null=True) \
                and Ut.is_list(cols, not_null=True) \
                and Ut.is_list(data, not_null=True) \
                and Ut.is_dict(time_stats, not_null=True):

            offset = 0
            result, item = list(), [offset, node]
            nb_intervals = len(time_stats['intervals'])

            for i, point in enumerate(data):
                if Ut.is_dict(point, not_null=True) \
                        and Ut.is_numeric(point.get("time"), not_null=True):
                    for key, value in point.items():
                        if key in cols:
                            item.append({key: value})
                    result.append(item)
                    if i < nb_intervals:
                        offset += time_stats['intervals'][i]
                        item = [offset, node]

        return result

    @staticmethod
    def prepare_input_bulk_data(data: dict,
                                input_structure: dict
                                ):
        """
        Prepare input bulk request data.
        """
        result, offset = None, None
        if Ut.is_dict(data, not_null=True) \
                and Ut.is_dict(input_structure, not_null=True):
            result = list()
            # order data points by time
            for node, item_list in data.items():
                if Ut.is_list(item_list, not_null=True):

                    item_values = EmoncmsApp.get_ordered_data_points(item_list)
                    time_stats = EmoncmsApp.control_data_time(item_values)
                    if Ut.is_dict(time_stats, not_null=True)\
                            and Ut.is_list(input_structure.get(node), not_null=True):
                        offset = time_stats.get("offset")
                        cols = input_structure.get(node)
                        data_points = EmoncmsApp.prepare_input_bulk_data_point(
                            node=node,
                            cols=cols,
                            data=item_values,
                            time_stats=time_stats
                        )
                        if Ut.is_list(data_points, not_null=True):
                            result = result + data_points
        return result, offset

    @staticmethod
    def data_cache_loop(data: dict):
        """Loop on inputs data cache"""
        if Ut.is_dict(data, not_null=True):
            keys = list(data.keys())
            keys.sort()
            for key in keys:
                if Ut.is_dict(data.get(key), not_null=True):
                    point_time = Ut.get_int(key, 0)
                    yield point_time, data.get(key)

    @staticmethod
    def control_interval_data_cache(data: dict):
        """Get time stats from inputs data cache."""
        result = None
        if Ut.is_dict(data, not_null=True):
            tmp_times = list()

            result = {
                'avg_interval': 0,
                'intervals': list(),
                'min': 0,
                'max': 0,
            }
            keys = list(data.keys())
            keys.sort()
            for i, point_time in enumerate(keys):
                point_time = Ut.get_int(point_time, 0)
                if Ut.is_int(point_time, positive=True):
                    if i > 0:
                        result['intervals'].append(point_time - tmp_times[-1])
                    tmp_times.append(point_time)
                    i += 1

            if Ut.is_dict(result, not_null=True) \
                    and Ut.is_list(result.get('intervals'), not_null=True):
                time_ref = Ut.get_int(round(time.time(), 0))
                result['time_ref'] = time_ref
                result['min'] = min(tmp_times)
                result['max'] = max(tmp_times)
                result['offset'] = time_ref - result['max']
                result['len'] = len(tmp_times)
                result['interval_total'] = result['max'] - result['min']
                result['avg_interval'] = sum(result['intervals']) / len(result['intervals'])
        return result

    @staticmethod
    def get_formatted_columns(point_items: dict, cols: list):
        """Get formatted columns from data cache."""
        return [{key: value} for key, value in point_items.items() if key in cols]

    @staticmethod
    def prepare_bulk_from_cache(data: dict,
                                input_structure: dict
                                ):
        """
        Prepare input bulk request data from inputs data cache.
        """
        result, offset = None, None
        if Ut.is_dict(data, not_null=True) \
                and Ut.is_dict(input_structure, not_null=True):
            result = list()
            time_stats = EmoncmsApp.control_interval_data_cache(data)
            if Ut.is_dict(time_stats, not_null=True):
                offset = time_stats.get('offset')
                for point_time, point in EmoncmsApp.data_cache_loop(data):
                    for node, point_items in point.items():
                        cols = input_structure.get(node)
                        if Ut.is_dict(time_stats, not_null=True) \
                                and Ut.is_list(cols, not_null=True):
                            tmp = EmoncmsApp.get_formatted_columns(
                                point_items=point_items,
                                cols=cols
                            )
                            offset_item = (point_time - time_stats.get('time_ref')) + offset
                            tmp.insert(0, offset_item)
                            tmp.insert(1, node)
                            result.append(tmp)
        return result, offset
