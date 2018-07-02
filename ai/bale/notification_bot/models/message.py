from sqlalchemy import Column, Integer, BOOLEAN, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from ai.bale.notification_bot.models.base import Base
from ai.bale.notification_bot.models.notification import Notification


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    sending_time = Column(DateTime, nullable=False)
    random_id = Column(String)
    response_date = Column(String)
    sent = Column(BOOLEAN)
    notification = relationship("Notification", backref="messages")

    def __init__(self, notification, sending_time, random_id=None, response_date=None, sent=False):
        self.notification = notification
        self.sending_time = sending_time
        self.random_id = random_id
        self.response_date = response_date
        self.sent = sent