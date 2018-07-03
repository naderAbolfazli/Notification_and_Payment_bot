from ai.bale.notification_bot.constant.enum import enum

ResponseValue = enum(
    setup_notification="setup_notification",
    showing_receipts="showing_receipts",
    only_once="only_once",
    iterative="iterative",
    daily="daily",
    weekly="weekly",
    monthly="monthly",
    normal="normal",
    debt="debt",
    no_picture="no_picture"
)
