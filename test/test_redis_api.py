"""Test RedisApi module"""
import time
from redis.client import Pipeline
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.exceptions import RedisConnectionException, RedisVeError
from vemonitor_m8.workers.redis.redis_api import RedisCli
from vemonitor_m8.workers.redis.redis_api import RedisBase
from vemonitor_m8.workers.redis.redis_api import RedisApi


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

        def init_redis_cli(self):
            """Init RedisCli"""
            self.obj = RedisCli(
                host=self.host,
                port=self.port,
                db=self.db
            )

        def init_redis_base(self):
            """Init RedisBase"""
            self.obj = RedisBase(
                credentials={
                    "host": self.host,
                    "port": self.port,
                    "db": self.db
                }
            )

        def init_redis_api(self):
            """Init RedisApi"""
            self.obj = RedisApi(
                credentials={
                    "host": self.host,
                    "port": self.port,
                    "db": self.db
                }
            )

        def add_hmap_test(self):
            """Init RedisApi"""
            assert self.obj.flush() is True
            nb = self.obj.cli.hset(
                name='data_test',
                key='key_test_0',
                value='a'
            )
            assert nb == 1

            nb = self.obj.cli.hset(
                name='data_test',
                key='key_test_1',
                value='b'
            )
            assert nb == 1

            nb = self.obj.cli.hset(
                name='data_test',
                key='key_test_2',
                value='c'
            )
            assert nb == 1

    return HelperManager()


class TestRedisCli:
    """Test RedisCli module"""

    def test_connect_to_redis(self, helper_manager):
        """Test connect_to_redis method"""
        helper_manager.init_redis_cli()

        assert helper_manager.obj.is_ready()
        assert helper_manager.obj.is_connected()

        helper_manager.obj.connect_to_redis(
            credentials={
                "host": helper_manager.host,
                "port": helper_manager.port,
                "db": helper_manager.db
            }
        )

        assert helper_manager.obj.is_ready()
        assert helper_manager.obj.is_connected()

        with pytest.raises(RedisConnectionException):
            helper_manager.obj.connect_to_redis(
                credentials={
                    "host": "127.9.9.9",
                    "port": helper_manager.port,
                }
            )

        with pytest.raises(RedisConnectionException):
            helper_manager.obj.connect_to_redis(
                credentials={
                    "host": "127.9.9.9",
                    "port": helper_manager.port,
                    "db": "not_int",
                    "bad_prm": "bad_value"
                }
            )

    def test_set_pipeline(self, helper_manager):
        """Test set_pipeline method"""
        helper_manager.init_redis_cli()
        assert helper_manager.obj.pipe is None

        helper_manager.obj.set_pipeline()
        assert isinstance(helper_manager.obj.pipe, Pipeline)

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.set_pipeline()

    def test_flush(self, helper_manager):
        """Test _flush method"""
        helper_manager.init_redis_cli()
        # Add Hmap keys
        helper_manager.add_hmap_test()

        data = helper_manager.obj.cli.hget(
            name='data_test',
            key='key_test_0'
        )
        assert data == 'a'

        assert helper_manager.obj.flush() is True
        data = helper_manager.obj.cli.hget(
            name='data_test',
            key='key_test'
        )
        assert data is None

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.flush()

    def test_is_redis_credentials(self, helper_manager):
        """Test is_redis_credentials method"""
        helper_manager.init_redis_cli()
        credentials = {
            "host": "127.9.9.256",
            "port": 6379
        }
        assert helper_manager.obj.is_redis_credentials(
            credentials
        ) is False

        credentials = {
            "host": "127.9.9.255",
            "port": 65536
        }
        assert helper_manager.obj.is_redis_credentials(
            credentials
        ) is False

        credentials = {
            "host": "127.9.9.255",
            "port": -1
        }
        assert helper_manager.obj.is_redis_credentials(
            credentials
        ) is False

        credentials = {
            "host": "127.9.9.9",
            "port": 6379,
            "db": "not_int",
            "bad_prm": "bad_value"
        }
        assert helper_manager.obj.is_redis_credentials(
            credentials
        ) is True

        credentials = {
            "host": "127.9.9.255",
            "port": 6379
        }
        assert helper_manager.obj.is_redis_credentials(
            credentials
        ) is True

    def test_is_redis_client_connected(self, helper_manager):
        """Test is_redis_client_connected method"""
        helper_manager.init_redis_cli()
        assert RedisCli.is_redis_client_connected(
            helper_manager.obj.cli
        ) is True

        assert RedisCli.is_redis_client_connected(
            helper_manager.obj
        ) is False


class TestRedisBase:
    """Test RedisBase module"""

    def test_get_key_type(self, helper_manager):
        """Test get_key_type method"""
        helper_manager.init_redis_base()
        # Add Hmap keys
        helper_manager.add_hmap_test()

        data = helper_manager.obj.cli.hget(
            name='data_test',
            key='key_test_0'
        )
        assert data == 'a'

        assert helper_manager.obj.get_key_type(
            key='data_test'
        ) == 'hash'

        with pytest.raises(RedisVeError):
            helper_manager.obj.get_key_type(
                key=['data_test']
            )

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_key_type(
                key='data_test'
            )

    def test_save_redis_data_on_disk(self, helper_manager):
        """Test save_redis_data_on_disk method"""
        helper_manager.init_redis_base()
        # Add Hmap keys
        helper_manager.add_hmap_test()

        info = helper_manager.obj.get_redis_info_usage()
        last_saved_time = info.get('rdb_last_save_time')
        now = Ut.get_int(time.time())
        assert now > last_saved_time

        helper_manager.obj.save_redis_data_on_disk()

        time.sleep(5)
        info = helper_manager.obj.get_redis_info_usage()
        last_saved_time = info.get('rdb_last_save_time')
        assert now <= last_saved_time

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.save_redis_data_on_disk()

    def test_get_redis_info_usage(self, helper_manager):
        """Test get_redis_info_usage method"""
        helper_manager.init_redis_base()

        info = helper_manager.obj.get_redis_info_usage(
            section='server'
        )
        assert Ut.is_dict(info, not_null=True)

        info = helper_manager.obj.get_redis_info_usage(
            keys=['redis_version', 'arch_bits']
        )
        assert Ut.is_dict(info, eq=2)

        nb_total_keys = len(helper_manager.obj.get_info_default_keys())
        info = helper_manager.obj.get_redis_info_usage()
        assert Ut.is_dict(info, eq=nb_total_keys-1)

        info = helper_manager.obj.get_redis_info_usage(
            full=True
        )
        assert Ut.is_dict(info, not_null=True)

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_redis_info_usage()


class TestRedisApi:
    """Test RedisApi module"""

    def test_get_hmap_len(self, helper_manager):
        """Test get_hmap_len method"""
        helper_manager.init_redis_api()
        # Add Hmap keys
        helper_manager.add_hmap_test()

        nb = helper_manager.obj.get_hmap_len(
            key='data_test'
        )
        assert nb == 3

        with pytest.raises(RedisVeError):
            nb = helper_manager.obj.get_hmap_len(
                key=['data_test']
            )

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_hmap_len(
                key='data_test'
            )

    def test_is_hmap_key(self, helper_manager):
        """Test is_hmap_key method"""
        helper_manager.init_redis_api()
        # Add Hmap keys
        helper_manager.add_hmap_test()

        assert helper_manager.obj.is_hmap_key(
            name='data_test',
            key='key_test_0'
        ) is True

        with pytest.raises(RedisVeError):
            helper_manager.obj.is_hmap_key(
                name='data_test',
                key=['data_test']
            )

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.is_hmap_key(
                name='data_test',
                key='key_test_0'
            )

    def test_get_hmap_keys(self, helper_manager):
        """Test get_hmap_keys method"""
        helper_manager.init_redis_api()
        # Add Hmap keys
        helper_manager.add_hmap_test()

        data = helper_manager.obj.get_hmap_keys(
            name='data_test'
        )
        assert data == ['key_test_0', 'key_test_1', 'key_test_2']

        with pytest.raises(RedisVeError):
            helper_manager.obj.get_hmap_keys(
                name=['data_test']
            )

        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_hmap_keys(
                name='data_test'
            )

    def test_del_hmap_keys(self, helper_manager):
        """Test del_hmap_keys method"""
        helper_manager.init_redis_api()

        # Add Hmap keys
        helper_manager.add_hmap_test()

        # Delete 2 hmap keys
        nb = helper_manager.obj.del_hmap_keys(
            name='data_test',
            keys=['key_test_0', 'key_test_1']
        )
        assert nb == 2

        # Control 2/3 keys are deleted
        data = helper_manager.obj.get_hmap_keys(
            name='data_test'
        )
        assert data == ['key_test_2']

        # test bad name type
        with pytest.raises(RedisVeError):
            nb = helper_manager.obj.del_hmap_keys(
                name=['data_test'],
                keys=['key_test_0', 'key_test_1']
            )

        # test loose redis conection
        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.del_hmap_keys(
                name='data_test',
                keys=['key_test_0', 'key_test_1']
            )

    def test_get_hmap_data(self, helper_manager):
        """Test get_hmap_data method"""
        helper_manager.init_redis_api()
        # Add Hmap keys
        helper_manager.add_hmap_test()

        data = helper_manager.obj.get_hmap_data(
            name='data_test'
        )
        assert data == {
            'key_test_0': 'a',
            'key_test_1': 'b',
            'key_test_2': 'c'
        }

        data = helper_manager.obj.get_hmap_data(
            name='data_test',
            keys=['key_test_0', 'key_test_1']
        )

        assert data == ['a', 'b']

        data = helper_manager.obj.get_hmap_data(
            name='data_test',
            keys='key_test_0'
        )

        assert data == 'a'

        # test bad name type
        with pytest.raises(RedisVeError):
            helper_manager.obj.get_hmap_data(
                name=['data_test']
            )

        # test loose redis conection
        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_hmap_data(
                name='data_test'
            )

    def test_set_hmap_data(self, helper_manager):
        """Test set_hmap_data method"""
        helper_manager.init_redis_api()
        # Delete db
        assert helper_manager.obj.flush() is True

        # Test set hmap with unique str value
        nb = helper_manager.obj.set_hmap_data(
            name='data_test',
            key='key_test_0',
            values='a'
        )
        assert nb == 1
        # verrify data added
        data = helper_manager.obj.get_hmap_data(
            name='data_test'
        )
        assert data == {
            'key_test_0': 'a'
        }

        # Test set hmap with dict values
        nb = helper_manager.obj.set_hmap_data(
            name='data_test',
            values={
                'key_test_1': 'b',
                'key_test_2': 'c'
            }
        )
        assert nb == 2
        # verrify data added
        data = helper_manager.obj.get_hmap_data(
            name='data_test'
        )
        assert data == {
            'key_test_0': 'a',
            'key_test_1': 'b',
            'key_test_2': 'c'
        }

        # test bad name type
        with pytest.raises(RedisVeError):
            nb = helper_manager.obj.set_hmap_data(
                name=['data_test'],
                key='key_test_0',
                values='a'
            )

        # test loose redis conection
        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.set_hmap_data(
                name='data_test',
                key='key_test_0',
                values='a'
            )

    def test_add_set_members(self, helper_manager):
        """Test add_set_members method"""
        helper_manager.init_redis_api()
        # Delete db
        assert helper_manager.obj.flush() is True

        # Test set hmap with unique str value
        nb = helper_manager.obj.add_set_members(
            name='data_test',
            values=['a']
        )
        assert nb == 1

        nb = helper_manager.obj.add_set_members(
            name='data_test',
            values=['b', 'c']
        )
        assert nb == 2

        # verrify data added
        data = helper_manager.obj.get_set_members(
            name='data_test'
        )
        assert data == {'c', 'b', 'a'}

        # test bad name type
        with pytest.raises(RedisVeError):
            nb = helper_manager.obj.add_set_members(
                name=['data_test'],
                values=['d']
            )

        # test loose redis conection
        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.add_set_members(
                name='data_test',
                values=['d']
            )

    def test_remove_set_members(self, helper_manager):
        """Test remove_set_members method"""
        helper_manager.init_redis_api()
        # Delete db
        assert helper_manager.obj.flush() is True

        # Test set hmap with unique str value
        nb = helper_manager.obj.add_set_members(
            name='data_test',
            values=['a', 'b', 'c']
        )
        assert nb == 3

        # verrify data added
        data = helper_manager.obj.get_set_members(
            name='data_test'
        )
        assert data == {'c', 'b', 'a'}

        # remove data
        nb = helper_manager.obj.remove_set_members(
            name='data_test',
            values=['a', 'b']
        )
        assert nb == 2

        # verrify data removed
        data = helper_manager.obj.get_set_members(
            name='data_test'
        )
        assert data == {'c'}

        # remove data
        nb = helper_manager.obj.remove_set_members(
            name='data_test',
            values='c'
        )
        assert nb == 1

        # test bad name type
        with pytest.raises(RedisVeError):
            nb = helper_manager.obj.remove_set_members(
                name=['data_test'],
                values=['d']
            )

        # test loose redis conection
        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.remove_set_members(
                name='data_test',
                values=['d']
            )

    def test_get_set_members(self, helper_manager):
        """Test get_set_members method"""
        helper_manager.init_redis_api()
        # Delete db
        assert helper_manager.obj.flush() is True

        # Test set hmap with unique str value
        nb = helper_manager.obj.add_set_members(
            name='data_test',
            values=['a', 'b', 'c']
        )
        assert nb == 3

        # verrify data added
        data = helper_manager.obj.get_set_members(
            name='data_test'
        )
        assert data == {'c', 'b', 'a'}

        # test bad name type
        with pytest.raises(RedisVeError):
            nb = helper_manager.obj.get_set_members(
                name=['data_test']
            )

        # test loose redis conection
        helper_manager.obj.cli = None
        with pytest.raises(RedisConnectionException):
            helper_manager.obj.get_set_members(
                name='data_test'
            )
