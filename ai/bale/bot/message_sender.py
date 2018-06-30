import asyncio
import datetime

from balebot.models.base_models import UserPeer, Request
from balebot.models.messages import PhotoMessage, TextMessage, PurchaseMessage
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater
from balebot.utils.util_functions import generate_random_id

from ai.bale.bot.message import Message
from ai.bale.bot.notification import Notification
from ai.bale.bot.time_period import *
from ai.bale.bot.base import Session, engine, Base

loop = asyncio.get_event_loop()
updater = Updater(token="0f8c34cd08e81d3604f23f712a095f167dfc37d8",
                  loop=loop)
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()


def db_pulling():
    messages = session.query(Message).join(Notification).filter(Message.sent == False).all()  # not sent messages
    for m in messages:
        print(m)
        notification = m.notification
        user_peer = UserPeer(notification.peer_id, notification.peer_access_hash)
        if notification.file_id is not None:
            message = PhotoMessage(file_id=notification.file_id, access_hash=notification.file_access_hash,
                                   name="Hoshdar",
                                   file_size='11337',
                                   mime_type="image/jpeg", caption_text=TextMessage(notification.name),
                                   file_storage_version=1, thumb=None)
        else:
            message = TextMessage(notification.name)
        if notification.type == "بدهی":
            final_message = PurchaseMessage(msg=message, account_number=notification.card_number,
                                            amount=notification.money,
                                            money_request_type=MoneyRequestType.normal)
        else:
            final_message = message
        random_id = generate_random_id()
        loop.call_soon(send_message, final_message, user_peer, random_id)
        m.sent = True
        m.time = datetime.datetime.now()
        m.random_id = random_id
        session.commit()
    loop.call_later(1, db_pulling)


def send_message(message, user_peer, random_id):
    bot.send_message(message, user_peer, random_id=random_id, success_callback=success, failure_callback=failure)


def success(response, user_data):
    print("success : ", response)
    # response_date = response.date
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


loop.call_soon(db_pulling)

updater.run()
