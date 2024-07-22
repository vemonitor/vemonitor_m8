#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test Utils class."""
import pytest
from ve_utils.utype import UType as Ut
from vemonitor_m8.core.utils import Utils as Utvm

class TestUtils:
    """Test Utils class."""

    def test_get_min_in_loop(self):
        """Test check_columns method."""
        result = Utvm.get_min_in_loop(
            value=0,
            min_val=6
        )
        assert result == 6

        result = Utvm.get_min_in_loop(
            value=12,
            min_val=6
        )
        assert result == 6

        result = Utvm.get_min_in_loop(
            value=3,
            min_val=6
        )
        assert result == 3

    def test_get_max_in_loop(self):
        """Test get_max_in_loop method."""
        result = Utvm.get_max_in_loop(
            value=0,
            max_val=6
        )
        assert result == 6

        result = Utvm.get_max_in_loop(
            value=3,
            max_val=6
        )
        assert result == 6

        result = Utvm.get_max_in_loop(
            value=12,
            max_val=6
        )
        assert result == 12

    def test_all_equal(self):
        """Test all_equal method."""
        result = Utvm.all_equal(
            iterable=[1, 1, 1, 1, 1]
        )
        assert result is True

        result = Utvm.all_equal(
            iterable=[1, 1, 2, 1, 1]
        )
        assert result is False

        result = Utvm.all_equal(
            iterable=(1, 1, 1, 1, 1)
        )
        assert result is True

        result = Utvm.all_equal(
            iterable=(1, 1, 2, 1, 1)
        )
        assert result is False

        result = Utvm.all_equal(
            iterable={'a': 1, 'b': 1, 'c': 1, 'd': 1}
        )
        assert result is False
