from ai.bale.notification_bot.constant.enum import enum

Pattern = enum(
    persian_datetime="^(139[7-9]|140[0-9])-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|30) ([0-1][0-9]|2[0-3]):[0-5][0-9]$",
    card_number="^[0-9]{16}$",
    number="^[0-9]+",
    weekday="^[0-6]$",
    month_day="^[1-2][0-9]|[1-9]|30$",
    year_day="^[0-2][0-9][0-9]|3[0-5][0-9]|36[0-5]$",
)
