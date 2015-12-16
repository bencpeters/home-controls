"""Equipment related DB models
"""

# Ben Peters (bencpeters@gmail.com)

from enum import Enum

from sqlalchemy import (
    Column, Integer, Float, Unicode, Boolean, DateTime
)

from home_controller.db import (
    Base, Timestamps, UniqueId, BaseType, Session, HasFloatDataCollection
)
from home_controller.tools import ThreadedExecutor

class EquipmentTypes(Enum):
    BINARY = 0

class Equipment(ThreadedExecutor, Timestamps, UniqueId, BaseType,
                HasFloatDataCollection, Base):
    """Base class for generic implementation of interacting with equipment.
    """
    __tablename__ = 'equipment'
    data_table_name = 'equipment_data'
    types = EquipmentTypes
    name = Column(Unicode, nullable=False)
    last_update = Column(DateTime)

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(Equipment, self).__init__()

    @property
    def current_state(self):
        if getattr(self, "_latest_data", None) is not None:
            try:
                return { v.name: v.value for v in self._latest_data }
            except TypeError:
                return self._latest_data.value

    def update_state(self, new_state, *args, **kwargs):
        """Inherit this method to update the state of the equipment

        This method should be thread-safe, and take care of securing locks on
        any required shared resources.
        """
        raise NotImplementedError("An equipment definition must implement "
                                  "update_state")

    def set(self, new_state, *args, **kwargs):
        args = (new_state,) + args

        try:
            self.execute(self.update_state, self._update_data, *args, **kwargs)
        except Exception as e:
            self.log.error("Error setting equipment {} to {}: {}".format(
                self.name,
                new_state,
                e
            ))

class BinaryEquipment(Equipment):
    """Basic equipment class that can be either on (1) or off (0)
    """
    __mapper_args__ = {
        'polymorphic_identity': Equipment.types.BINARY.value
    }

    def __init__(self, state_name, *args, **kwargs):
        """`state_name` is used to be the name of the value object that this
        equipment has.
        """
        if state_name is None:
            state_name = "state"

        self.state_name = state_name
        self.type_ = Equipment.types.BINARY.value
        super(BinaryEquipment, self).__init__(*args, **kwargs)

    def update_state(self, new_state, *args, **kwargs):
        """Update mechanism enforces binary state
        """
        if (new_state > 0.5):
            new_state = 1.0
        else:
            new_state = 0.0
        return self.value_type(new_state, self.state_name)
