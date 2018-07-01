from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ai.bale.bot.base import Base


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    peer_id = Column(String, nullable=False)
    peer_access_hash = Column(String, nullable=False)
    time_period_id = Column(Integer, ForeignKey("time_period.id"))
    time_period = relationship("TimePeriod", backref="notifications")
    type = Column(String, nullable=False)
    interval = Column(Integer, nullable=False)
    only_once = Column(BOOLEAN, nullable=False)
    name = Column(String)
    card_number = Column(String)
    money = Column(String)
    stopper = Column(String)
    file_id = Column(String)
    file_access_hash = Column(String)
    on_state = Column(BOOLEAN)

    def __init__(self, peer_id=None, peer_access_hash=None, time=None, type=None, card_number=None, money=None,
                 interval=None, weekdays=None, name=None, stopper=None, file_id=None, file_access_hash=None,
                 only_once=False, on_state=True):
        self.peer_id = peer_id
        self.peer_access_hash = peer_access_hash
        self.time = time
        self.type = type
        self.weekdays = weekdays
        self.card_number = card_number
        self.money = money
        self.interval = interval
        self.name = name
        self.stopper = stopper
        self.file_id = file_id
        self.file_access_hash = file_access_hash
        self.only_once = only_once
        self.on_state = on_state
