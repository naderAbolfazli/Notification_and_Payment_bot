from sqlalchemy import Column, Integer, Time, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship, backref

from ai.bale.bot.base import Base


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    time = Column(Time)
    sent = Column(BOOLEAN)
    notification = relationship("Notification", backref=backref("messages", uselist=False))

    def __init__(self, notification, time=None, sent=False):
        self.notification = notification
        self.time = time
        self.sent = sent
