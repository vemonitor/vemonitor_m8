"""Test workers model module."""
import pytest
from vemonitor_m8.core.exceptions import SettingInvalidException
from vemonitor_m8.workers.redis.redis_app import RedisApp
from vemonitor_m8.workers.redis.redis_worker import RedisInputWorker
from vemonitor_m8.workers.redis.redis_worker import RedisOutputWorker


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = None
            self.conf = None
            self.credentials = {
                "host": '127.0.0.1',
                "port": 6379,
                "db": 2
            }

        def init_input_worker(self):
            """Init RedisInputWorker class"""
            self.conf = {
                "item": {
                    "name": "RedisInputWorkerTest",
                    "time_interval": 1,
                    "cache_interval": 1,
                    "columns": {
                        "bmv700": ["V", "I", "P"]
                    },
                    "ref_cols": [
                            ['bat_voltage', 'V'],
                            ['bat_current', 'I'],
                            ['bat_power', 'P']
                    ]
                },
                "worker_key": "RedisTestWorker",
                "enum_key": 2,
                "connector": self.credentials
            }
            self.obj = RedisInputWorker(
                conf=self.conf
            )

        def init_output_worker(self):
            """Init Workers class"""
            self.conf = {
                "item": {
                    "name": "RedisOutputWorkerTest",
                    "time_interval": 1,
                    "cache_interval": 1,
                    "columns": {
                        "bmv700": ["V", "I", "P"]
                    },
                    "ref_cols": [
                            ['bat_voltage', 'V'],
                            ['bat_current', 'I'],
                            ['bat_power', 'P']
                    ]
                },
                "worker_key": "RedisTestWorker",
                "enum_key": 2,
                "connector": self.credentials
            }
            self.obj = RedisOutputWorker(
                conf=self.conf
            )

    return HelperManager()


class TestRedisInputWorker:
    """Test RedisInputWorker model class."""
    def test_is_ready(self, helper_manager):
        """Test is_ready method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.is_ready() is True

    def test_has_info(self, helper_manager):
        """Test has_info method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_info() is True

    def test_has_name(self, helper_manager):
        """Test is_ready method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_name() is True

    def test_has_worker_key(self, helper_manager):
        """Test has_worker_key method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_worker_key() is True

    def test_get_worker_key(self, helper_manager):
        """Test get_worker_key method"""
        helper_manager.init_input_worker()
        result = helper_manager.obj.get_worker_key()
        assert result == "RedisTestWorker"

    def test_has_enum_key(self, helper_manager):
        """Test has_enum_key method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_enum_key() is True

    def test_get_enum_key(self, helper_manager):
        """Test get_enum_key method"""
        helper_manager.init_input_worker()
        result = helper_manager.obj.get_enum_key()
        assert result == 2

    def test_has_time_interval(self, helper_manager):
        """Test has_enum_key method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_time_interval() is True

    def test_has_ref_cols(self, helper_manager):
        """Test has_enum_key method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_ref_cols() is True

    def test_has_worker_conf(self, helper_manager):
        """Test has_enum_key method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_worker_conf() is True

    def test_has_columns(self, helper_manager):
        """Test has_enum_key method"""
        helper_manager.init_input_worker()

        assert helper_manager.obj.has_columns() is True

    def test_set_columns(self, helper_manager):
        """Test has_enum_key method"""
        helper_manager.init_input_worker()
        result = helper_manager.obj.set_columns(
            value={
                    "bmv700": ["V", "I", "P"]
                }
        )
        assert result is True
        result = helper_manager.obj.set_columns(
            value=["V", "I", "P"]
        )
        assert result is False

    def test_set_worker_status(self, helper_manager):
        """Test set_worker_status method"""
        helper_manager.init_input_worker()
        result = helper_manager.obj.set_worker_status()
        assert result is True

    def test_set_worker(self, helper_manager):
        """Test set_worker method"""
        helper_manager.init_input_worker()
        result = helper_manager.obj.set_worker(
            worker=helper_manager.credentials
        )
        assert result is True

        redis_app = RedisApp(
            credentials=helper_manager.credentials
        )
        result = helper_manager.obj.set_worker(
            worker=redis_app
        )
        assert result is True

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_worker(
                worker=None
            )

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_worker(
                worker={'a': 1}
            )

    def test_set_conf(self, helper_manager):
        """Test set_conf method"""
        helper_manager.init_input_worker()
        result = helper_manager.obj.set_conf(
            conf=helper_manager.conf
        )
        assert result is True

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_conf(
                conf={'a': 1}
            )


class TestRedisOutputWorker:
    """Test RedisOutputWorker model class."""
    def test_is_ready(self, helper_manager):
        """Test is_ready method"""
        helper_manager.init_output_worker()

        assert helper_manager.obj.is_ready()

    def test_has_columns(self, helper_manager):
        """Test has_columns method"""
        helper_manager.init_output_worker()

        assert helper_manager.obj.has_columns() is True

    def test_set_last_saved_time(self, helper_manager):
        """Test set_last_saved_time method"""
        helper_manager.init_output_worker()

        assert helper_manager.obj.has_last_saved_time() is False
        result = helper_manager.obj.set_last_saved_time(
            value=1722013447
        )
        assert result is True
        assert helper_manager.obj.has_last_saved_time() is True
        assert helper_manager.obj.get_last_saved_time() == 1722013447

        result = helper_manager.obj.set_last_saved_time(
            value=-1
        )
        assert result is False

    def test_set_cache_interval(self, helper_manager):
        """Test set_cache_interval method"""
        helper_manager.init_output_worker()

        assert helper_manager.obj.has_time_interval() is True
        assert helper_manager.obj.get_cache_interval() == 1
        result = helper_manager.obj.set_cache_interval(
            value=5
        )
        assert result is True
        assert helper_manager.obj.has_time_interval() is True
        assert helper_manager.obj.get_cache_interval() == 5

    def test_set_min_req_interval(self, helper_manager):
        """Test set_min_req_interval method"""
        helper_manager.init_output_worker()

        result = helper_manager.obj.set_min_req_interval(
            value=2
        )
        assert result is True
        assert helper_manager.obj.has_min_req_interval() is True
        assert helper_manager.obj.get_min_req_interval() == 2

    def test_respect_req_interval(self, helper_manager):
        """Test respect_req_interval method"""
        helper_manager.init_output_worker()

        result = helper_manager.obj.set_min_req_interval(
            value=1
        )
        assert result is True
        assert helper_manager.obj.has_min_req_interval() is True
        assert helper_manager.obj.get_min_req_interval() == 1
        helper_manager.obj.update_req_time()
        helper_manager.obj.respect_req_interval()

    def test_set_worker_status(self, helper_manager):
        """Test set_worker_status method"""
        helper_manager.init_output_worker()
        result = helper_manager.obj.set_worker_status()
        assert result is True

    def test_set_worker(self, helper_manager):
        """Test set_worker method"""
        helper_manager.init_output_worker()
        result = helper_manager.obj.set_worker(
            worker=helper_manager.credentials
        )
        assert result is True

        redis_app = RedisApp(
            credentials=helper_manager.credentials
        )
        result = helper_manager.obj.set_worker(
            worker=redis_app
        )
        assert result is True

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_worker(
                worker=None
            )

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_worker(
                worker={'a': 1}
            )

    def test_set_conf(self, helper_manager):
        """Test set_conf method"""
        helper_manager.init_output_worker()
        result = helper_manager.obj.set_conf(
            conf=helper_manager.conf
        )
        assert result is True

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_conf(
                conf={'a': 1}
            )
