"""Notification Bot
for Bale
author: Nader"""

import asyncio
import functools
import threading
import time

import schedule
from balebot.filters import DefaultFilter
from balebot.models.base_models import Peer
from balebot.models.constants.peer_type import PeerType
from balebot.models.messages import *
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater

from ai.bale.bot.base import Session, engine, Base
from ai.bale.bot.message import Message
from ai.bale.bot.notification import Notification

updater = Updater(token="0f8c34cd08e81d3604f23f712a095f167dfc37d8",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()

jobStopper = {}


def success(response, user_data):
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


@dispatcher.message_handler([DefaultFilter()])
def stopper_handler(bot, update):
    peer_id = update.get_effective_user().peer_id
    message = update.get_effective_message().text
    jobStopper[peer_id] = message


async def custom_sleep(delay):
    await asyncio.sleep(delay)


async def db_pushing():
    while True:
        notifications = session.query(Notification).all()  # notifications within an hour
        for notification in notifications:
            threading.Thread(target=job, args=(notification,)).start()
        await asyncio.sleep(10)


def job(notification):
    user_peer = Peer(PeerType.user, notification.peer_id, notification.peer_access_hash)
    if notification.file_id is not None:
        message = PhotoMessage(file_id=notification.file_id, access_hash=notification.file_access_hash,
                               name="Hoshdar",
                               file_size='11337',
                               mime_type="image/jpeg", caption_text=TextMessage(notification.name),
                               file_storage_version=1, thumb=None)
    else:
        message = TextMessage(notification.name)
    if notification.type == "بدهی":
        final_message = PurchaseMessage(msg=message, account_number=notification.card_number, amount=notification.money,
                                        money_request_type=MoneyRequestType.normal)
    else:
        final_message = message

    # schedule.every(str(notification.time)[0:5]).day.do(functools.partial(
    #     send_notification_task, final_message, user_peer, notification.interval, notification.stopper))
    # time_dif = notification.time - datetime.time
    # print(datetime.datetime.now().minute)
    # time.sleep(10)
    message_object = Message(notification)
    session.add(message_object)
    session.commit()
    bot.send_message(final_message, user_peer, success_callback=success, failure_callback=failure)
    send_notification_task(final_message, user_peer, notification.interval, notification.stopper)


def sending_message(message, user_peer):
    bot.send_message(message=message, peer=user_peer, success_callback=success, failure_callback=failure)


def sending_message_canceler(iter_job, peer_id, stopper):
    while jobStopper[peer_id] != stopper:
        time.sleep(1)
    schedule.cancel_job(iter_job)
    print("job canceled")


def send_notification_task(message, user_peer, interval, stopper):
    jobStopper[user_peer.peer_id] = ""
    iter_job = schedule.every(interval).seconds.do(functools.partial(sending_message, message, user_peer))
    stopper_thread = threading.Thread(target=sending_message_canceler, args=(iter_job, user_peer.peer_id, stopper))
    stopper_thread.start()
    # sending_message_canceler(iter_job, user_peer.peer_id, stopper)
    print("job started")
    # return schedule.CancelJob


def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)


def loop_forever():
    iloop = asyncio.new_event_loop()
    asyncio.set_event_loop(iloop)
    iloop.create_task(db_pushing())
    iloop.run_forever()


def updater_run():
    updater.run()


# loop = asyncio.get_event_loop()
# loop.create_task()
# tasks = [asyncio.ensure_future(db_pushing())]
         # asyncio.ensure_future(updater_run())]
# loop.call_later(300, db_pushing())

sch_thread = threading.Thread(target=loop_forever, args=())
sch_thread.start()

# schedule.every(10).seconds.do(db_pushing)

# db_pushing()


updater.run()
