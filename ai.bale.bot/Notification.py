from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    time = Column(Time, nullable=False)
    type = Column(String, nullable=False)
    interval = Column(Integer, nullable=False)
    name = Column(String)
    stopper = Column(String)
    file_id = Column(String)
    access_hash = Column(String)

    def __init__(self, user_id, time, type, interval, name, stopper, file_id, access_hash):
        self.user_id = user_id
        self.time = time
        self.type = type
        self.interval = interval
        self.name = name
        self.stopper = stopper
        self.file_id = file_id
        self.access_hash = access_hash