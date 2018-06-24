from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    peer_access_hash = Column(String, nullable=False)
    time = Column(Time, nullable=False)
    type = Column(String, nullable=False)
    interval = Column(Integer, nullable=False)
    name = Column(String)
    stopper = Column(String)
    file_id = Column(String)
    file_access_hash = Column(String)

    def __init__(self, user_id, peer_access_hash, time, type, interval, name, stopper, file_id, file_access_hash):
        self.user_id = user_id
        self.peer_access_hash = peer_access_hash
        self.time = time
        self.type = type
        self.interval = interval
        self.name = name
        self.stopper = stopper
        self.file_id = file_id
        self.file_access_hash = file_access_hash