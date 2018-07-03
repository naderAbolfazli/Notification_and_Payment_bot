"""Notification Bot
for Bale
author: Nader"""

import asyncio
import csv
import datetime
import locale

import jdatetime
from balebot.filters import *
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.messages import *
from balebot.updater import Updater

from ai.bale.notification_bot.constant.bot_commands import Command
from ai.bale.notification_bot.constant.fields import Attr
from ai.bale.notification_bot.constant.notification_bot_messages import BotMessages
from ai.bale.notification_bot.constant.patterns import Pattern
from ai.bale.notification_bot.constant.response_values import ResponseValue
from ai.bale.notification_bot.models.base import Base, engine, Session
from ai.bale.notification_bot.models.message import Message
from ai.bale.notification_bot.models.notification import Notification
from ai.bale.notification_bot.models.receipt import Receipt

locale.setlocale(locale.LC_ALL, "fa_IR")
print(jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
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


notification = {}


@dispatcher.command_handler([Command.start])
def conversation_starter(bot, update):
    global notification
    notification.clear()
    notification[Attr.peer_id] = update.body.sender_user.peer_id
    notification[Attr.peer_access_hash] = update.body.sender_user.access_hash
    general_message = TextMessage(BotMessages.service_selection)
    btn_list = [TemplateMessageButton(BotMessages.setup_notification, ResponseValue.setup_notification, 0),
                TemplateMessageButton(BotMessages.showing_receipts, ResponseValue.showing_receipts, 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.setup_notification]), ask_time),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.showing_receipts]), showing_receipts),
        MessageHandler(DefaultFilter(), wrong_periodic_state),
        CommandHandler([Command.start], conversation_starter)
    ])


def showing_receipts(bot, update):
    def file_upload_success(result, user_data):
        print("upload was successful : ", result)
        print(user_data)
        file_id = str(user_data.get(Attr.file_id, None))
        access_hash = str(user_data.get(Attr.user_id, None))
        # application / vnd.openxmlformats - officedocument.spreadsheetml.sheet
        doc_message = DocumentMessage(file_id=file_id, access_hash=access_hash, name="purchase_report.csv",
                                      file_size=outfile.__sizeof__(),
                                      mime_type="text/csv",
                                      caption_text=TextMessage(BotMessages.receipts_report))
        bot.send_message(doc_message, user_peer, success_callback=success, failure_callback=failure)

    user_peer = update.get_effective_user()
    with open('files/{}.csv'.format(notification[Attr.peer_id]), 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        records = session.query(Receipt).join(Message).join(Notification).filter(
            Notification.peer_id == notification[Attr.peer_id]
        ).all()
        rs = []
        for record in records:
            rs.append((record.payer, record.receiver, record.message.notification.text,
                       jdatetime.datetime.fromgregorian(datetime=record.purchasing_time),
                       record.is_expenditure, record.description, record.status, record.traceNo))
        header = ("payerId", "receiverId", "isExpenditure", "purchasingTime", "description", "status", "raceNo")
        writer.writerow(header)
        for r in rs:
            writer.writerow(r)

    bot.upload_file(file="files/{}.csv".format(notification[Attr.peer_id]), file_type="file",
                    success_callback=file_upload_success,
                    failure_callback=failure)
    dispatcher.finish_conversation(update)


def ask_time(bot, update):
    bot.respond(update, BotMessages.ask_time, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.persian_datetime), periodic_state),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_time)])


def wrong_time(bot, update):
    bot.respond(update, BotMessages.wrong_format, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.persian_datetime), periodic_state),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_time)])


def periodic_state(bot, update):
    str_date = update.get_effective_message().text
    notification[Attr.date_time] = jdatetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M")
    general_message = TextMessage(BotMessages.periodic_state_selection)
    btn_list = [TemplateMessageButton(BotMessages.only_once, ResponseValue.only_once, 0),
                TemplateMessageButton(BotMessages.iterative, ResponseValue.iterative, 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.only_once]), ask_type),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.iterative]), period_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_periodic_state)

    ])


def wrong_periodic_state(bot, update):
    bot.respond(update, BotMessages.wrong_answer, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.only_once]), ask_type),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.iterative]), period_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_periodic_state)
    ])


def period_type(bot, update):
    notification[Attr.iterate_number] = 0
    general_message = TextMessage(BotMessages.periodic_type_selection)
    btn_list = [TemplateMessageButton(BotMessages.daily, ResponseValue.daily, 0),
                TemplateMessageButton(BotMessages.weekly, ResponseValue.weekly, 0),
                TemplateMessageButton(BotMessages.monthly, ResponseValue.monthly, 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.daily]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.weekly]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.monthly]), ask_iterate_number),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_period_type)
    ])


def wrong_period_type(bot, update):
    bot.respond(update, BotMessages.wrong_answer, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.daily]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.weekly]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.monthly]), ask_iterate_number),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_period_type)
    ])


def ask_iterate_number(bot, update):
    notification[Attr.periodic_type] = update.get_effective_message().text_message
    bot.respond(update, BotMessages.iterate_number_selection, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.number), ask_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_iterate_number)
    ])


def wrong_iterate_number(bot, update):
    bot.respond(update, TextMessage(BotMessages.wrong_answer_pls_number), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.number), ask_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_iterate_number)
    ])


def ask_type(bot, update):
    if notification.get(Attr.iterate_number) is None:
        notification[Attr.iterate_number] = int(update.get_effective_message().text)
    general_message = TextMessage(BotMessages.notification_type_selection)
    btn_list = [TemplateMessageButton(BotMessages.normal, ResponseValue.normal, 0),
                TemplateMessageButton(BotMessages.debt, ResponseValue.debt, 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.normal]), ask_picture),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.debt]), ask_card_number),
        MessageHandler(DefaultFilter(), wrong_type)])


def wrong_type(bot, update):
    bot.respond(update, BotMessages.wrong_answer, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.normal]), ask_picture),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.debt]), ask_card_number),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_type)])


def ask_card_number(bot, update):
    notification[Attr.type] = ResponseValue.debt
    bot.respond(update, BotMessages.card_number_entering, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.card_number), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number),
        CommandHandler([Command.start], conversation_starter)])


def wrong_card_number(bot, update):
    bot.respond(update, BotMessages.wrong_card_number, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.card_number), ask_amount),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_card_number)])


def ask_amount(bot, update):
    notification[Attr.card_number] = update.get_effective_message().text
    bot.respond(update, BotMessages.amount_entering, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.number), ask_picture),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_amount)
    ])


def wrong_amount(bot, update):
    bot.respond(update, BotMessages.wrong_answer_pls_number, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.number), ask_picture),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_amount)
    ])


def ask_picture(bot, update):
    if notification.get(Attr.type):
        notification[Attr.money_amount] = update.get_effective_message().text
    else:
        notification[Attr.type] = ResponseValue.normal
    message = TemplateMessage(general_message=TextMessage(BotMessages.picture_request),
                              btn_list=[
                                  TemplateMessageButton(BotMessages.no_picture_needed, ResponseValue.no_picture, 0)])
    bot.respond(update, message, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.no_picture]), ask_text),
        MessageHandler(PhotoFilter(), getting_picture),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_picture)])


def wrong_picture(bot, update):
    bot.respond(update, BotMessages.wrong_answer, success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.no_picture]), ask_text),
        MessageHandler(PhotoFilter(), getting_picture),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_picture)])


def getting_picture(bot, update):
    notification[Attr.file_id] = update.body.message.file_id
    notification[Attr.file_access_hash] = update.body.message.access_hash
    bot.respond(update, BotMessages.notification_text_entering, success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        MessageHandler(DefaultFilter(), wrong_name_response),
                                                        CommandHandler([Command.start], conversation_starter)])


def ask_text(bot, update):
    bot.respond(update, BotMessages.notification_text_entering, success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        CommandHandler([Command.start], conversation_starter),
                                                        MessageHandler(DefaultFilter(), wrong_name_response)])


def wrong_name_response(bot, update):
    bot.respond(update, BotMessages.wrong_answer_pls_text, success, failure)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        CommandHandler([Command.start], conversation_starter),
                                                        MessageHandler(DefaultFilter(), wrong_name_response)])


def finnish_notification_register(bot, update):
    notification[Attr.text] = update.get_effective_message().text
    db_notification = Notification(notification.get(Attr.peer_id), notification.get(Attr.peer_access_hash),
                                   notification.get(Attr.type), notification.get(Attr.card_number),
                                   notification.get(Attr.money_amount),
                                   notification.get(Attr.text), notification.get(Attr.file_id),
                                   notification.get(Attr.file_access_hash))
    session.add(db_notification)

    start_datetime = notification[Attr.date_time].togregorian()
    time_delta = time_delta_func(notification[Attr.periodic_type])
    for i in range(notification[Attr.iterate_number] + 1):
        message = Message(db_notification, sending_time=(start_datetime + time_delta * i))
        session.add(message)
    session.commit()

    bot.respond(update, BotMessages.successful_notification_registering, success, failure)
    dispatcher.finish_conversation(update)


def time_delta_func(type):
    return {
        ResponseValue.daily: datetime.timedelta(days=1),
        ResponseValue.weekly: datetime.timedelta(weeks=1),
        ResponseValue.monthly: datetime.timedelta(days=30)
    }[type]


@dispatcher.message_handler([BankMessageFilter()])
def handling_bank_message(bot, update):
    if len(update.get_effective_user().peer_id) < 3:
        return
    transfer_info = update.get_effective_message().bank_ext_message.transfer_info.items
    i = {"isExpenditure": 1, "payer": 2, "description": 4, "date": 9, "status": 10, "msgUID": 6,
         "receiver": 7, "traceNo": 12}
    is_expenditure = transfer_info[i["isExpenditure"]].value.get_json_object()['value']
    payer = transfer_info[i["payer"]].value.get_json_object()['value']
    receiver = transfer_info[i["receiver"]].value.get_json_object()['value']
    description = transfer_info[i["description"]].value.get_json_object()['text']
    status = transfer_info[i["status"]].value.get_json_object()['text']
    msgUID = transfer_info[i["msgUID"]].value.get_json_object()['text']
    random_id = str(msgUID).split("-")[0]
    trace_no = None
    if status == "SUCCESS":
        trace_no = transfer_info[i["traceNo"]].value.get_json_object()['value']
    purchase_message_date = str(msgUID).split("-")[1]
    purchased_message = session.query(Message).filter(
        Message.response_date == purchase_message_date).filter(
        Message.random_id == random_id).one()
    current_time = datetime.datetime.now()
    receipt = Receipt(purchased_message, payer, receiver, is_expenditure, current_time, status, trace_no, description)
    session.add(receipt)
    session.commit()
    print("receipt registered in db")


updater.run()
