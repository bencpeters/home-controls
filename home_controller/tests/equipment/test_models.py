"""Tests basic equipment functionality
"""

# Ben Peters (bencpeters@gmail.com)

from time import sleep
from datetime import datetime
from unittest.mock import MagicMock

from nose.tools import *

from home_controller.tests import DatabaseTest
from home_controller.equipment import Equipment, BinaryEquipment

class TestEquipment(DatabaseTest):
    """Tests basic shared equipment functionality.
    """
    def update_fxn(self, state, *args, **kwargs):
        """Mocked basic implementation of update function
        """
        return Equipment.value_type(state, "value")

    def setup(self):
        self.equip = Equipment("equipment")
        self.equip.type_ = 0
        self.equip.update_state = MagicMock(side_effect=self.update_fxn)
        self.async_wait_time = 0.1
        super().setup()

    def test_set_calls_update_fxn(self):
        val = 0.7
        self.equip.set(val)
        sleep(self.async_wait_time)
        self.equip.update_state.assert_called_once_with(val)

    def test_set_adds_objects_to_db(self):
        val = 0.5
        eq_(len(self.equip.data), 0)
        self.equip.set(val)
        sleep(self.async_wait_time)
        records = self.session.query(Equipment). \
            filter(Equipment.id == self.equip.id).first().data
        eq_(len(records), 1)
        eq_(records[0].values[0].value, val)

    def test_set_updates_current_value(self):
        val = 0.5
        self.equip.set(val)
        sleep(self.async_wait_time)
        curr_val = self.equip.current_state
        eq_(curr_val, val)

    def test_last_update(self):
        start = datetime.now()
        self.equip.set(0.5)
        sleep(self.async_wait_time)
        ok_(self.equip.last_update > start)

class TestBinaryEquipment(DatabaseTest):
    def setup(self):
        self.equip = BinaryEquipment("output", "equip")
        super().setup()

    def _test_val(self, setpoint, exp):
        value = self.equip.update_state(setpoint)
        ok_(isinstance(value, Equipment.value_type),
            "Type of value should be EquipmentDataValues, got {}".format(
                    type(value)))
        eq_(value.value, exp)

    def test_binary_coercion(self):
        tests = [
            (0.0, 0.0),
            (0.1, 0.0),
            (0.4, 0.0),
            (-1.0, 0.0),
            (0.6, 1.0),
            (0.9, 1.0),
            (5.0, 1.0),
        ]
        for val, exp in tests:
            yield self._test_val, val, exp
