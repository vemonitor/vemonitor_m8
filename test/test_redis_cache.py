"""Test redis_cache module"""
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.exceptions import RedisConnectionException, RedisVeError
from vemonitor_m8.workers.redis.redis_app import RedisApp
from vemonitor_m8.workers.redis.redis_cache import RedisConnector
from vemonitor_m8.workers.redis.redis_cache import RedisCache


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None
            self.host = '127.0.0.1'
            self.port = 6379
            self.db = 2

        def init_redis_connector(self):
            """Init RedisCli"""
            self.obj = RedisConnector(
                connector={
                    "host": self.host,
                    "port": self.port,
                    "db": self.db
                }
            )

        def init_redis_cache(self):
            """Init RedisCache"""
            self.obj = RedisCache(
                max_rows=10,
                connector={
                    "host": self.host,
                    "port": self.port,
                    "db": self.db
                },
                reset_at_start=True
            )

        def init_nodes_test(self):
            """Init RedisCache"""
            # reset data cache
            self.obj.reset_data_cache()
            # get all nodes list
            data = self.obj.get_cache_nodes_keys_list()
            assert data == []
            # register nodes
            assert self.obj.register_node('pytest_1') is True
            assert self.obj.register_node('pytest_2') is True
            assert self.obj.register_node('pytest_3') is True

        def init_data_test(self):
            """Init data to test"""
            # init nodes
            self.init_nodes_test()

            assert self.obj.add_data_cache(
                time_key=1722013447,
                node='pytest_1',
                data={
                    'V': 25.5,
                    'I': 3.12
                }
            ) is True

            assert self.obj.add_data_cache(
                time_key=1722013448,
                node='pytest_1',
                data={
                    'V': 26.8,
                    'I': 1.52
                }
            ) is True

            assert self.obj.add_data_cache(
                time_key=1722013449,
                node='pytest_1',
                data={
                    'V': 26.2,
                    'I': 1.55
                }
            ) is True

        def add_more_data_test(self):
            """Init data to test"""
            now = 1722013440

            for i in range(50):
                now += 1
                assert self.obj.add_data_cache(
                    time_key=now,
                    node="pytest_1",
                    data={
                        'V': 26.8 + i + 1,
                        'I': 1.52 + i + 1
                    }
                ) is True

                if now % 2 == 0:
                    assert self.obj.add_data_cache(
                        time_key=now,
                        node="pytest_2",
                        data={
                            'V': 26.8 + i + 1,
                            'I': 1.52 + i + 1
                        }
                    ) is True

                if now % 5 == 0:
                    assert self.obj.add_data_cache(
                        time_key=now,
                        node="pytest_3",
                        data={
                            'V': 26.8 + i + 1,
                            'I': 1.52 + i + 1
                        }
                    ) is True

    return HelperManager()


class TestRedisConnector:
    """Test RedisConnector class"""

    def test_set_redis_app(self, helper_manager):
        """Test set_redis_app method"""
        helper_manager.init_redis_connector()
        # set redis app with dict data
        assert helper_manager.obj.set_redis_app(
            connector={
                "host": helper_manager.host,
                "port": helper_manager.port,
                "db": helper_manager.db,
                "active": True
            }
        ) is True

        # set redis app with RedisApp object
        connector = RedisApp(
            credentials={
                "host": helper_manager.host,
                "port": helper_manager.port,
                "db": helper_manager.db
            }
        )

        assert helper_manager.obj.set_redis_app(
            connector=connector
        ) is True


class TestRedisCache:
    """Test RedisCache class"""

    def test_get_cache_nodes_keys_list(self, helper_manager):
        """Test get_cache_nodes_keys_list method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_nodes_test()

        # get all nodes list
        data = helper_manager.obj.get_cache_nodes_keys_list()
        assert Ut.is_list(data, eq=3)

        # get two first nodes list
        data = helper_manager.obj.get_cache_nodes_keys_list(
            nodes=['pytest_1', 'pytest_2']
        )
        assert Ut.is_list(data, eq=2)
        assert 'ric_pytest_1' in data
        assert 'ric_pytest_2' in data

        # test bad name type
        helper_manager.obj.cache_name = ["inputs_cache"]
        with pytest.raises(RedisVeError):
            helper_manager.obj.get_cache_nodes_keys_list()
        helper_manager.obj.cache_name = "inputs_cache"

        # test loose redis conection
        helper_manager.obj.app.api.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_cache_nodes_keys_list()

    def test_get_cache_keys_by_node(self, helper_manager):
        """Test get_cache_keys_by_node method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_data_test()

        # get cache keys by node
        data = helper_manager.obj.get_cache_keys_by_node(
            formatted_node='ric_pytest_1'
        )
        assert Ut.is_list(data, eq=3)
        assert data == [1722013447, 1722013448, 1722013449]

        # get cache keys by node
        data = helper_manager.obj.get_cache_keys_by_node(
            formatted_node='ric_pytest_1',
            from_time=1722013448
        )
        assert Ut.is_list(data, eq=2)
        assert data == [1722013448, 1722013449]

        # test bad name type
        helper_manager.obj.cache_name = ["inputs_cache"]
        with pytest.raises(RedisVeError):
            helper_manager.obj.get_cache_nodes_keys_list()
        helper_manager.obj.cache_name = "inputs_cache"

        # test loose redis conection
        helper_manager.obj.app.api.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_cache_nodes_keys_list()

    def test_get_interval_keys(self, helper_manager):
        """Test get_interval_keys method"""
        keys = [1722013465, 1722013470]
        assert RedisCache.get_interval_keys(
            keys
        ) == 5

        keys = [1722013464, 1722013466, 1722013468, 1722013470]
        assert RedisCache.get_interval_keys(
            keys
        ) == 2

        keys = [1722013466, 1722013467, 1722013468, 1722013469, 1722013470]
        assert RedisCache.get_interval_keys(
            keys
        ) == 1

        keys = [1722013466, 1722013468, 1722013469, 1722013470, 1722013475]
        assert RedisCache.get_interval_keys(
            keys
        ) == 1

    def test_get_cache_keys_structure(self, helper_manager):
        """Test get_cache_keys_structure method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_nodes_test()

        # Set max data cache to 10 items
        helper_manager.obj.set_max_rows(10)
        # add more cache data
        helper_manager.add_more_data_test()

        result = helper_manager.obj.get_cache_keys_structure(
            node_keys=['ric_pytest_3', 'ric_pytest_1', 'ric_pytest_2'],
            from_time=1722013464,
            nb_items=2
        )
        assert result == {'ric_pytest_3': [1722013465, 1722013470]}

        result = helper_manager.obj.get_cache_keys_structure(
            node_keys=['ric_pytest_3', 'ric_pytest_1', 'ric_pytest_2'],
            from_time=1722013460,
            nb_items=5
        )
        assert result == {
            'ric_pytest_3': [1722013460, 1722013465, 1722013470],
            'ric_pytest_2': [1722013472, 1722013474]
        }

    def test_enum_cache_keys(self, helper_manager):
        """Test enum_cache_keys method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_data_test()

        for node, keys in helper_manager.obj.enum_cache_keys():

            if node == 'ric_pytest_1':
                assert keys == [1722013447, 1722013448, 1722013449]
            else:
                assert keys is None

        for node, keys in helper_manager.obj.enum_cache_keys(
            nodes=['ric_pytest_1', 'ric_pytest_2']
        ):

            if node == 'ric_pytest_1':
                assert keys == [1722013447, 1722013448, 1722013449]
            elif node == 'ric_pytest_2':
                assert keys is None
            else:
                assert False

        for node, keys in helper_manager.obj.enum_cache_keys(
            nodes=['ric_pytest_1', 'ric_pytest_2'],
            from_time=1722013448
        ):

            if node == 'ric_pytest_1':
                assert keys == [1722013448, 1722013449]
            elif node == 'ric_pytest_2':
                assert keys is None
            else:
                assert False

    def test_reset_data_cache(self, helper_manager):
        """Test reset_data_cache method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_data_test()

        deleted = helper_manager.obj.reset_data_cache()
        assert deleted == [3, 3]

    def test_add_data_cache(self, helper_manager):
        """Test add_data_cache method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_nodes_test()

        # Set max data cache to 10 items
        helper_manager.obj.set_max_rows(10)
        # add more cache data
        helper_manager.add_more_data_test()

        data_ric_pytest_1 = helper_manager.obj.app.api.get_hmap_data(
            "ric_pytest_1"
        )
        data_ric_pytest_2 = helper_manager.obj.app.api.get_hmap_data(
            "ric_pytest_2"
        )
        data_ric_pytest_3 = helper_manager.obj.app.api.get_hmap_data(
            "ric_pytest_3"
        )

        assert len(data_ric_pytest_1) == 10
        assert len(data_ric_pytest_2) == 10
        assert len(data_ric_pytest_3) == 10

    def test_enum_node_data_cache_interval(self, helper_manager):
        """Test enum_node_data_cache_interval method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_data_test()

        for key, values in helper_manager.obj.enum_node_data_cache_interval(
            formatted_node='ric_pytest_1',
            keys=[1722013447, 1722013448]
        ):
            if key == 1722013447:
                assert values == {'V': 25.5, 'I': 3.12}
            elif key == 1722013448:
                assert values == {'V': 26.8, 'I': 1.52}
            else:
                assert False

    def test_get_data_from_redis(self, helper_manager):
        """Test get_data_from_redis method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_nodes_test()

        # Set max data cache to 5 items
        helper_manager.obj.set_max_rows(10)
        # add more cache data
        helper_manager.add_more_data_test()

        # get all items for all nodes
        result, max_time = helper_manager.obj.get_data_from_redis()
        keys = list(result.keys())
        keys.sort()
        assert keys == [
            1722013445, 1722013450, 1722013455,
            1722013460, 1722013465, 1722013470,
            1722013472, 1722013474, 1722013475,
            1722013476, 1722013478, 1722013480,
            1722013481, 1722013482, 1722013483,
            1722013484, 1722013485, 1722013486,
            1722013487, 1722013488, 1722013489,
            1722013490
        ] and len(keys) == 22
        assert max_time == 1722013490

        # get two items from every node who start at 1722013464
        result, max_time = helper_manager.obj.get_data_from_redis(
            from_time=1722013464,
            nb_items=2
        )
        keys = list(result.keys())
        keys.sort()
        assert keys == [
            1722013465,
            1722013470
        ]

        assert max_time == 1722013470

        # Get two items of 'V' key from pytest_1 node
        # who start at 1722013464
        result, max_time = helper_manager.obj.get_data_from_redis(
            from_time=1722013464,
            nb_items=2,
            structure={
                'pytest_1': ['V']
            }
        )
        keys = list(result.keys())
        keys.sort()
        assert keys == [1722013481, 1722013482]

        assert max_time == 1722013482

    def test_get_data_from_cache(self, helper_manager):
        """Test get_data_from_cache method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_nodes_test()

        # Set max data cache to 5 items
        helper_manager.obj.set_max_rows(10)
        # add more cache data
        helper_manager.add_more_data_test()

        # get all items for all nodes
        result, last_time, max_time = helper_manager.obj.get_data_from_cache()
        keys = list(result.keys())
        keys.sort()
        assert keys == [
            1722013445, 1722013450, 1722013455,
            1722013460, 1722013465, 1722013470,
            1722013472, 1722013474, 1722013475,
            1722013476, 1722013478, 1722013480,
            1722013481, 1722013482, 1722013483,
            1722013484, 1722013485, 1722013486,
            1722013487, 1722013488, 1722013489,
            1722013490
        ] and len(keys) == 22
        assert max_time == 1722013490
        assert last_time == 1722013491

        # get fist for time  keys from data cache
        result, last_time, max_time = helper_manager.obj.get_data_from_cache(
           nb_items=4
        )
        assert result == {
            1722013445: {
                'pytest_3': {'V': 31.8, 'I': 6.52}
            },
            1722013450: {
                'pytest_3': {'V': 36.8, 'I': 11.52}
            },
            1722013455: {
                'pytest_3': {'V': 41.8, 'I': 16.52}
            },
            1722013460: {
                'pytest_3': {'V': 46.8, 'I': 21.52}
            }
        }
        assert max_time == 1722013460
        assert last_time == 1722013461

        # get all items from time 1722013488
        result, last_time, max_time = helper_manager.obj.get_data_from_cache(
           from_time=1722013488
        )
        assert result == {
            1722013488: {
                'pytest_1': {'V': 74.8, 'I': 49.52},
                'pytest_2': {'V': 74.8, 'I': 49.52}
            },
            1722013489: {'pytest_1': {'V': 75.8, 'I': 50.52}},
            1722013490: {
                'pytest_1': {'V': 76.8, 'I': 51.52},
                'pytest_2': {'V': 76.8, 'I': 51.52},
                'pytest_3': {'V': 76.8, 'I': 51.52}
            }
        }
        assert max_time == 1722013490
        assert last_time == 1722013491

        # get all pytest_1 node data
        result, last_time, max_time = helper_manager.obj.get_data_from_cache(
           structure={'pytest_1': ['V', 'I']}
        )
        assert result == {
            1722013481: {'pytest_1': {'V': 67.8, 'I': 42.52}},
            1722013482: {'pytest_1': {'V': 68.8, 'I': 43.52}},
            1722013483: {'pytest_1': {'V': 69.8, 'I': 44.52}},
            1722013484: {'pytest_1': {'V': 70.8, 'I': 45.52}},
            1722013485: {'pytest_1': {'V': 71.8, 'I': 46.52}},
            1722013486: {'pytest_1': {'V': 72.8, 'I': 47.52}},
            1722013487: {'pytest_1': {'V': 73.8, 'I': 48.52}},
            1722013488: {'pytest_1': {'V': 74.8, 'I': 49.52}},
            1722013489: {'pytest_1': {'V': 75.8, 'I': 50.52}},
            1722013490: {'pytest_1': {'V': 76.8, 'I': 51.52}}
        }
        assert max_time == 1722013490
        assert last_time == 1722013491

        # get four items from every node who start at 1722013460
        result, last_time, max_time = helper_manager.obj.get_data_from_cache(
            structure={'pytest_1': ['V']}
        )

        assert result == {
            1722013481: {'pytest_1': {'V': 67.8}},
            1722013482: {'pytest_1': {'V': 68.8}},
            1722013483: {'pytest_1': {'V': 69.8}},
            1722013484: {'pytest_1': {'V': 70.8}},
            1722013485: {'pytest_1': {'V': 71.8}},
            1722013486: {'pytest_1': {'V': 72.8}},
            1722013487: {'pytest_1': {'V': 73.8}},
            1722013488: {'pytest_1': {'V': 74.8}},
            1722013489: {'pytest_1': {'V': 75.8}},
            1722013490: {'pytest_1': {'V': 76.8}}
        }
        assert max_time == 1722013490
        assert last_time == 1722013491

        # get seven items from every node who start at 1722013460
        result, last_time, max_time = helper_manager.obj.get_data_from_cache(
            from_time=1722013484,
            nb_items=4
        )

        assert result == {
            1722013484: {
                'pytest_1': {'V': 70.8, 'I': 45.52},
                'pytest_2': {'V': 70.8, 'I': 45.52}
            },
            1722013485: {
                'pytest_1': {'V': 71.8, 'I': 46.52},
                'pytest_3': {'V': 71.8, 'I': 46.52}
            },
            1722013486: {
                'pytest_1': {'V': 72.8, 'I': 47.52},
                'pytest_2': {'V': 72.8, 'I': 47.52}
            },
            1722013487: {'pytest_1': {'V': 73.8, 'I': 48.52}}
        }
        assert max_time == 1722013487
        assert last_time == 1722013488

        # Get two items of 'V' key from pytest_1 node
        # who start at 1722013464
        result, last_time, max_time = helper_manager.obj.get_data_from_cache(
            from_time=1722013484,
            nb_items=4,
            structure={
                'pytest_1': ['V']
            }
        )
        assert result == {
            1722013484: {'pytest_1': {'V': 70.8}},
            1722013485: {'pytest_1': {'V': 71.8}},
            1722013486: {'pytest_1': {'V': 72.8}},
            1722013487: {'pytest_1': {'V': 73.8}}
        }
        assert max_time == 1722013487
        assert last_time == 1722013488

    def test_get_time_interval(self, helper_manager):
        """Test get_time_interval method"""
        helper_manager.init_redis_cache()
        # init nodes test
        helper_manager.init_data_test()
