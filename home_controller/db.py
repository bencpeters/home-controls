"""App-wide DB definitions
"""

# Ben Peters (bencpeters@gmail.com)

import json
from datetime import datetime

from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import (
    ForeignKey, Column, DateTime, Integer, Float, Unicode
)
from sqlalchemy.sql.expression import func

from home_controller.log import logger


class Base(object):
    """Mixin to augment the declarative base with logging & other common model
    functionality
    """
    @property
    def log(self):
        return logger
Base = declarative_base(cls=Base)

class Timestamps(object):
    """Mixin for adding TimeStamp columns to a model
    """
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

class UniqueId(object):
    """Mixin for adding a unique id column to a model
    """
    id = Column(Integer, primary_key=True, nullable=False)

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    Recipe from 
    http://docs.sqlalchemy.org/en/rel_0_9/core/custom_types.html#marshal-json-strings

    Usage::

        JSONEncodedDict(255)

    """
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

session_factory = sessionmaker()
Session = scoped_session(session_factory)

class BaseType(object):
    """Mixin for a class that is intended to be the base class for a wide
    variety of inherited types.
    """
    @declared_attr
    def type_(cls):
        return Column(Integer, nullable=False)
    attributes = Column(JSONEncodedDict)

    __mapper_args__ = {
        "polymorphic_on": type_
    }

    @property
    def type_string(self):
        """Accessor for the string type name
        """
        if getattr(self, "types", None) is not None:
            return self.types(self.type).name

class _DataCollection(UniqueId):
    """Base class that gets used for dynamically created classes in
    HasFloatDataCollection mixin. This is the collection of values that is
    linked with the parent class.
    """
    timestamp = Column(DateTime)

    def __init__(self, parent, values):
        try:
            len(values)
            self.values = values
        except:
            self.values = [values]

        self.parent = parent

class _DataCollectionValues(UniqueId):
    """Base class that gets used for dynamically created classes in
    HasFloatDataCollection mixin. This is the actual value holder that is
    linked with the records collection.
    """
    value = Column(Float)
    name = Column(Unicode(20), nullable=False)

    def __init__(self, value, name, record=None):
        self.value = value
        self.name = name
        self.record = record

class HasFloatDataCollection(object):
    """Mixin to add data collection tables & relationships.
    """
    @declared_attr
    def data(cls):
        make_cls_name = lambda n: "".join(
            [s.capitalize() for s in cls.data_table_name.split("_")]) + n

        collection = type(make_cls_name("Collection"),
            (_DataCollection, Base), {
            "__tablename__": cls.data_table_name,
            "values": relationship(make_cls_name("CollectionValues"),
                                   backref="record"),
            "parent_id": Column(Integer,
                                ForeignKey("{}.id".format(cls.__tablename__)),
                                nullable=False),
        })

        values = type(make_cls_name("CollectionValues"),
            (_DataCollectionValues, Base), {
            "__tablename__": cls.data_table_name + "_values",
            "record_id": Column(Integer,
                                ForeignKey("{}.id".format(cls.data_table_name)),
                                nullable=False),
        })

        cls.record_type = collection
        cls.value_type = values

        return relationship(collection, backref="parent")

    def _update_data(self, data):
        """Helper function to update the DB with new data values

        Create our own session so that we're threadsafe
        """
        session = Session()
        session.add(self.record_type(self, data))

        try:
            self.last_update = datetime.utcnow()
        except AttributeError:
            pass

        session.commit()
        self._latest_data = data
        try:
            self.log.debug("Updated data for {cls_name} {name}".format(
                cls_name=self.__class__.__name__,
                name=self.name,
            ))
        except AttributeError:
            pass
