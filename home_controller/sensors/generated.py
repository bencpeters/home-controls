"""Sensors that produce computer generated data for testing/dev purposes.
"""

# Ben Peters (bencpeters@gmail.com)

import random
from time import time
from math import sin, pi

from .models import Sensor

class RandomValuesSensor(Sensor):
    """Randomly generates two values in [0, 1.0] using `random.random()`
    """
    __mapper_args__ = {
        'polymorphic_identity': Sensor.types.RANDOM_VALUES.value
    }

    def __init__(self, *args, **kwargs):
        random.seed()
        self.type_ = self.types.RANDOM_VALUES.value
        super(RandomValuesSensor, self).__init__(*args, **kwargs)

    def read(self, *args, **kwargs):
        """Generates 2 random values

        Returns `SensorDataValues` objects
        """
        return [ self.value_type(random.random(), "value_{}".format(i)) \
                 for i in range(0, 2) ]

class SineWaveSensor(Sensor):
    """Generates a Sine wave betwen the specified limits with the specified
    period.
    """

    __mapper_args__ = {
        'polymorphic_identity': Sensor.types.SINE_WAVE.value
    }

    def __init__(self, period=60, min_value=0, max_value=10, **kwargs):
        """
        :param period: Period of oscillation for the sensor, in seconds
        :param min_value: minimum value for the sensor
        :param max_value: maximum value for the sensor
        """
        self.period = period
        if (self.period <= 0):
            raise ValueError("period ({}) must be greater than 0!".format(
                             period))

        self.min = min_value
        self.max = max_value
        if not self.max > self.min:
            raise ValueError("max_value ({}) must be greater than min_value "
                             "({})".format(max_value, min_value))
        self._start = time()
        self.type_ = self.types.SINE_WAVE.value
        super(SineWaveSensor, self).__init__(**kwargs)

    def read(self, *args, **kwargs):
        """Starts the internal Sine Wave generator and outputs its value based
        on time.
        """
        amp = (self.max - self.min) / 2
        offset = amp + self.min
        interval = (time() - self._start) * 2 * pi / self.period
        return [ self.value_type(sin(interval) * amp + offset, "value") ]
