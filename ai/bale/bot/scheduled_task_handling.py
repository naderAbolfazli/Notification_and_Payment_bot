"""Notification Bot
for Bale
author: Nader"""

import _thread
import asyncio
import functools
import threading
import time
from threading import Thread

import schedule
from balebot.filters import DefaultFilter
from balebot.models.base_models import UserPeer, Peer
from balebot.models.constants.peer_type import PeerType
from balebot.updater import Updater
from balebot.models.messages import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ai.bale.bot.notification import Notification
from ai.bale.bot.stoppable_thread import StoppableThread

updater = Updater(token="",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

engine = create_engine('postgresql://postgres:nader1993@localhost:5432/testdb')
Session = sessionmaker(bind=engine)
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
    user_id = update.get_effective_user().peer_id
    message = update.get_effective_message().text
    jobStopper[user_id] = message


def db_pushing():
    notifications = session.query(Notification).all()  # notifications within an hour
    for notification in notifications:
        job(notification)


def job(notification):
    user_peer = Peer(PeerType.user, notification.user_id, notification.peer_access_hash)
    # print("hi job " + notification.user_id, notification.peer_access_hash)
    if notification.file_id:
        message = PhotoMessage(file_id=notification.file_id, access_hash=notification.file_access_hash,
                               name="Hoshdar",
                               file_size='11337',
                               mime_type="image/jpeg", caption_text=TextMessage(notification.name),
                               file_storage_version=1, thumb=None)
    else:
        message = TextMessage(notification.name)

    schedule.every().day.at(str(notification.time)[:5]).do(functools.partial(
        send_notification, message, user_peer, notification.interval, notification.stopper))


def notification_thread_starting(message, user_peer, interval):
    while True:
        bot.send_message(message=message, peer=user_peer, success_callback=success, failure_callback=failure)
        # print(user_peer.peer_id + " " + message.)
        time.sleep(interval)


def send_notification(message, user_peer, interval, stopper):
    jobStopper[user_peer.peer_id] = ""
    # notif_thread = StoppableThread(target=notification_thread_starting, args=(message, user_peer, interval))
    # notif_thread.start()
    print("job started")
    while jobStopper[user_peer.peer_id] != stopper:
        bot.send_message(message=message, peer=user_peer, success_callback=success, failure_callback=failure)
        time.sleep(interval)
    print("job canceled")
    # notif_thread.stop()
    return schedule.CancelJob


def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)


# schedule.every(2).seconds.do(job)
db_pushing()
# schedule.every().hour.do(db_pushing)
# db_pushing()

sch_thread = threading.Thread(target=schedule_loop, )
sch_thread.start()

updater.run()
