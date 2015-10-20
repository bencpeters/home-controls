"""App-wide DB definitions
"""

# Ben Peters (bencpeters@gmail.com)

import json

from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
