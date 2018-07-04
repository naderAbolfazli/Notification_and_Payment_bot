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

from Config import Config
from ai.bale.notification_bot.constants import Command, Attr, ResponseValue, BotMessages, Pattern, MessageButtonAction, \
    MimeType, TransferInfo, MsgUID, LogMessage, UserData
from ai.bale.notification_bot.logger import Logger
from ai.bale.notification_bot.models.base import Base, engine, Session
from ai.bale.notification_bot.models.message import Message
from ai.bale.notification_bot.models.notification import Notification
from ai.bale.notification_bot.models.receipt import Receipt

my_logger = Logger.get_logger()

locale.setlocale(locale.LC_ALL, Config.system_local)
updater = Updater(token=Config.bot_token,
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()


def success(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_peer = user_data[UserData.user_peer]
    step_name = user_data[UserData.step_name]
    my_logger.info(LogMessage.successful_step_message_sending,
                   extra={UserData.user_id: user_peer.peer_id, UserData.step_name: step_name, "tag": "info"})


def failure(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_peer = user_data[UserData.user_peer]
    step_name = user_data[UserData.step_name]
    message = user_data[UserData.message]
    user_data[UserData.attempt] += 1
    if user_data[UserData.attempt] < Config.resending_max_try:
        bot.send_message(message, user_peer, success, failure)
        return
    my_logger.info(LogMessage.failed_step_message_sending,
                   extra={UserData.user_id: user_peer.peer_id, UserData.step_name: step_name, "tag": "info"})


def receipt_report_success(response, user_data):
    user_data = user_data[UserData.kwargs]
    my_logger.info(LogMessage.successful_report_sending,
                   extra={UserData.user_id: user_data[UserData.user_peer].peer_id, "tag": "info"})


def receipt_report_failure(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_data[UserData.report_attempt] += 1
    if user_data[UserData.report_attempt] <= Config.resending_max_try:
        bot.send_message(user_data[UserData.doc_message], user_data[UserData.user_peer],
                         success_callback=receipt_report_success,
                         failure_callback=receipt_report_failure, kwargs=user_data)
        return
    my_logger.info(LogMessage.failed_report_sending,
                   extra={UserData.user_id: user_data[UserData.user_peer].peer_id, "tag": "info"})


def generate_receipt_report(peer_id):
    with open('files/{}.csv'.format(peer_id), 'w') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        records = session.query(Receipt).join(Message).join(Notification).filter(
            Notification.peer_id == peer_id
        ).all()
        rs = []
        for record in records:
            rs.append((record.payer, record.receiver, record.message.notification.text,
                       record.message.notification.card_number, record.message.notification.money_amount,
                       jdatetime.datetime.fromgregorian(datetime=record.purchasing_time),
                       jdatetime.datetime.fromgregorian(datetime=record.message.sent_time),
                       record.is_expenditure, record.description, record.status, record.traceNo))
        header = ("payerId", "receiverId", "text", "payedCardNo", "amount", "purchasingTime", "purchaseMessageTime",
                  "isExpenditure", "description", "status", "traceNo")
        writer.writerow(header)
        for r in rs:
            writer.writerow(r)
    return outfile


notification = {}


@dispatcher.command_handler([Command.start])
def conversation_starter(bot, update):
    global notification
    notification.clear()
    notification[Attr.peer_id] = update.body.sender_user.peer_id
    notification[Attr.peer_access_hash] = update.body.sender_user.access_hash
    general_message = TextMessage(BotMessages.service_selection)
    btn_list = [TemplateMessageButton(BotMessages.setup_notification, ResponseValue.setup_notification,
                                      MessageButtonAction.default),
                TemplateMessageButton(BotMessages.showing_receipts, ResponseValue.showing_receipts,
                                      MessageButtonAction.default)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {UserData.user_peer: update.get_effective_user(), UserData.step_name: "conversation_starter", "message": message}
    bot.respond(update, message, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.setup_notification]), ask_time),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.showing_receipts]), showing_receipts),
        MessageHandler(DefaultFilter(), wrong_periodic_state),
        CommandHandler([Command.start], conversation_starter)
    ])


def showing_receipts(bot, update):
    def file_upload_success(result, user_data):
        file_id = str(user_data.get(Attr.file_id, None))
        file_url = str(user_data.get(Attr.url))
        my_logger.info(LogMessage.successful_report_upload,
                       extra={"for_user": user_peer.peer_id, "file_url": file_url})
        access_hash = str(user_data.get(Attr.user_id, None))
        doc_message = DocumentMessage(file_id=file_id, access_hash=access_hash, name="purchase_report.csv",
                                      file_size=outfile.__sizeof__(), mime_type=MimeType.csv,
                                      caption_text=TextMessage(BotMessages.receipts_report))
        kwargs = {"user_peer": user_peer, "doc_message": doc_message, "report_attempt": 1}
        bot.send_message(doc_message, user_peer, success_callback=receipt_report_success,
                         failure_callback=receipt_report_failure, kwargs=kwargs)

    def file_upload_failure(result, user_data):
        global upload_attempt
        upload_attempt += 1
        if upload_attempt <= Config.reuploading_max_try:
            bot.upload_file(file="files/{}.csv".format(notification[Attr.peer_id]), file_type="file",
                            success_callback=file_upload_success,
                            failure_callback=file_upload_failure)
            return
        my_logger.log(LogMessage.failed_report_upload)

    user_peer = update.get_effective_user()
    outfile = generate_receipt_report(notification[Attr.peer_id])
    upload_attempt = 1
    bot.upload_file(file="files/{}.csv".format(notification[Attr.peer_id]), file_type="file",
                    success_callback=file_upload_success,
                    failure_callback=file_upload_failure)
    dispatcher.finish_conversation(update)


def ask_time(bot, update):
    message = TextMessage(BotMessages.ask_time)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "ask_time", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.persian_datetime), periodic_state),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_time)])


def wrong_time(bot, update):
    message = TextMessage(BotMessages.wrong_format)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "wrong_time", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.persian_datetime), periodic_state),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_time)])


def periodic_state(bot, update):
    str_date = update.get_effective_message().text
    notification[Attr.date_time] = jdatetime.datetime.strptime(str_date, Config.accepted_datetime_format)
    general_message = TextMessage(BotMessages.periodic_state_selection)
    btn_list = [TemplateMessageButton(BotMessages.only_once, ResponseValue.only_once, MessageButtonAction.default),
                TemplateMessageButton(BotMessages.iterative, ResponseValue.iterative, MessageButtonAction.default)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "periodic_state", "message": message}
    bot.respond(update, message, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.only_once]), ask_type),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.iterative]), period_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_periodic_state)

    ])


def wrong_periodic_state(bot, update):
    message = TextMessage(BotMessages.wrong_answer)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "wrong_periodic_state", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.only_once]), ask_type),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.iterative]), period_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_periodic_state)
    ])


def period_type(bot, update):
    general_message = TextMessage(BotMessages.periodic_type_selection)
    btn_list = [TemplateMessageButton(BotMessages.daily, ResponseValue.daily, MessageButtonAction.default),
                TemplateMessageButton(BotMessages.weekly, ResponseValue.weekly, MessageButtonAction.default),
                TemplateMessageButton(BotMessages.monthly, ResponseValue.monthly, MessageButtonAction.default)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "period_type", "message": message}
    bot.respond(update, message, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.daily]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.weekly]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.monthly]), ask_iterate_number),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_period_type)
    ])


def wrong_period_type(bot, update):
    message = TextMessage(BotMessages.wrong_answer)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "wrong_period_type", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.daily]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.weekly]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.monthly]), ask_iterate_number),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_period_type)
    ])


def ask_iterate_number(bot, update):
    notification[Attr.periodic_type] = update.get_effective_message().text_message
    message = TextMessage(BotMessages.iterate_number_selection)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "ask_iterate_number", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.number), ask_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_iterate_number)
    ])


def wrong_iterate_number(bot, update):
    message = TextMessage(BotMessages.wrong_answer_pls_number)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.number), ask_type),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_iterate_number)
    ])


def ask_type(bot, update):
    if notification.get(Attr.iterate_number) is None:
        notification[Attr.iterate_number] = int(update.get_effective_message().text)
    else:
        notification[Attr.iterate_number] = 0

    general_message = TextMessage(BotMessages.notification_type_selection)
    btn_list = [TemplateMessageButton(BotMessages.normal, ResponseValue.normal, MessageButtonAction.default),
                TemplateMessageButton(BotMessages.debt, ResponseValue.debt, MessageButtonAction.default)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.normal]), ask_picture),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.debt]), ask_card_number),
        MessageHandler(DefaultFilter(), wrong_type)])


def wrong_type(bot, update):
    message = TextMessage(BotMessages.wrong_answer)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.normal]), ask_picture),
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.debt]), ask_card_number),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_type)])


def ask_card_number(bot, update):
    notification[Attr.type] = ResponseValue.debt
    message = TextMessage(BotMessages.card_number_entering)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.card_number), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number),
        CommandHandler([Command.start], conversation_starter)])


def wrong_card_number(bot, update):
    message = TextMessage(BotMessages.wrong_card_number)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.card_number), ask_amount),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_card_number)])


def ask_amount(bot, update):
    notification[Attr.card_number] = update.get_effective_message().text
    message = TextMessage(BotMessages.amount_entering)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Pattern.number), ask_picture),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_amount)
    ])


def wrong_amount(bot, update):
    message = TextMessage(BotMessages.wrong_answer_pls_number)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
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
                                  TemplateMessageButton(BotMessages.no_picture_needed, ResponseValue.no_picture,
                                                        MessageButtonAction.default)])
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.no_picture]), ask_text),
        MessageHandler(PhotoFilter(), getting_picture),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_picture)])


def wrong_picture(bot, update):
    message = TextMessage(BotMessages.wrong_answer)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ResponseValue.no_picture]), ask_text),
        MessageHandler(PhotoFilter(), getting_picture),
        CommandHandler([Command.start], conversation_starter),
        MessageHandler(DefaultFilter(), wrong_picture)])


def getting_picture(bot, update):
    notification[Attr.file_id] = update.body.message.file_id
    notification[Attr.file_access_hash] = update.body.message.access_hash
    notification[Attr.file_size] = update.body.message.file_size
    message = TextMessage(BotMessages.notification_text_entering)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        MessageHandler(DefaultFilter(), wrong_name_response),
                                                        CommandHandler([Command.start], conversation_starter)])


def ask_text(bot, update):
    message = TextMessage(BotMessages.notification_text_entering)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [MessageHandler(TextFilter(), finnish_notification_register),
                                                        CommandHandler([Command.start], conversation_starter),
                                                        MessageHandler(DefaultFilter(), wrong_name_response)])


def wrong_name_response(bot, update):
    message = TextMessage(BotMessages.wrong_answer_pls_text)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
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
    my_logger.info(LogMessage.notification_registering,
                   extra={"peer_id": notification[Attr.peer_id], "text": notification[Attr.text],
                          "type": notification[Attr.type]})
    message = TextMessage(BotMessages.successful_notification_registering)
    kwargs = {"user_peer": update.get_effective_user(), "step_name": "", "message": message}
    bot.respond(update, message, success, failure, kwargs=kwargs)
    dispatcher.finish_conversation(update)


def time_delta_func(type):
    return {
        ResponseValue.daily: datetime.timedelta(days=1),
        ResponseValue.weekly: datetime.timedelta(weeks=1),
        ResponseValue.monthly: datetime.timedelta(days=30)
    }[type]


@dispatcher.message_handler([BankMessageFilter()])
def handling_bank_message(bot, update):
    if len(update.get_effective_user().peer_id) < 3:  # bot id 2digit
        return
    transfer_info = update.get_effective_message().bank_ext_message.transfer_info.items
    is_expenditure = transfer_info[TransferInfo.isExpenditure].value.get_json_object()['value']
    payer = transfer_info[TransferInfo.payer].value.get_json_object()['value']
    receiver = transfer_info[TransferInfo.receiver].value.get_json_object()['value']
    description = transfer_info[TransferInfo.description].value.get_json_object()['text']
    status = transfer_info[TransferInfo.status].value.get_json_object()['text']
    msgUID = transfer_info[TransferInfo.msgUID].value.get_json_object()['text']
    random_id = str(msgUID).split("-")[MsgUID.random_id]
    trace_no = None
    if status == TransferInfo.success_status:
        trace_no = transfer_info[TransferInfo.traceNo].value.get_json_object()['value']
    purchase_message_date = str(msgUID).split("-")[msgUID.date]
    purchased_message = session.query(Message).filter(
        Message.response_date == purchase_message_date).filter(
        Message.random_id == random_id).one()
    current_time = datetime.datetime.now()
    receipt = Receipt(purchased_message, payer, receiver, is_expenditure, current_time, status, trace_no, description)
    session.add(receipt)
    session.commit()
    my_logger.info(LogMessage.registering_receipt,
                   extra={"payer": payer, "receiver": receiver, "description": description})


updater.run()
