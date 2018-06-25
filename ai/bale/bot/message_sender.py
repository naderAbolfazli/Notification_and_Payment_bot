import asyncio
import threading
import time

import schedule
from balebot.models.base_models import UserPeer
from balebot.models.messages import PhotoMessage, TextMessage, PurchaseMessage
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater

from ai.bale.bot.message import Message
from ai.bale.bot.notification import Notification
from ai.bale.bot.base import Session, engine, Base

updater = Updater(token="0f8c34cd08e81d3604f23f712a095f167dfc37d8",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()


def db_pushing():
    while True:
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
            bot.send_message(final_message, user_peer, success_callback=success, failure_callback=failure)
            m.sent = True
            session.commit()
            # time.sleep(1)


def success(response, user_data):
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


# def schedule_loop():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)


# schedule.every().second.do(db_pushing)
threading.Thread(target=db_pushing, args=()).start()
updater.run()
