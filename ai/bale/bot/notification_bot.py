"""Notification Bot
for Bale
author: Nader"""

import asyncio

from balebot.filters import *
from balebot.handlers import MessageHandler
from balebot.models.messages import *
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai.bale.bot.notification import Notification

updater = Updater(token="",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

engine = create_engine('postgresql://postgres:nader1993@localhost:5432/testdb')
Session = sessionmaker(bind=engine)
session = Session()

Notification.metadata.create_all(engine)


def success(response, user_data):
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


notification = Notification()


@dispatcher.command_handler(["/start"])
def conversation_starter(bot, update):
    global notification
    notification = Notification()
    general_message = TextMessage("انتخاب نوع هشدار")
    btn_list = [TemplateMessageButton("عادی", "عادی", 0),
                TemplateMessageButton("بدهی", "بدهی", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["عادی"]), ask_time),
        MessageHandler(TemplateResponseFilter(keywords=["بدهی"]), ask_card_number)])


def wrong_type(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["عادی"]), ask_time),
        MessageHandler(TemplateResponseFilter(keywords=["بدهی"]), ask_card_number)])


def ask_card_number(bot, update):
    notification.type = "بدهی"
    bot.respond(update, TextMessage("شماره کارت فرد مورد نظر را وارد کنید:"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]{16}$"), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number)])


def wrong_card_number(bot, update):
    bot.respond(update, TextMessage("فرمت شماره کارت صحیح نمیباشد:"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]{16}$"), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number)])


def ask_amount(bot, update):
    notification.card_number = update.get_effective_message().text
    bot.respond(update, TextMessage("مبلغ را به ریال وارد کنید:"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]+"), ask_time),
        MessageHandler(DefaultFilter(), wrong_amount)
    ])


def wrong_amount(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب لطفا عدد وارد کنید:"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]+"), ask_time),
        MessageHandler(DefaultFilter(), wrong_amount)
    ])


# def notification_menu(bot, update):
#     general_message = TextMessage("انتخاب کنید")
#     btn_list = [TemplateMessageButton("ایجاد", "ایجاد", 0),
#                 TemplateMessageButton("حذف", "حذف", 0),
#                 TemplateMessageButton("تغییر", "تغییر", 0)]
#     message = TemplateMessage(general_message=general_message, btn_list=btn_list)
#     bot.respond(update, message, success_callback=success, failure_callback=failure)
#     dispatcher.register_conversation_next_step_handler(update, [
#         MessageHandler(TemplateResponseFilter(keywords=["ایجاد"]),
#                        create_notification),
#         MessageHandler(TemplateResponseFilter(keywords=["حذف"]),
#                        notification_menu),
#         MessageHandler(TemplateResponseFilter(keywords=["تغییر"]),
#                        notification_menu)])


def ask_time(bot, update):
    if notification.type is None:
        notification.type = "عادی"
    else:
        notification.money = update.get_effective_message().text
    bot.respond(update, TextMessage("زمان:\nنمونه(۱۳:۲۰)"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$"), ask_picture),
        MessageHandler(DefaultFilter(), wrong_time)])


def wrong_time(bot, update):
    bot.respond(update, TextMessage("فرمت وارد شده صحیح نیست مجدد وارد کنید"))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$"), ask_picture),
        MessageHandler(DefaultFilter(), wrong_time)])


def ask_picture(bot, update):
    notification.time = update.get_effective_message().text
    bot.respond(update, TextMessage("تصویر(اختیاری)"))
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(PhotoFilter(), getting_picture),
                                                                MessageHandler(DefaultFilter(), skip_picture)])


def getting_picture(bot, update):
    notification.file_id = update.body.message.file_id
    notification.file_access_hash = update.body.message.access_hash
    notification.peer_id = update.body.sender_user.peer_id
    notification.peer_access_hash = update.body.sender_user.access_hash
    bot.respond(update, TextMessage("متن هشدار:"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), ask_interval),
                                                                MessageHandler(DefaultFilter(),
                                                                               wrong_name_response)])


def skip_picture(bot, update):
    bot.respond(update, TextMessage("بدون عکس.\nمتن هشدار:"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), ask_interval),
                                                                MessageHandler(DefaultFilter(),
                                                                               wrong_name_response)])


def wrong_name_response(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب. لطفا متن وارد کنید"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), ask_interval),
                                                                MessageHandler(DefaultFilter(),
                                                                               wrong_name_response)])


def ask_interval(bot, update):
    notification.name = update.get_effective_message().text
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
    notification.interval = update.get_effective_message().text
    bot.respond(update, TextMessage("فرمان توقف:"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(), finnish_notification_register),
        MessageHandler(DefaultFilter(), wrong_stopper_response)])


def wrong_stopper_response(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب. لطفا متن وارد کنید"), success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        MessageHandler(DefaultFilter(), wrong_stopper_response)])


def finnish_notification_register(bot, update):
    notification.stopper = update.get_effective_message().text
    bot.respond(update, TextMessage("هشدار با موفقیت ثبت شد(نمونه پیام)"), success, failure)
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
    bot.respond(update, final_message, success, failure)
    session.add(notification)
    session.commit()

    general_message = TextMessage(" ")
    btn_list = [TemplateMessageButton("پایان", "پایان", 0)]
    tmessage = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, tmessage, success_callback=success, failure_callback=failure)
    dispatcher.finish_conversation(update)


def create_debit(bot, update):
    pass


updater.run()
