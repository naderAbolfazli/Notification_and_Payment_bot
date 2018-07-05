import logging


# Config for logger
class Config:
    base_url = "wss://api.bale.ai/v1/bots/"
    bot_token = "0f8c34cd08e81d3604f23f712a095f167dfc37d8"
    request_timeout = 5
    db_message_checking_interval = 60
    database_url = "postgresql://postgres:nader1993@localhost:5432/notification_bot"

    system_local = "fa_IR"
    accepted_datetime_format = "%Y-%m-%d %H:%M"

    resending_max_try = 5
    reuploading_max_try = 5

    use_graylog = True
    graylog_host = "127.0.0.1"
    graylog_port = 12201
    log_level = logging.DEBUG  # DEBUG | INFO | ERROR | WARNING | CRITICAL
    log_facility_name = "python_bale_bot"
    source = "notification_bot"
