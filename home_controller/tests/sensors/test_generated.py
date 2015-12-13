"""Test sensor functionality using the computer generated sensors
"""

# Ben Peters (bencpeters@gmail.com)

from nose.tools import *
from time import sleep

from home_controller.tests import DatabaseTest
from home_controller.sensors import RandomValuesSensor, Sensor, SineWaveSensor

class TestRandomSensor(DatabaseTest):
    """
    Tests basic sensor functionality with the simplest generated sensor.
    """
    def setup(self):
        self.sensor = RandomValuesSensor(sensor_name="random")
        super().setup()

    def _test_random_value(self, values):
        eq_(len(values), 2)
        for val in values:
            ok_(isinstance(val, Sensor.value_type),
                "Type of values should be SensorDataValues, got {}".format(
                    type(val)))
            ok_(abs(val.value) < 100,
                "Val should be between -100, 100, got {}".format(val))

    def test_read_sensor(self):
        self._test_random_value(self.sensor.read())

    def test_update_sensor_reads_sensor(self):
        self.sensor.update()
        sleep(0.1)
        records = self.sensor.data
        eq_(len(records), 1)
        self._test_random_value(records[0].values)

    def test_update_sensor_adds_objects_to_db(self):
        eq_(len(self.sensor.data), 0)
        self.sensor.update()
        sleep(0.1)
        records = self.session.query(Sensor). \
            filter(Sensor.id == self.sensor.id).first().data
        eq_(len(records), 1)
        self._test_random_value(records[0].values)

class TestSineWaveSensor(DatabaseTest):
    def setup(self):
        self.period = 0.1
        self.max = 10
        self.min = -2
        self.sensor = SineWaveSensor(sensor_name="sine", period = self.period,
                                     max_value=self.max, min_value=self.min)
        super().setup()

    def test_read_sensor(self):
        start_val = self.sensor.read()[0]
        ok_(isinstance(start_val, Sensor.value_type),
            "Type of values should be SensorDataValues, got {}".format(
            type(start_val)))

        # check the period works properly
        sleep(self.period * 0.95)
        end_val = self.sensor.read()[0]
        ok_(abs(end_val.value - start_val.value) < 1,
            "Sine Wave sensor should have appropriate periodicity. Got values "
            "start: {}, end: {}".format(start_val.value, end_val.value))

        # make sure the value is actually changing
        sleep(self.period * 0.3)
        val = self.sensor.read()[0]
        ok_(val.value < self.max and val.value > self.min,
            "Value {} should be between {} and {}".format(val.value, self.min,
                                                          self.max))
        ok_(abs(val.value - end_val.value) > 1, "Value {} should have changed "
                "from {}".format(val.value, end_val.value))
