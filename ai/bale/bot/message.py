from sqlalchemy import Column, Integer, Time, BOOLEAN, ForeignKey, DATETIME, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship, backref

from ai.bale.bot.base import Base


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    time = Column(TIMESTAMP)
    random_id = Column(String)
    response_date = Column(String)
    sent = Column(BOOLEAN)
    notification = relationship("Notification", backref="messages")

    def __init__(self, notification, time=None, random_id=None, response_date=None, sent=False):
        self.notification = notification
        self.time = time
        self.random_id = random_id
        self.response_date = response_date
        self.sent = sent
