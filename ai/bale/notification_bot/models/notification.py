from sqlalchemy import Column, Integer, String, BOOLEAN

from ai.bale.notification_bot.models.base import Base


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    peer_id = Column(String, nullable=False)
    peer_access_hash = Column(String, nullable=False)
    type = Column(String, nullable=False)
    text = Column(String)
    card_number = Column(String)
    money_amount = Column(String)
    file_id = Column(String)
    file_access_hash = Column(String)
    on_state = Column(BOOLEAN)

    def __init__(self, peer_id=None, peer_access_hash=None, type=None, card_number=None, money=None,
                 text=None, file_id=None, file_access_hash=None, on_state=True):
        self.peer_id = peer_id
        self.peer_access_hash = peer_access_hash
        self.type = type
        self.card_number = card_number
        self.money_amount = money
        self.text = text
        self.file_id = file_id
        self.file_access_hash = file_access_hash
        self.on_state = on_state
