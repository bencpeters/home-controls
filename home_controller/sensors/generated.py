"""Sensors that produce computer generated data for testing/dev purposes.
"""

# Ben Peters (bencpeters@gmail.com)

import random

from .models import Sensor, SensorDataValues, SensorTypes

class RandomValuesSensor(Sensor):
    """Randomly generates two values in [0, 1.0] using `random.random()`
    """
    __mapper_args__ = {
        'polymorphic_identity': SensorTypes.RANDOM_VALUES.value
    }

    def __init__(self, **kwargs):
        self.type = SensorTypes.RANDOM_VALUES.value
        random.seed()
        super().__init__(**kwargs)

    def read(self, *args, **kwargs):
        """Generates 2 random values

        Returns `SensorDataValues` objects
        """
        return [ SensorDataValues(random.random(), "value_{}".format(i)) \
                 for i in range(0, 2) ]
