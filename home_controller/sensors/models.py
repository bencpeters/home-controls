"""Sensor-related DB models
"""

# Ben Peters (bencpeters@gmail.com)

from enum import Enum

from sqlalchemy import (
    Column, Unicode, DateTime
)

from home_controller.db import (
    Base, Timestamps, UniqueId, BaseType, Session, HasFloatDataCollection
)
from home_controller.tools import ThreadedExecutor

class SensorTypes(Enum):
    RANDOM_VALUES = 0
    SINE_WAVE = 1

class Sensor(ThreadedExecutor, Timestamps, UniqueId, BaseType,
             HasFloatDataCollection, Base):
    """Base sensor class contains generic implementations for interacting with 
    sensors
    """
    __tablename__ = 'sensors'
    data_table_name = 'sensor_data'
    types = SensorTypes
    name = Column(Unicode, nullable=False)
    last_update = Column(DateTime)

    def __init__(self, sensor_name, *args, **kwargs):
        self.name = sensor_name
        super(Sensor, self).__init__()

    @property
    def current_value(self):
        if getattr(self, "_latest_data", None) is not None:
            try:
                return { v.name: v.value for v in self._latest_data }
            except TypeError:
                return self._latest_data.value

    def read(self, *args, **kwargs):
        """Inherit this method to read a sensor

        This method should be thread-safe, and take care of securing locks on
        any required shared resources, as it will be run in its own thread.
        """
        raise NotImplementedError("A sensor defintion must implement read")

    def update(self, *args, **kwargs):
        """Method to update this sensor's value.

        `read` will be called in its own thread.
        """
        try:
            self.execute(self.read, self._update_data, *args, **kwargs)
        except Exception as e:
            self.log.error("Error reading sensor {}: {}".format(
                self.name, e
            ))
