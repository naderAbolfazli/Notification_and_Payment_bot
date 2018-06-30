from sqlalchemy import Column, Integer, Time, BOOLEAN, ForeignKey, DATETIME, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship, backref

from ai.bale.bot.base import Base


class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    purchasing_time = Column(TIMESTAMP)
    purchase_message_date = Column(String)
    description = Column(String)
    status = Column(String)
    traceNo = Column(String)
    notification = relationship("Notification", backref="receipts")

    def __init__(self, notification, purchase_message_date=None, purchasing_time=None, description=None,
                 status=None, trace_no=None):
        self.notification = notification
        self.purchase_message_date = purchase_message_date
        self.purchasing_time = purchasing_time
        self.description = description
        self.status = status
        self.traceNo = trace_no
