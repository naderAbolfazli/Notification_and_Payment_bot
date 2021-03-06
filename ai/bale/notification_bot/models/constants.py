class Command:
    start = "/start"


class MessageButtonAction:
    default = 0


class MimeType:
    image = "image/jpeg"
    csv = "text/csv"
    xlsx = "application / vnd.openxmlformats - officedocument.spreadsheetml.sheet"


class Attr:
    peer_id = "peer_id"
    user_id = "user_id"
    peer_access_hash = "peer_access_hash"
    file_id = "file_id"
    file_access_hash = "file_access_hash"
    file_size = "file_size"
    date_time = "date_time"
    iterate_number = "iterate_number"
    periodic_type = "periodic_type"
    type = "type"
    card_number = "card_number"
    money_amount = "money_amount"
    text = "text"
    value = "value"
    url = "url"
    payer = "payer"
    receiver = "receiver"
    description = "description"


class BotMessages:
    pls_use_start = "لطفا از دستور 'start/' استفاده کنید"
    service_selection = "انتخاب سرویس"
    setup_notification = "تنظیم هشدار"
    showing_receipts = "مشاهده پرداخت ها"
    receipts_report = "گزارش پرداخت های شما"
    ask_time = "زمان هشدار خود را اعلام کنید:\nنمونه (15:15 20-04-1397)"
    wrong_format = "فرمت وارد شده صحیح نیست مجدد وارد کنید"
    periodic_state_selection = "نوع اعلان هشدار"
    only_once = "فقط یکبار"
    iterative = "تکرار شونده"
    wrong_answer = "جواب نامناسب"
    periodic_type_selection = "انتخاب نوع تکرار"
    daily = "روزانه"
    weekly = "هفتگی"
    monthly = "ماهانه"
    iterate_number_selection = "تعداد دفعات تکرار:"
    wrong_answer_pls_number = "جواب نامناسب (لطفا عدد وارد کنید)"
    notification_type_selection = "انتخاب نوع هشدار"
    normal = "عادی"
    debt = "بدهی"
    card_number_entering = "شماره کارت فرد مورد نظر را وارد کنید:"
    wrong_card_number = "فرمت شماره کارت صحیح نمیباشد:"
    amount_entering = "مبلغ را به ریال وارد کنید:"
    picture_request = "تصویر(اختیاری)"
    notification_text_entering = "متن هشدار:"
    wrong_answer_pls_text = "جواب نامناسب. لطفا متن وارد کنید"
    no_picture_needed = "بدون عکس"
    successful_notification_registering = "هشدار با موفقیت ثبت شد"
    photo_name = "هشدار"


class Pattern:
    persian_datetime = "^(139[7-9]|140[0-9])-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|30) ([0-1][0-9]|2[0-3]):[0-5][0-9]$"
    card_number = "^[0-9]{16}$"
    number = "^[0-9]+"
    weekday = "^[0-6]$"
    month_day = "^[1-2][0-9]|[1-9]|30$"
    year_day = "^[0-2][0-9][0-9]|3[0-5][0-9]|36[0-5]$"


class ResponseValue:
    setup_notification = "setup_notification"
    showing_receipts = "showing_receipts"
    only_once = "only_once"
    iterative = "iterative"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    normal = "normal"
    debt = "debt"
    no_picture = "no_picture"


class LogMessage:
    db_has_message_to_send = "there are some message to send"
    reading_message_db = "reading from messages db"
    successful_sending = "successful sending of message:"
    failed_sending = "failed sending of message:"
    successful_report_upload = "successful receipt report uploading"
    failed_report_upload = "failure receipt report uploading"
    successful_report_sending = "successful receipt report sending"
    failed_report_sending = "failure receipt report sending"
    registering_receipt = "receipt registered successfully"
    notification_registering = "notification registered successfully"
    successful_step_message_sending = "successful step message sending"
    failed_step_message_sending = "failure step message sending"


class TransferInfo:
    isExpenditure = 1
    payer = 2
    description = 4
    date = 9
    status = 10
    msgUID = 6
    receiver = 7
    traceNo = 12
    success_status = "SUCCESS"


class MessageStatus:
    sent = 1
    notSent = 0
    failed = -1


class SendingAttempt:
    first = 1


class MsgUID:
    random_id = 0
    date = 1


class UserData:
    ask_picture = "ask_picture"
    message_type = "message_type"
    message_id = "message_id"
    sending_set_time = "sending_set_time"
    base_message = "base_message"
    db_msg = "db_msg"
    random_id = "random_id"
    sending_attempt = "sending_attempt"
    kwargs = "kwargs"
    user_id = "user_id"
    user_peer = "user_peer"
    step_name = "step_name"
    message = "message"
    attempt = "attempt"
    report_attempt = "report_attempt"
    doc_message = "doc_message"
    file_url = "file_url"


class Value:
    text = "text"
    value = "value"


class Step:
    finnish_notification_register = "finnish_notification_register"
    wrong_name_response = "wrong_name_response"
    ask_text = "ask_text"
    getting_picture = "getting_picture"
    wrong_picture = "wrong_picture"
    wrong_amount = "wrong_amount"
    ask_amount = "ask_amount"
    wrong_card_number = "wrong_card_number"
    ask_card_number = "ask_card_number"
    wrong_type = "wrong_type"
    ask_type = "ask_type"
    wrong_iterate_number = "wrong_iterate_number"
    ask_iterate_number = "ask_iterate_number"
    wrong_period_type = "wrong_period_type"
    period_type = "period_type"
    wrong_periodic_state = "wrong_periodic_state"
    periodic_state = "periodic_state"
    wrong_time = "wrong_time"
    ask_time = "ask_time"
    conversation_starter = "conversation_starter"


class DefaultPhoto:
    file_id = -4274813247859260413
    access_hash = 1471278867
    file_size = 41430
