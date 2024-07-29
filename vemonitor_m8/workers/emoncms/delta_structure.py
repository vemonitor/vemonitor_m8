"""Emoncms Input Model."""

from ve_utils.utype import UType as Ut


class DeltaStructure:
    """This Class is representing Emoncms Delta Structure Model."""
    def __init__(self):
        """
        Initialise Config model instance.
        """
        self.inputs_get = []
        self.inputs_conf = []
        self.inputs_set = None
        self.inputs_update = None
        self.process_list = None
        self.feeds_get = []
        self.feeds_conf = []
        self.feeds_set = None
        self.feeds_update = None
        self.conf_process_list = None

    def add_inputs_get_list(self, data: list) -> bool:
        """Add inputs list got on server."""
        result = False
        if Ut.is_list(data, not_null=True):
            self.inputs_get = self.inputs_get + data
            result = True
        return result

    def add_inputs_conf_list(self, data: list) -> bool:
        """Add inputs got list"""
        result = False
        if Ut.is_list(data, not_null=True):
            self.inputs_conf = self.inputs_conf + data
            result = True
        return result

    def has_inputs_to_set(self) -> bool:
        """Add inputs got list"""
        return Ut.is_list(self.inputs_set, not_null=True)

    def add_inputs_to_set(self) -> bool:
        """Add inputs got list"""
        result = False
        if Ut.is_list(self.inputs_conf, not_null=True):
            if not Ut.is_list(self.inputs_get, not_null=True):
                self.inputs_set = self.inputs_conf
            elif len(self.inputs_conf) != len(self.inputs_get):
                self.inputs_set = list(
                    set(self.inputs_conf) - set(self.inputs_get)
                )
            result = True
        return result

    def init_inputs_update(self):
        """Add inputs got list"""
        if not Ut.is_dict(self.inputs_update):
            self.inputs_update = dict()

    def init_inputs_update_key(self, key: str):
        """Add inputs got list"""
        self.init_inputs_update()
        if Ut.is_str(key, not_null=True) \
                and not Ut.is_dict(self.inputs_update.get(key)):
            self.inputs_update[key] = dict()

    def has_inputs_to_update(self) -> bool:
        """Add inputs got list"""
        return Ut.is_dict(self.inputs_update, not_null=True)

    def add_inputs_update_item(self,
                               input_name: str,
                               input_id: int,
                               key: str,
                               value: any
                               ) -> bool:
        """Add inputs data to update."""
        result = False
        self.init_inputs_update_key(input_name)
        if Ut.is_str(input_name, not_null=True)\
                and Ut.is_int(input_id, positive=True)\
                and Ut.is_str(key, not_null=True):
            self.inputs_update[input_name].update({
                'id': input_id,
                key: value
            })
            result = True
        return result

    def add_feeds_get_list(self, data: list) -> bool:
        """Add feeds list got on server."""
        result = False
        if Ut.is_list(data, not_null=True):
            self.feeds_get = self.feeds_get + data
            result = True
        return result

    def add_feeds_conf_list(self, data: list) -> bool:
        """Add inputs got list"""
        result = False
        if Ut.is_list(data, not_null=True):
            self.feeds_conf = self.feeds_conf + data
            result = True
        return result

    def init_feeds_set(self):
        """Add inputs got list"""
        if not Ut.is_dict(self.feeds_set):
            self.feeds_set = dict()

    def init_feeds_set_key(self, key: str):
        """Add inputs got list"""
        self.init_feeds_set()
        if Ut.is_str(key, not_null=True) \
                and not Ut.is_list(self.feeds_set.get(key)):
            self.feeds_set[key] = []

    def has_feeds_to_set(self) -> bool:
        """Add inputs got list"""
        return Ut.is_dict(self.feeds_set, not_null=True)

    def has_feed_key_to_set(self, key: str):
        """Add inputs got list"""
        return self.has_feeds_to_set()\
            and Ut.is_str(key, not_null=True)\
            and self.feeds_set.get(key)

    def add_feeds_to_set(self,
                         input_name: str,
                         feeds_conf: list,
                         feeds_get: list
                         ) -> bool:
        """Add inputs got list"""
        result = False
        if Ut.is_list(feeds_conf, not_null=True)\
                and Ut.is_str(input_name, not_null=True):
            if not Ut.is_list(feeds_get, not_null=True):
                self.init_feeds_set_key(input_name)
                self.feeds_set[input_name] = feeds_conf
            elif len(feeds_conf) != len(feeds_get):
                self.init_feeds_set_key(input_name)
                self.feeds_set[input_name] = list(
                    set(feeds_conf) - set(feeds_get)
                )
            result = True
        return result

    def init_feeds_update(self):
        """Add feeds got list"""
        if not Ut.is_dict(self.feeds_update):
            self.feeds_update = dict()

    def init_feeds_update_key(self, key: str):
        """Add feeds got list"""
        self.init_feeds_update()
        if Ut.is_str(key, not_null=True) \
                and not Ut.is_dict(self.feeds_update.get(key)):
            self.feeds_update[key] = dict()

    def has_feeds_to_update(self) -> bool:
        """Test if he has feeds to update."""
        return Ut.is_dict(
            self.feeds_update,
            not_null=True
        )

    def add_feeds_update_item(self,
                              input_name: str,
                              feed_id: int,
                              key: str,
                              value: str
                              ):
        """Add feeds got list"""
        self.init_feeds_update_key(input_name)
        if Ut.is_str(input_name, not_null=True)\
                and Ut.is_int(feed_id, positive=True)\
                and Ut.is_str(key, not_null=True)\
                and Ut.is_str(value):
            self.feeds_update[input_name].update({
                'id': feed_id,
                key: value
            })

    def init_conf_process_list(self):
        """Add feeds got list"""
        if not Ut.is_dict(self.conf_process_list):
            self.conf_process_list = dict()

    def init_conf_process_list_key(self, key: str):
        """Add feeds got list"""
        self.init_conf_process_list()
        if Ut.is_str(key, not_null=True) \
                and not Ut.is_dict(self.conf_process_list.get(key)):
            self.conf_process_list[key] = []

    def set_conf_process_list_item(self, input_name: str, process_list: list):
        """Add feeds got list"""
        if Ut.is_str(input_name, not_null=True)\
                and Ut.is_list(process_list, not_null=True):
            self.init_conf_process_list_key(input_name)
            self.conf_process_list[input_name] = process_list

    def get_conf_process_list_key(self, input_name: str):
        """Add feeds got list"""
        result = None
        if Ut.is_str(input_name, not_null=True)\
                and Ut.is_dict(self.conf_process_list):
            result = self.conf_process_list.get(input_name)
        return result
