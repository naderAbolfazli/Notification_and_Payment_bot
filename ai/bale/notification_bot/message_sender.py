import asyncio
import datetime

import jdatetime
from balebot.models.base_models import UserPeer
from balebot.models.messages import PhotoMessage, TextMessage, PurchaseMessage
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater
from balebot.utils.util_functions import generate_random_id
from sqlalchemy import cast, Date

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
    time_delta = current_time + datetime.timedelta(minutes=1)
    passed_day = current_time - datetime.timedelta(days=1)

    today_not_sent_messages = session.query(Message).filter(Message.sent == False).filter(  # not sent messages
        cast(Message.sending_time, Date) == current_time.date())

    going_to_send_messages = today_not_sent_messages.filter(Message.sending_time > current_time).filter(
        Message.sending_time <= time_delta).all()
    sending_messages = going_to_send_messages

    missed_messages = today_not_sent_messages.filter(Message.sending_time < current_time).filter(
        Message.sending_time > passed_day).all()
    sending_messages += missed_messages

    for m in sending_messages:
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
        if notification.type == "debt":
            final_message = PurchaseMessage(msg=message, account_number=notification.card_number,
                                            amount=notification.money,
                                            money_request_type=MoneyRequestType.normal)
        else:
            final_message = message
        random_id = generate_random_id()
        loop.call_later(60, send_message, final_message, user_peer, random_id)
        m.sent = True
        m.time = jdatetime.datetime.now()
        m.random_id = random_id
        session.commit()
    loop.call_later(60, db_pulling)


def send_message(message, user_peer, random_id):
    kwargs = {"random_id": random_id}
    bot.send_message(message, user_peer, random_id=random_id, success_callback=success,
                     failure_callback=failure, kwargs=kwargs)


def success(response, user_data):
    user_data = user_data["kwargs"]
    random_id = user_data["random_id"]
    msg = session.query(Message).filter(Message.random_id == random_id).all()[0]  # it only return one msg
    response_date = response.body.date
    msg.response_date = response_date
    session.commit()
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


loop.call_soon(db_pulling)

updater.run()
