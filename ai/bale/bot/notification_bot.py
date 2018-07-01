"""Notification Bot
for Bale
author: Nader"""

import asyncio
import datetime

from balebot.filters import *
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.base_models import FatSeqUpdate
from balebot.models.base_models.banking.receipt_message import ReceiptMessage
from balebot.models.base_models.value_types import MapValueItem
from balebot.models.messages import *
from balebot.models.messages.banking.money_request_type import *
from balebot.models.messages.banking.purchase_message import *
from balebot.models.server_responses.messaging.message_sent import MessageSent
from balebot.updater import Updater

from ai.bale.bot.base import Base, engine, Session
from ai.bale.bot.message import Message
from ai.bale.bot.notification import Notification
from ai.bale.bot.receipt import Receipt
from ai.bale.bot.time_period import TimePeriod, DayNumber

updater = Updater(token="0f8c34cd08e81d3604f23f712a095f167dfc37d8",
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()


def success(response, user_data):
    print("success : ", response)
    print(user_data)


def failure(response, user_data):
    print("failure : ", response)
    print(user_data)


def purchase_message_success(response, user_data):
    print("purchase response success :")


def purchase_message_failure(response, user_data):
    print("purchase response failure :")


notification = Notification()
time_period = TimePeriod()


@dispatcher.command_handler(["/start"])
def conversation_starter(bot, update):
    global notification
    global time_period
    notification = Notification()
    notification.peer_id = update.body.sender_user.peer_id
    notification.peer_access_hash = update.body.sender_user.access_hash
    time_period = TimePeriod()
    general_message = TextMessage("انتخاب نوع هشدار")
    btn_list = [TemplateMessageButton("عادی", "عادی", 0),
                TemplateMessageButton("بدهی", "بدهی", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["عادی"]), periodic_state),
        MessageHandler(TemplateResponseFilter(keywords=["بدهی"]), ask_card_number),
        MessageHandler(DefaultFilter(), wrong_type)])


def wrong_type(bot, update):
    bot.respond(update, "جواب نامناسب", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["عادی"]), periodic_state),
        MessageHandler(TemplateResponseFilter(keywords=["بدهی"]), ask_card_number),
        MessageHandler(DefaultFilter(), wrong_type),
        CommandHandler(["/start"], conversation_starter)])


def ask_card_number(bot, update):
    notification.type = "بدهی"
    bot.respond(update, "شماره کارت فرد مورد نظر را وارد کنید:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]{16}$"), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number)],
                                                       CommandHandler(["/start"], conversation_starter))


def wrong_card_number(bot, update):
    bot.respond(update, "فرمت شماره کارت صحیح نمیباشد:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]{16}$"), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number)],
                                                       CommandHandler(["/start"], conversation_starter))


def ask_amount(bot, update):
    notification.card_number = update.get_effective_message().text
    bot.respond(update, "مبلغ را به ریال وارد کنید:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]+"), periodic_state),
        MessageHandler(DefaultFilter(), wrong_amount),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_amount(bot, update):
    bot.respond(update, "جواب نامناسب لطفا عدد وارد کنید:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^[0-9]+"), periodic_state),
        MessageHandler(DefaultFilter(), wrong_amount),
        CommandHandler(["/start"], conversation_starter)
    ])


def periodic_state(bot, update):
    if notification.type is None:
        notification.type = "عادی"
    else:
        notification.money = update.get_effective_message().text
    general_message = TextMessage("نوع اعلان هشدار")
    btn_list = [TemplateMessageButton("فقط یکبار", "فقط یکبار", 0),
                TemplateMessageButton("تکرار شونده", "تکرار شونده", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["فقط یکبار"]), period_type),
        MessageHandler(TemplateResponseFilter(keywords=["تکرار شونده"]), period_type),
        MessageHandler(DefaultFilter(), wrong_periodic_state),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_periodic_state(bot, update):
    bot.respond(update, "جواب نامناسب", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["فقط یکبار"]), period_type),
        MessageHandler(TemplateResponseFilter(keywords=["تکرار شونده"]), period_type),
        MessageHandler(DefaultFilter(), wrong_periodic_state),
        CommandHandler(["/start"], conversation_starter)
    ])


def period_type(bot, update):
    if update.get_effective_message().text_message == "فقط یکبار":
        notification.only_once = True
    general_message = TextMessage("انتخاب بازه زمانی")
    btn_list = [TemplateMessageButton("روزانه", "روزانه", 0),
                TemplateMessageButton("هفتگی", "هفتگی", 0),
                TemplateMessageButton("ماهانه", "ماهانه", 0),
                TemplateMessageButton("سالانه", "سالانه", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["روزانه"]), ask_time),
        MessageHandler(TemplateResponseFilter(keywords=["هفتگی"]), ask_days),
        MessageHandler(TemplateResponseFilter(keywords=["ماهانه"]), ask_days),
        MessageHandler(TemplateResponseFilter(keywords=["سالانه"]), ask_days),
        MessageHandler(DefaultFilter(), wrong_period_type),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_period_type(bot, update):
    bot.respond(update, "جواب نامناسب", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["روزانه"]), ask_time),
        MessageHandler(TemplateResponseFilter(keywords=["هفتگی"]), ask_days),
        MessageHandler(TemplateResponseFilter(keywords=["ماهانه"]), ask_days),
        MessageHandler(TemplateResponseFilter(keywords=["سالانه"]), ask_days),
        MessageHandler(DefaultFilter(), wrong_period_type),
        CommandHandler(["/start"], conversation_starter)
    ])


period_pattern = {"هفتگی": "^[0-6]$",
                  "ماهانه": "^[1-2][0-9]|[1-9]|30$",
                  "سالانه": "^[0-2][0-9][0-9]|3[0-5][0-9]|36[0-5]$"}


def ask_days(bot, update):
    time_period.type = update.get_effective_message().text_message
    general_message = TextMessage(
        "روز های مورد نظر در بازه ی خود را به صورت عددی در آن باز وارد کنید و در اتمام از کلید استفاده کنید")
    btn_list = [TemplateMessageButton("اتمام", "اتمام", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=period_pattern[time_period.type]), receive_days),
        MessageHandler(DefaultFilter(), wrong_day),
        CommandHandler(["/start"], conversation_starter)
    ])


def receive_days(bot, update):
    time_period.days += [DayNumber(update.get_effective_message().text)]
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["اتمام"]), ask_time),
        MessageHandler(TextFilter(pattern=period_pattern[time_period.type]), receive_days),
        MessageHandler(DefaultFilter(), wrong_day),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_day(bot, update):
    bot.respond(update, "جواب نامناسب", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["اتمام"]), ask_time),
        MessageHandler(TextFilter(pattern=period_pattern[time_period.type]), receive_days),
        MessageHandler(DefaultFilter(), wrong_day),
        CommandHandler(["/start"], conversation_starter)
    ])


def ask_time(bot, update):
    if time_period.type is None:
        time_period.type = "روزانه"
    bot.respond(update, "زمان:\nنمونه(۱۳:۲۰)", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$"), ask_picture),
        MessageHandler(DefaultFilter(), wrong_time),
        CommandHandler(["/start"], conversation_starter)])


def wrong_time(bot, update):
    bot.respond(update, "فرمت وارد شده صحیح نیست مجدد وارد کنید", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]$"), ask_picture),
        MessageHandler(DefaultFilter(), wrong_time),
        CommandHandler(["/start"], conversation_starter)])


def ask_picture(bot, update):
    time_period.time = update.get_effective_message().text
    bot.respond(update, "تصویر(اختیاری)", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(PhotoFilter(), getting_picture),
                                                                MessageHandler(DefaultFilter(), skip_picture)],
                                                       CommandHandler(["/start"], conversation_starter))


def getting_picture(bot, update):
    notification.file_id = update.body.message.file_id
    notification.file_access_hash = update.body.message.access_hash
    bot.respond(update, "متن هشدار:", success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        MessageHandler(DefaultFilter(),
                                                                       wrong_name_response),
                                                        CommandHandler(["/start"], conversation_starter)])


def skip_picture(bot, update):
    bot.respond(update, "بدون عکس.\nمتن هشدار:", success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        MessageHandler(DefaultFilter(),
                                                                       wrong_name_response),
                                                        CommandHandler(["/start"], conversation_starter)])


def wrong_name_response(bot, update):
    bot.respond(update, "جواب نامناسب. لطفا متن وارد کنید", success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        MessageHandler(DefaultFilter(),
                                                                       wrong_name_response),
                                                        CommandHandler(["/start"], conversation_starter)])


#
#
# def ask_interval(bot, update):
#     notification.name = update.get_effective_message().text
#     bot.respond(update, "وقفه زمانی هشدار(ثانیه):", success, failure)
#     dispatcher.register_conversation_next_step_handler(update, [
#         MessageHandler(TextFilter(pattern="^[0-9]+$"), ask_stopper),
#         MessageHandler(DefaultFilter(), wrong_interval_response)])
#
#
# def wrong_interval_response(bot, update):
#     bot.respond(update, "جواب نامناسب. لطفا بین 0 و 30 وارد کنید", success, failure)
#     dispatcher.register_conversation_next_step_handler(update,
#                                                        [MessageHandler(TextFilter(pattern="^[1-2][0-9]|[1-9]$"),
#                                                                        ask_stopper),
#                                                         MessageHandler(DefaultFilter(), wrong_interval_response)])
#
#
# def ask_stopper(bot, update):
#     notification.interval = update.get_effective_message().text
#     bot.respond(update, "فرمان توقف:", success, failure)
#     dispatcher.register_conversation_next_step_handler(update, [
#         MessageHandler(TextFilter(), finnish_notification_register),
#         MessageHandler(DefaultFilter(), wrong_stopper_response)])
#
#
# def wrong_stopper_response(bot, update):
#     bot.respond(update, "جواب نامناسب. لطفا متن وارد کنید", success, failure)
#     dispatcher.register_conversation_next_step_handler(update,
#                                                        [MessageHandler(TextFilter(), finnish_notification_register),
#                                                         MessageHandler(DefaultFilter(), wrong_stopper_response)])
#

def finnish_notification_register(bot, update):
    notification.name = update.get_effective_message().text
    # notification.stopper = update.get_effective_message().text
    bot.respond(update, TextMessage("هشدار با موفقیت ثبت شد(نمونه پیام)"), success, failure)
    if notification.file_id != None:
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
    notification.time_period = time_period
    session.add(notification)
    session.commit()
    bot.respond(update, final_message, purchase_message_success, purchase_message_failure)
    dispatcher.finish_conversation(update)


@dispatcher.message_handler([BankMessageFilter()])
def handling_bank_message(bot, update):
    if len(update.get_effective_user().peer_id) < 3:
        return
    transfer_info = update.get_effective_message().bank_ext_message.transfer_info.items
    d = {"description": 4, "date": 9, "status": 10, "msgUID": 6, "traceNo": 12}
    description = transfer_info[d["description"]].value.get_json_object()['text']
    status = transfer_info[d["status"]].value.get_json_object()['text']
    msgUID = transfer_info[d["msgUID"]].value.get_json_object()['text']
    random_id = str(msgUID).split("-")[0]
    # trace_no = None
    # if status == "SUCCESS":
    trace_no = transfer_info[d["traceNo"]].value.get_json_object()['value']
    purchase_message_date = str(msgUID).split("-")[1]
    purchased_notification = session.query(Message).filter(
        Message.response_date == purchase_message_date).filter(
        Message.random_id == random_id).all()[0].notification
    current_time = datetime.datetime.now()
    receipt = Receipt(purchased_notification, purchase_message_date, current_time, description, status, trace_no)
    session.add(receipt)
    session.commit()
    print("receipt registered in db")


updater.run()
