from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    peer_id = Column(String, nullable=False)
    peer_access_hash = Column(String, nullable=False)
    time = Column(Time, nullable=False)
    type = Column(String, nullable=False)
    interval = Column(Integer, nullable=False)
    card_number = Column(String)
    money = Column(String)
    name = Column(String)
    stopper = Column(String)
    file_id = Column(String)
    file_access_hash = Column(String)

    def __init__(self, peer_id=None, peer_access_hash=None, time=None, type=None, card_number=None, money=None,
                 interval=None, name=None, stopper=None, file_id=None, file_access_hash=None):
        self.peer_id = peer_id
        self.peer_access_hash = peer_access_hash
        self.time = time
        self.type = type
        self.card_number = card_number
        self.money = money
        self.interval = interval
        self.name = name
        self.stopper = stopper
        self.file_id = file_id
        self.file_access_hash = file_access_hash
