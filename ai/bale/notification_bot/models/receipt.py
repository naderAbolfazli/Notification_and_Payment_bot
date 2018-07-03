from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, BOOLEAN
from sqlalchemy.orm import relationship

from ai.bale.notification_bot.models.base import Base


class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    payer = Column(String)
    receiver = Column(String)
    purchasing_time = Column(DateTime)
    is_expenditure = Column(BOOLEAN)
    description = Column(String)
    status = Column(String)
    traceNo = Column(String)
    message = relationship("Message", backref="receipts")

    def __init__(self, message, payer, receiver, is_expenditure, purchasing_time,
                 status, trace_no, description=None):
        self.message = message
        self.payer = payer
        self.receiver = receiver
        self.is_expenditure = is_expenditure
        self.purchasing_time = purchasing_time
        self.description = description
        self.status = status
        self.traceNo = trace_no
