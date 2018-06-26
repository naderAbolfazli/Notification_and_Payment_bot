from sqlalchemy import Column, Integer, Time, BOOLEAN, ForeignKey, DATETIME, TIME, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship, backref

from ai.bale.bot.base import Base


class TimePeriod(Base):
    __tablename__ = 'time_period'
    id = Column(Integer, primary_key=True)
    time = Column(TIME, nullable=False)
    type = Column(String, nullable=False)
    days = relationship("DayNumber", order_by="DayNumber.day_number", collection_class=ordering_list('day_number'))

    def __init__(self, time=None, type=None):
        self.time = time
        self.type = type


class DayNumber(Base):
    __tablename__ = 'day_numbers'
    id = Column(Integer, primary_key=True)
    day_number = Column(Integer, nullable=False)
    time_period_id = Column(Integer, ForeignKey("time_period.id"))

    def __init__(self, day_number):
        self.day_number = day_number
