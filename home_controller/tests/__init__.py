"""Base initialization for tests
"""

# Ben Peters (bencpeters@gmail.com)

from sqlalchemy.engine import create_engine

from home_controller.db import Base, Session, session_factory

def setup_module():
    global connection, engine

    engine = create_engine('sqlite://')
    connection = engine.connect()
    Base.metadata.create_all(connection)
    session_factory.configure(bind=engine)

def teardown_module():
    connection.close()
    engine.dispose()

class DatabaseTest(object):
    def setup(self):
        self.__transaction = connection.begin()
        self.session = Session()

    def teardown(self):
        self.session.close()
        self.__transaction.rollback()
