from sqlalchemy import Column, Integer, Time, BOOLEAN, ForeignKey, DATETIME
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship, backref

from ai.bale.bot.base import Base


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    time = Column(TIMESTAMP)
    sent = Column(BOOLEAN)
    notification = relationship("Notification", backref="messages")

    def __init__(self, notification, time=None, sent=False):
        self.notification = notification
        self.time = time
        self.sent = sent
