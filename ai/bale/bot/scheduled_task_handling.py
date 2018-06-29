"""Notification Bot
for Bale
author: Nader"""

import asyncio
import datetime
import functools
import threading
import time

import schedule
from balebot.filters import DefaultFilter, TextFilter
from balebot.updater import Updater
from sqlalchemy import or_, and_

from ai.bale.bot.base import Session, engine, Base
from ai.bale.bot.message import Message
from ai.bale.bot.notification import Notification
from ai.bale.bot.time_period import TimePeriod, DayNumber

updater = Updater(token="0f8c34cd08e81d3604f23f712a095f167dfc37d8",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()

taskStopper = {}
notificationCanceler = {}


def success(response, user_data):
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


@dispatcher.message_handler([TextFilter()])
def stopper_handler(bot, update):
    peer_id = update.get_effective_user().peer_id
    message = update.get_effective_message().text
    taskStopper[peer_id] = message
    notificationCanceler[peer_id] = message


def db_pulling():
    current_time = datetime.datetime.now()
    first_day_of_year = datetime.datetime(current_time.year, 1, 1)
    later_10min = current_time + datetime.timedelta(minutes=10)
    notifications = session.query(Notification).join(TimePeriod).join(DayNumber).filter(Notification.on_state == True).\
        filter(or_(and_(TimePeriod.type == "هفتگی", DayNumber.day_number == (current_time.weekday() + 2) % 7),
                   and_(TimePeriod.type == "ماهانه", DayNumber.day_number == current_time.day),
                   and_(TimePeriod.type == "سالانه",
                        DayNumber.day_number == (current_time - first_day_of_year).days + 1),
                   and_(TimePeriod.type == "روزانه"))).filter(
        current_time.time() < TimePeriod.time).filter(TimePeriod.time < later_10min.time()).all()
    for notification in notifications:
        for day in notification.time_period.days:
            print(day.day_number)
        schedule_time = str(notification.time_period.time)[0:5]
        schedule.every().day.at(schedule_time).do(functools.partial(
            send_notification_task, notification))


def push_message_to_db(notification):
    message_object = Message(notification, datetime.datetime.now())
    session.add(message_object)
    session.commit()
    # bot.send_message(message=message, peer=user_peer, success_callback=success, failure_callback=failure)


def sending_message_canceler(iter_job, notification):
    peer_id = notification.peer_id
    stopper = notification.stopper
    while taskStopper[peer_id] != stopper:
        time.sleep(1)
    schedule.cancel_job(iter_job)
    if notification.only_once:
        notification.on_state = False
        session.commit()
    print("task stopped")


def send_notification_task(notification):
    taskStopper[notification.peer_id] = ""
    notificationCanceler[notification.peer_id] = ""
    iter_job = schedule.every(notification.interval).seconds.do(functools.partial(push_message_to_db, notification))
    threading.Thread(target=sending_message_canceler, args=(iter_job, notification)).start()
    print("some task started")
    return schedule.CancelJob


def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(target=schedule_loop, args=()).start()

schedule.every(2).minutes.do(db_pulling)

db_pulling()

updater.run()
