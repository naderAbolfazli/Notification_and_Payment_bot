import asyncio
import datetime

import jdatetime
from balebot.models.base_models import UserPeer
from balebot.models.messages import PhotoMessage, TextMessage, PurchaseMessage
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater
from balebot.utils.util_functions import generate_random_id
from sqlalchemy import cast, Date

from ai.bale.notification_bot.constant.notification_bot_messages import BotMessages
from ai.bale.notification_bot.models.base import Session, engine, Base
from ai.bale.notification_bot.models.message import Message

loop = asyncio.get_event_loop()
updater = Updater(token="0f8c34cd08e81d3604f23f712a095f167dfc37d8",
                  loop=loop)
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()


def db_pulling():
    current_time = datetime.datetime.now()

    message_tobe_sent = session.query(Message).filter(Message.sent == 0).filter(  # not sent messages
        cast(Message.sending_time, Date) == current_time.date()).filter(
        Message.sending_time < current_time).all()

    for msg in message_tobe_sent:
        notification = msg.notification
        user_peer = UserPeer(notification.peer_id, notification.peer_access_hash)
        if notification.file_id:
            message = PhotoMessage(file_id=notification.file_id, access_hash=notification.file_access_hash,
                                   name=BotMessages.photo_name,
                                   file_size='11337',
                                   mime_type="image/jpeg", caption_text=TextMessage(notification.name),
                                   file_storage_version=1, thumb=None)
        else:
            message = TextMessage(notification.text)
        if notification.type == "debt":
            final_message = PurchaseMessage(msg=message, account_number=notification.card_number,
                                            amount=notification.money_amount,
                                            money_request_type=MoneyRequestType.normal)
        else:
            final_message = message
        loop.call_soon(send_message, final_message, user_peer, msg)
    loop.call_later(60, db_pulling)


def send_message(base_message, user_peer, msg):
    random_id = generate_random_id()
    msg.random_id = random_id
    session.commit()
    kwargs = {"random_id": random_id, "db_msg": msg}
    bot.send_message(base_message, user_peer, random_id=random_id, success_callback=success,
                     failure_callback=failure, kwargs=kwargs)


def success(response, user_data):
    user_data = user_data["kwargs"]
    msg = user_data["db_msg"]
    msg.response_date = response.body.date
    msg.sent = 1
    session.commit()
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


loop.call_soon(db_pulling)

updater.run()
