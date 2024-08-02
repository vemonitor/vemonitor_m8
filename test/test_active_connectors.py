"""Test active_connectors helper module."""
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.workers.active_connectors import ActiveConnectors


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.obj = ActiveConnectors()

    return HelperManager()


class TestActiveConnectors:
    """Test ActiveConnectors model class."""

    def test_has_items(self, helper_manager):
        """Test has_items method """
        helper_manager.obj.add_item(
          key=("worker_name", "worker_key"),
          value=("worker_status", "worker_interval")
        )
        assert helper_manager.obj.has_items() is True

    def test_has_item_key(self, helper_manager):
        """Test has_item_key method """
        helper_manager.obj.add_item(
          key=("worker_name", "worker_key"),
          value=("worker_status", "worker_interval")
        )
        assert helper_manager.obj.has_item_key(
            key=("worker_name", "worker_key")
        ) is True

    def test_init_item(self, helper_manager):
        """Test init_item method """
        helper_manager.obj.add_item(
          key=("worker_name", "worker_key"),
          value=("worker_status", "worker_interval")
        )
        helper_manager.obj.init_item(reset=True)
        assert helper_manager.obj.has_items() is False

    def test_add_item(self, helper_manager):
        """Test add_item method """
        result = helper_manager.obj.add_item(
          key=("worker_name", "worker_key"),
          value=("worker_status", "worker_interval")
        )
        assert result is True
        assert helper_manager.obj.has_items() is True
        assert helper_manager.obj.has_item_key(
            key=("worker_name", "worker_key")
        ) is True

        result = helper_manager.obj.add_item(
          key="worker_name",
          value="worker_name"
        )
        assert result is False

    def test_get_item(self, helper_manager):
        """Test get_item method """
        result = helper_manager.obj.add_item(
          key=("worker_name", "worker_key"),
          value=("worker_status", "worker_interval")
        )
        assert result is True
        result = helper_manager.obj.get_item(
          key=("worker_name", "worker_key")
        )

        assert result == ("worker_status", "worker_interval")

    def test_loop_on_items(self, helper_manager):
        """Test loop_on_items method """
        result = helper_manager.obj.add_item(
          key=("worker_name", "worker_key"),
          value=("worker_status", "worker_interval")
        )
        assert result is True
        for key, item in helper_manager.obj.loop_on_items():
            assert key == ("worker_name", "worker_key")
            assert item == ("worker_status", "worker_interval")

    def test_get_items(self, helper_manager):
        """Test get_items method """
        key = ("worker_name", "worker_key")
        item = ("worker_status", "worker_interval")
        result = helper_manager.obj.add_item(
          key=key,
          value=item
        )
        assert result is True
        result = helper_manager.obj.get_items()
        assert Ut.is_dict(result, eq=1)
        assert result.get(key) == item

    def test_is_valid_item_key(self, helper_manager):
        """Test is_valid_item_key method """
        assert helper_manager.obj.is_valid_item_key(
            key=("a", "b")
        ) is True

        assert helper_manager.obj.is_valid_item_key(
            key=("", "")
        ) is False

        assert helper_manager.obj.is_valid_item_key(
            key="a"
        ) is False

        assert helper_manager.obj.is_valid_item_key(
            key=None
        ) is False

    def test_is_valid_item_value(self, helper_manager):
        """Test is_valid_item_value method """
        assert helper_manager.obj.is_valid_item_value(
            value=("a", "b")
        ) is True

        assert helper_manager.obj.is_valid_item_value(
            value=("", "")
        ) is False

        assert helper_manager.obj.is_valid_item_value(
            value="a"
        ) is False

        assert helper_manager.obj.is_valid_item_value(
            value=None
        ) is False
