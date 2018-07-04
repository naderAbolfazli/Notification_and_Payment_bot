from sqlalchemy import Column, Integer, BOOLEAN, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, backref

from ai.bale.notification_bot.models.base import Base
from ai.bale.notification_bot.models.notification import Notification


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    sending_time = Column(DateTime, nullable=False)
    sent_time = Column(DateTime)
    random_id = Column(String)
    response_date = Column(String)
    sent = Column(Integer)
    notification = relationship("Notification", backref=backref("messages", cascade="all, delete-orphan"))

    def __init__(self, notification, sending_time, sent_time=None, random_id=None, response_date=None, sent=0):
        self.notification = notification
        self.sending_time = sending_time
        self.sent_time = sent_time
        self.random_id = random_id
        self.response_date = response_date
        self.sent = sent
