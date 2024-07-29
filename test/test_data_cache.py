#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test DataChecker class."""
import pytest
from vemonitor_m8.core.data_cache import DataCache


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            self.obj = DataCache(
                max_rows=10
            )

        def init_nodes_test(self):
            """Init DataCache nodes"""
            # reset data cache
            self.obj.reset_data_cache()
            # get all nodes list
            data = self.obj.get_cache_nodes_keys_list()
            assert data == []
            # register nodes
            assert self.obj.register_node('pytest_1') is True
            assert self.obj.register_node('pytest_2') is True
            assert self.obj.register_node('pytest_3') is True

        def add_data_test(self):
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


class TestDataChecker:
    """Test DataChecker class."""

    def test_add_data_cache(self, helper_manager):
        """Test add_data_cache method."""
        # init nodes test
        helper_manager.init_nodes_test()
        # Set max data cache to 10 items
        helper_manager.obj.set_max_rows(10)
        # add more cache data
        helper_manager.add_data_test()

        pytest_1_keys = helper_manager.obj.get_cache_keys_by_node(
            node='pytest_1'
        )
        pytest_2_keys = helper_manager.obj.get_cache_keys_by_node(
            node='pytest_2'
        )
        pytest_3_keys = helper_manager.obj.get_cache_keys_by_node(
            node='pytest_3'
        )
        assert len(pytest_1_keys) == 10
        assert len(pytest_2_keys) == 10
        assert len(pytest_3_keys) == 10

    def test_get_data_from_cache(self, helper_manager):
        """Test get_data_from_cache method."""
        # init nodes test
        helper_manager.init_nodes_test()
        # Set max data cache to 10 items
        helper_manager.obj.set_max_rows(10)
        # add more cache data
        helper_manager.add_data_test()

        # get all data from cache
        result, last_time, max_time = helper_manager.obj.get_data_from_cache()
        assert len(result) == 22
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

        # get all 'V' values from pytest_1 node data
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

        # get first four time keys data from time 1722013484
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

        # get first four pytest_1 nodes data from time 1722013484
        result, last_time, max_time = helper_manager.obj.get_data_from_cache(
           from_time=1722013484,
           nb_items=4,
           structure={'pytest_1': ['V', 'I']}
        )
        assert result == {
            1722013484: {'pytest_1': {'V': 70.8, 'I': 45.52}},
            1722013485: {'pytest_1': {'V': 71.8, 'I': 46.52}},
            1722013486: {'pytest_1': {'V': 72.8, 'I': 47.52}},
            1722013487: {'pytest_1': {'V': 73.8, 'I': 48.52}}
        }
        assert max_time == 1722013487
        assert last_time == 1722013488
