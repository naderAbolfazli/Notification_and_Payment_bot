import asyncio
import datetime

from balebot.models.base_models import UserPeer
from balebot.models.messages import PhotoMessage, TextMessage, PurchaseMessage
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.updater import Updater
from balebot.utils.util_functions import generate_random_id
from sqlalchemy import cast, Date

from Config import Config
from ai.bale.notification_bot.models.constants import BotMessages, ResponseValue, MimeType, MessageStatus, LogMessage, \
    SendingAttempt, UserData, DefaultPhoto
from ai.bale.notification_bot.utils.logger import Logger
from ai.bale.notification_bot.models.base import Session, engine, Base
from ai.bale.notification_bot.models.message import Message

my_logger = Logger.get_logger()
loop = asyncio.get_event_loop()
updater = Updater(token=Config.bot_token,
                  loop=loop)
bot = updater.bot
dispatcher = updater.dispatcher

Base.metadata.create_all(engine)
session = Session()


def db_pulling():
    my_logger.info(LogMessage.reading_message_db)
    current_time = datetime.datetime.now()
    message_tobe_sent = session.query(Message).filter(Message.sent != MessageStatus.sent).filter(
        # not sent messages
        cast(Message.sending_time, Date) == current_time.date()).filter(
        Message.sending_time < current_time).all()

    for msg in message_tobe_sent:
        my_logger.info(LogMessage.db_has_message_to_send)
        notification = msg.notification
        user_peer = UserPeer(notification.peer_id, notification.peer_access_hash)
        if notification.file_id:
            message = PhotoMessage(file_id=notification.file_id, access_hash=notification.file_access_hash,
                                   name=BotMessages.photo_name,
                                   file_size=notification.file_size,
                                   mime_type=MimeType.image, caption_text=TextMessage(notification.text),
                                   file_storage_version=1, thumb=None)
        else:
            message = TextMessage(notification.text)
        if notification.type == ResponseValue.debt:
            if isinstance(message, TextMessage):
                message = PhotoMessage(file_id=DefaultPhoto.file_id, access_hash=DefaultPhoto.access_hash,
                                       name=BotMessages.photo_name,
                                       file_size=DefaultPhoto.file_size,
                                       mime_type=MimeType.image, caption_text=TextMessage(notification.text),
                                       file_storage_version=1, thumb=None)
            final_message = PurchaseMessage(msg=message, account_number=notification.card_number,
                                            amount=notification.money_amount,
                                            money_request_type=MoneyRequestType.normal)

        else:
            final_message = message
        loop.call_soon(send_message, final_message, user_peer, msg, SendingAttempt.first)
    loop.call_later(Config.db_message_checking_interval, db_pulling)


def send_message(base_message, user_peer, msg, sending_attempt):
    random_id = generate_random_id()
    kwargs = {UserData.random_id: random_id, UserData.db_msg: msg, UserData.base_message: base_message,
              UserData.user_peer: user_peer, UserData.sending_attempt: sending_attempt}
    bot.send_message(base_message, user_peer, random_id=random_id, success_callback=success,
                     failure_callback=failure, kwargs=kwargs)


def success(response, user_data):
    user_data = user_data[UserData.kwargs]
    msg = user_data[UserData.db_msg]
    user_id = user_data[UserData.user_peer].peer_id
    sending_attempt = user_data[UserData.sending_attempt]
    msg.random_id = user_data[UserData.random_id]
    msg.response_date = response.body.date
    msg.sent_time = datetime.datetime.now()
    msg.sent = MessageStatus.sent
    session.commit()
    my_logger.info(LogMessage.successful_sending,
                   extra={UserData.user_id: user_id, UserData.sending_attempt: sending_attempt,
                          UserData.sending_set_time: msg.sending_time, "tag": "info"})


def failure(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_peer = user_data[UserData.user_peer]
    base_message = user_data[UserData.base_message]
    sending_attempt = user_data[UserData.sending_attempt] + 1
    msg = user_data[UserData.db_msg]
    if sending_attempt <= Config.resending_max_try:
        send_message(base_message, user_peer, msg, sending_attempt)
        return
    msg.sent = MessageStatus.failed
    session.commit()
    my_logger.info(LogMessage.failed_sending,
                   extra={UserData.user_peer: user_peer.peer_id, UserData.message_id: msg.id,
                          UserData.message_type: msg.notification.type,
                          UserData.sending_set_time: msg.sending_time, "tag": "info"})


loop.call_soon(db_pulling)

updater.run()
