#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test Utils class."""
from vemonitor_m8.core.utils import Utils as Ut

class TestUtils:
    """Test Utils class."""

    def test_get_min_in_loop(self):
        """Test check_columns method."""
        result = Ut.get_min_in_loop(
            value=0,
            min_val=6
        )
        assert result == 6

        result = Ut.get_min_in_loop(
            value=12,
            min_val=6
        )
        assert result == 6

        result = Ut.get_min_in_loop(
            value=3,
            min_val=6
        )
        assert result == 3

    def test_get_max_in_loop(self):
        """Test get_max_in_loop method."""
        result = Ut.get_max_in_loop(
            value=0,
            max_val=6
        )
        assert result == 6

        result = Ut.get_max_in_loop(
            value=3,
            max_val=6
        )
        assert result == 6

        result = Ut.get_max_in_loop(
            value=12,
            max_val=6
        )
        assert result == 12

    def test_all_equal(self):
        """Test all_equal method."""
        result = Ut.all_equal(
            iterable=[1, 1, 1, 1, 1]
        )
        assert result is True

        result = Ut.all_equal(
            iterable=[1, 1, 2, 1, 1]
        )
        assert result is False

        result = Ut.all_equal(
            iterable=(1, 1, 1, 1, 1)
        )
        assert result is True

        result = Ut.all_equal(
            iterable=(1, 1, 2, 1, 1)
        )
        assert result is False

        result = Ut.all_equal(
            iterable={'a': 1, 'b': 1, 'c': 1, 'd': 1}
        )
        assert result is False
    
    def test_is_valid_port(self):
        """Test is_valid_port method."""
        assert Ut.is_valid_port(0) is False
        assert Ut.is_valid_port(-1) is False
        assert Ut.is_valid_port(65536) is False
        assert Ut.is_valid_port(1) is True
        assert Ut.is_valid_port(65535) is True

    def test_is_valid_host(self):
        """Test is_valid_host method."""
        assert Ut.is_valid_host(0) is False
        assert Ut.is_valid_host('0') is False
        assert Ut.is_valid_host('0.0') is False
        assert Ut.is_valid_host('0.0.0') is False
        assert Ut.is_valid_host('256.255.255.255') is False
        assert Ut.is_valid_host('255.256.255.255') is False
        assert Ut.is_valid_host('255.255.256.255') is False
        assert Ut.is_valid_host('255.255.255.256') is False
        assert Ut.is_valid_host('-1.255.255.255') is False
        assert Ut.is_valid_host('255.-1.255.255') is False
        assert Ut.is_valid_host('255.255.-1.255') is False
        assert Ut.is_valid_host('255.255.255.-1') is False


        assert Ut.is_valid_host('0.0.0.0') is True
        assert Ut.is_valid_host('255.255.255.255') is True
        assert Ut.is_valid_host('127.0.0.1') is True
        assert Ut.is_valid_host('192.168.1.1') is True