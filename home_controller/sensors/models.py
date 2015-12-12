"""Sensor-related DB models
"""

# Ben Peters (bencpeters@gmail.com)

from enum import Enum
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import (
    ForeignKey,
    Column, Integer, Float, Unicode, Boolean, DateTime
)
from sqlalchemy.orm import relationship, backref

from home_controller.db import Base, JSONEncodedDict, Session
from home_controller.log import logger

class SensorTypes(Enum):
    RANDOM_VALUES = 0
    SINE_WAVE = 1

class SensorData(Base):
    """Class for sensor data tuple in DB. A record should be created every time
    a sensor is updated (`sensor.update()`)

    It has a one to many relationship with `SensorDataValues` where the actual
    numeric sensor values are written. This allows us to have variable # of
    values for different sensor types.
    """
    __tablename__ = 'sensor_data'
    id = Column(Integer, primary_key=True, nullable=False)
    timestamp = Column(DateTime)
    values = relationship("SensorDataValues", backref="record")
    sensor_id = Column(Integer, ForeignKey('sensors.id'), nullable=False)

    def __init__(self, sensor, values):
        self.values = values
        self.sensor = sensor

class SensorDataValues(Base):
    """Class to hold actual numeric sensor values.
    """
    __tablename__ = 'sensor_data_values'
    id = Column(Integer, primary_key=True, nullable=False)
    record_id = Column(Integer, ForeignKey('sensor_data.id'), nullable=False)
    value = Column(Float)
    value_name = Column(Unicode(20), nullable=False)

    def __init__(self, value, name, record=None):
        self.value = value
        self.value_name = name
        self.record = record

class Sensor(Base):
    """Base sensor class contains generic implementations for interacting with 
    sensors
    """
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(Integer, nullable=False)
    sensor_name = Column(Unicode, nullable=False)
    last_update = Column(DateTime)
    attributes = Column(JSONEncodedDict)
    data = relationship("SensorData", backref="sensor")

    __mapper_args__ = {
        "polymorphic_on": type
    }

    def __init__(self, sensor_name, *args, **kwargs):
        self.sensor_name = sensor_name
        self._executor = None

    @property
    def read_executor(self):
        if self._executor is None:
            self._executor = ThreadPoolExecutor(1)
        return self._executor

    @property
    def log(self):
        return logger

    @property
    def current_value(self):
        return self._value

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
        future = self.read_executor.submit(self.read, args, kwargs)
        try:
            values = future.result()
            session = Session()
            session.add(SensorData(self, values))
            session.commit()
            self.log.debug("Read sensor {}".format(self.sensor_name))
        except Exception as e:
            self.log.error("Error reading sensor {}: {}".format(
                self.sensor_name, e
            ))
