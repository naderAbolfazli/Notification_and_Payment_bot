"""Notification Bot
for Bale
author: Nader"""

import _thread
import asyncio

import schedule
from balebot.updater import Updater
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session

from . import Notification

updater = Updater(token="",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

Base = declarative_base()



def db_pushing():
    within_hour_notif = session.query(Notification)
    pass


def job():
    print("I'm working...")


schedule.every(2).seconds.do(job)


def schedule_loop():
    while True:
        schedule.run_pending()


_thread.start_new_thread(schedule_loop, ())

updater.run()

