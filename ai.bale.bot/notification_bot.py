"""Notification Bot
for Bale
author: Nader"""

import asyncio
import datetime

from balebot.filters import *
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.messages import *
from balebot.updater import Updater
from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

updater = Updater(token="",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

Base = declarative_base()


class Notifications(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    time = Column(Time, nullable=False)
    interval = Column(Integer, nullable=False)
    name = Column(String)
    stopper = Column(String)
    file_id = Column(String)
    access_hash = Column(String)


engine = create_engine('postgresql://postgres:nader1993@localhost:5432/testdb')

Base.metadata.create_all(engine)


def success(response, user_data):
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data.get())


def final_download_success(result, user_data):
    print("download was successful : ", result)
    stream = user_data.get("byte_stream", None)
    print(type(stream))
    info = user_data["kwargs"]
    print(info["user_id"])

    with open("../files/notification_photo_" + info["user_id"] + "_" + info["notification_name"], "wb") as file:
        file.write(stream)
        file.close()


notification = {}


@dispatcher.command_handler(["/start"])
def conversation_starter(bot, update):
    general_message = TextMessage("انتخاب سرویس")
    btn_list = [TemplateMessageButton("هشدار", "هشدار", 0),
                TemplateMessageButton("بدهی", "بدهی", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["هشدار"]),
                       notification_menu),
        MessageHandler(TemplateResponseFilter(keywords=["بدهی"]),
                       create_debit)])


def notification_menu(bot, update):
    general_message = TextMessage("انتخاب کنید")
    btn_list = [TemplateMessageButton("ایجاد", "ایجاد", 0),
                TemplateMessageButton("حذف", "حذف", 0),
                TemplateMessageButton("تغییر", "تغییر", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["ایجاد"]),
                       create_notification),
        MessageHandler(TemplateResponseFilter(keywords=["حذف"]),
                       notification_menu),
        MessageHandler(TemplateResponseFilter(keywords=["تغییر"]),
                       notification_menu)])


def create_notification(bot, update):
    bot.respond(update, TextMessage("time:\nexample: 13:20"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=""), ask_picture),
        MessageHandler(DefaultFilter(), incorrect_time)])


def incorrect_time(bot, update):
    bot.respond(update, TextMessage("فرمت وارد شده صحیح نیست مجدد وارد کنید"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=""), ask_picture),
        MessageHandler(DefaultFilter(), incorrect_time)])


def ask_picture(bot, update):
    notification["time"] = update.get_effective_message().text
    bot.respond(update, TextMessage("تصویر(اختیاری)"))
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(PhotoFilter(), getting_picture),
                                                                MessageHandler(DefaultFilter(), skip_picture)])


def getting_picture(bot, update):
    notification["file_id"] = update.body.message.file_id
    notification["access_hash"] = update.body.message.access_hash
    notification["user_id"] = update.body.sender_user.peer_id
    bot.respond(update, TextMessage("متن هشدار:"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), ask_interval),
                                                                MessageHandler(DefaultFilter(), wrong_name_response)])


def skip_picture(bot, update):
    bot.respond(update, TextMessage("بدون عکس.\nمتن هشدار:"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), ask_interval),
                                                                MessageHandler(DefaultFilter(), wrong_name_response)])


def wrong_name_response(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب. لطفا متن وارد کنید"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), ask_interval),
                                                                MessageHandler(DefaultFilter(), wrong_name_response)])


def ask_interval(bot, update):
    notification["name"] = update.get_effective_message().text
    bot.respond(update, TextMessage("بازه زمانی هشدار(ثانیه):"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]+$"), ask_stopper),
        MessageHandler(DefaultFilter(), wrong_interval_response)])


def wrong_interval_response(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب. لطفا عدد وارد کنید"), success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(pattern="^[0-9]+$"), ask_stopper),
                                                        MessageHandler(DefaultFilter(), wrong_interval_response)])


def ask_stopper(bot, update):
    notification["interval"] = update.get_effective_message().text
    bot.respond(update, TextMessage("فرمان توقف:"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(), finnish_notification_register),
        MessageHandler(DefaultFilter(), wrong_stopper_response)])


def wrong_stopper_response(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب. لطفا متن وارد کنید"), success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register()),
                                                        MessageHandler(DefaultFilter(), wrong_name_response)])


def finnish_notification_register(bot, update):
    notification["stopper"] = update.get_effective_message().text
    bot.respond(update, TextMessage("هشدار با موفقیت ثبت شد(نمونه پیام)"), success, failure)
    if notification.__contains__("file_id"):
        message = PhotoMessage(file_id=notification["file_id"], access_hash=notification["access_hash"], name="Hoshdar",
                               file_size='11337',
                               mime_type="image/jpeg", caption_text=TextMessage(notification["name"]),
                               file_storage_version=1, thumb=None)
    else:
        message = TextMessage(notification["name"])
    bot.respond(update, message, success, failure)
    print(notification)
    notification.clear()
    dispatcher.finish_conversation(update)


def create_debit(bot, update):
    pass


updater.run()
