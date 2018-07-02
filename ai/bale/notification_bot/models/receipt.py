from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from ai.bale.notification_bot.models.base import Base


class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    purchasing_time = Column(DateTime)
    description = Column(String)
    status = Column(String)
    traceNo = Column(String)
    message = relationship("Message", backref="receipts")

    def __init__(self, message, purchasing_time=None, description=None,
                 status=None, trace_no=None):
        self.message = message
        self.purchasing_time = purchasing_time
        self.description = description
        self.status = status
        self.traceNo = trace_no
