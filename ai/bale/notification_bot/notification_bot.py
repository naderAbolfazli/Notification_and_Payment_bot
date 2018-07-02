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
from balebot.models.messages.banking.money_request_type import *
from balebot.models.messages.banking.purchase_message import *
from balebot.updater import Updater

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

pattern = {
    "persian_datetime": "^(139[7-9]|140[0-9])-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|30) ([0-1][0-9]|2[0-3]):[0-5][0-9]$",
    "card_number": "^[0-9]{16}$",
    "number": "^[0-9]+",
    "weekday": "^[0-6]$",
    "month_day": "^[1-2][0-9]|[1-9]|30$",
    "year_day": "^[0-2][0-9][0-9]|3[0-5][0-9]|36[0-5]$"
}


@dispatcher.command_handler(["/start"])
def conversation_starter(bot, update):
    global notification
    notification.clear()
    notification['peer_id'] = update.body.sender_user.peer_id
    notification['peer_access_hash'] = update.body.sender_user.access_hash
    general_message = TextMessage("انتخاب سرویس")
    btn_list = [TemplateMessageButton("تنظیم هشدار", "setup_notification", 0),
                TemplateMessageButton("مشاهده پرداخت ها", "showing_receipts", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["setup_notification"]), ask_time),
        MessageHandler(TemplateResponseFilter(keywords=["showing_receipts"]), showing_receipts),
        MessageHandler(DefaultFilter(), wrong_periodic_state),
        CommandHandler(["/start"], conversation_starter)
    ])


def showing_receipts(bot, update):
    def file_upload_success(result, user_data):
        print("upload was successful : ", result)
        print(user_data)
        file_id = str(user_data.get("file_id", None))
        access_hash = str(user_data.get("user_id", None))
        doc_message = DocumentMessage(file_id=file_id, access_hash=access_hash, name="purchase_report",
                                      file_size=outfile.__sizeof__(),
                                      mime_type=outfile.__format__("csv"), caption_text="گزارش پرداخت های شما")

        bot.send_message(doc_message, user_peer, success_callback=success, failure_callback=failure)

    user_peer = update.get_effective_user()
    outfile = open('files/{}.csv'.format(notification['peer_id']), 'wb')
    outcsv = csv.writer(outfile)
    records = session.query(Receipt).join(Message).join(Notification).filter(
        Notification.peer_id == notification['peer_id']).all()
    outcsv.writerows([records])
    bot.upload_file(file="files/{}.csv".format(notification['peer_id']), file_type="file",
                    success_callback=file_upload_success,
                    failure_callback=failure)
    dispatcher.finish_conversation(update)


def ask_time(bot, update):
    bot.respond(update, "سلام. زمان هشدار خود را اعلام کنید:\nنمونه (15:15 20-04-1397)", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["persian_datetime"]), periodic_state),
        MessageHandler(DefaultFilter(), wrong_time),
        CommandHandler(["/start"], conversation_starter)])


def wrong_time(bot, update):
    bot.respond(update, "فرمت وارد شده صحیح نیست مجدد وارد کنید", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["persian_datetime"]), periodic_state),
        MessageHandler(DefaultFilter(), wrong_time),
        CommandHandler(["/start"], conversation_starter)])


def periodic_state(bot, update):
    str_date = update.get_effective_message().text
    notification['date_time'] = jdatetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M")
    general_message = TextMessage("نوع اعلان هشدار")
    btn_list = [TemplateMessageButton("فقط یکبار", "only_once", 0),
                TemplateMessageButton("تکرار شونده", "iterative", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["only_once"]), ask_type),
        MessageHandler(TemplateResponseFilter(keywords=["iterative"]), period_type),
        MessageHandler(DefaultFilter(), wrong_periodic_state),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_periodic_state(bot, update):
    bot.respond(update, "جواب نامناسب", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["only_once"]), ask_type),
        MessageHandler(TemplateResponseFilter(keywords=["iterative"]), period_type),
        MessageHandler(DefaultFilter(), wrong_periodic_state),
        CommandHandler(["/start"], conversation_starter)
    ])


def period_type(bot, update):
    notification['only_once'] = False
    general_message = TextMessage("انتخاب نوع تکرار")
    btn_list = [TemplateMessageButton("روزانه", "daily", 0),
                TemplateMessageButton("هفتگی", "weekly", 0),
                TemplateMessageButton("ماهانه", "monthly", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["daily"]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=["weekly"]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=["monthly"]), ask_iterate_number),
        MessageHandler(DefaultFilter(), wrong_period_type),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_period_type(bot, update):
    bot.respond(update, "جواب نامناسب", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["daily"]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=["weekly"]), ask_iterate_number),
        MessageHandler(TemplateResponseFilter(keywords=["monthly"]), ask_iterate_number),
        MessageHandler(DefaultFilter(), wrong_period_type),
        CommandHandler(["/start"], conversation_starter)
    ])


def ask_iterate_number(bot, update):
    notification['periodic_type'] = update.get_effective_message().text_message
    bot.respond(update, TextMessage("تعداد دفعات تکرار:"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["number"]), ask_type),
        MessageHandler(DefaultFilter(), wrong_iterate_number),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_iterate_number(bot, update):
    bot.respond(update, TextMessage("جواب نامناسب (لطفا عدد وارد کنید)"), success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["number"]), ask_type),
        MessageHandler(DefaultFilter(), wrong_iterate_number),
        CommandHandler(["/start"], conversation_starter)
    ])


def ask_type(bot, update):
    if notification.__contains__('only_once'):
        notification['iterate_number'] = update.get_effective_message().text
    else:
        notification['only_once'] = True
    general_message = TextMessage("انتخاب نوع هشدار")
    btn_list = [TemplateMessageButton("عادی", "normal", 0),
                TemplateMessageButton("بدهی", "debt", 0)]
    message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    bot.respond(update, message, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["normal"]), ask_picture),
        MessageHandler(TemplateResponseFilter(keywords=["debt"]), ask_card_number),
        MessageHandler(DefaultFilter(), wrong_type)])


def wrong_type(bot, update):
    bot.respond(update, "جواب نامناسب", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["normal"]), ask_picture),
        MessageHandler(TemplateResponseFilter(keywords=["debt"]), ask_card_number),
        MessageHandler(DefaultFilter(), wrong_type),
        CommandHandler(["/start"], conversation_starter)])


def ask_card_number(bot, update):
    notification['type'] = "debt"
    bot.respond(update, "شماره کارت فرد مورد نظر را وارد کنید:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["card_number"]), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number),
        CommandHandler(["/start"], conversation_starter)])


def wrong_card_number(bot, update):
    bot.respond(update, "فرمت شماره کارت صحیح نمیباشد:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["card_number"]), ask_amount),
        MessageHandler(DefaultFilter(), wrong_card_number),
        CommandHandler(["/start"], conversation_starter)])


def ask_amount(bot, update):
    notification['card_number'] = update.get_effective_message().text
    bot.respond(update, "مبلغ را به ریال وارد کنید:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["number"]), ask_picture),
        MessageHandler(DefaultFilter(), wrong_amount),
        CommandHandler(["/start"], conversation_starter)
    ])


def wrong_amount(bot, update):
    bot.respond(update, "جواب نامناسب لطفا عدد وارد کنید:", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=pattern["number"]), ask_picture),
        MessageHandler(DefaultFilter(), wrong_amount),
        CommandHandler(["/start"], conversation_starter)
    ])


def ask_picture(bot, update):
    if notification.__contains__('type'):
        notification['money'] = update.get_effective_message().text
    else:
        notification['type'] = "normal"
    bot.respond(update, "تصویر(اختیاری)", success, failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(PhotoFilter(), getting_picture),
                                                                MessageHandler(DefaultFilter(), skip_picture),
                                                                CommandHandler(["/start"], conversation_starter)])


def getting_picture(bot, update):
    notification['file_id'] = update.body.message.file_id
    notification['file_access_hash'] = update.body.message.access_hash
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


def finnish_notification_register(bot, update):
    notification['name'] = update.get_effective_message().text
    db_notification = Notification(notification.get('peer_id'), notification.get('peer_access_hash'),
                                   notification.get('type'), notification.get('card_number'), notification.get('money'),
                                   notification.get('name'), notification.get('file_id'),
                                   notification.get('file_access_hash'))
    session.add(db_notification)

    start_datetime = notification['date_time'].togregorian()
    if notification['only_once'] == False:
        time_delta = time_delta_func(notification['periodic_type'])
        for i in range(int(notification['iterate_number'])):
            message = Message(db_notification, sending_time=(start_datetime + time_delta * i))
            session.add(message)
    else:
        message = Message(db_notification, start_datetime, "adfadf", "adfadfa")
        session.add(message)

    session.commit()

    bot.respond(update, TextMessage("هشدار با موفقیت ثبت شد(نمونه پیام)"), success, failure)
    if db_notification.file_id != None:
        message = PhotoMessage(file_id=db_notification.file_id, access_hash=db_notification.file_access_hash,
                               name="Hoshdar",
                               file_size='11337',
                               mime_type="image/jpeg", caption_text=TextMessage(db_notification.name),
                               file_storage_version=1, thumb=None)

    else:
        message = TextMessage(db_notification.name)
    if db_notification.type == "debt":
        final_message = PurchaseMessage(msg=message, account_number=db_notification.card_number,
                                        amount=db_notification.money,
                                        money_request_type=MoneyRequestType.normal)
    else:
        final_message = message
    bot.respond(update, final_message, purchase_message_success, purchase_message_failure)
    dispatcher.finish_conversation(update)


def time_delta_func(type):
    return {
        'daily': datetime.timedelta(days=1),
        'weekly': datetime.timedelta(weeks=1),
        'monthly': datetime.timedelta(days=30)
    }[type]


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
    purchased_message = session.query(Message).filter(
        Message.response_date == purchase_message_date).filter(
        Message.random_id == random_id).all()[0]
    current_time = datetime.datetime.now()
    receipt = Receipt(purchased_message, current_time, description, status, trace_no)
    session.add(receipt)
    session.commit()
    print("receipt registered in db")


updater.run()
