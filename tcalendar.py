from telebot import types
import calendar
from datetime import datetime

def create_calendar(year,month):
    today = str(datetime.now())
    markup = types.InlineKeyboardMarkup()
    row=[]
    row.append(types.InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data="ignore"))
    markup.row(*row)
    week_days=["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
    row=[]
    for day in week_days:
        row.append(types.InlineKeyboardButton(day,callback_data="ignore"))
    markup.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for day in week:

            if month > int(today[5:7]):
                if (day == 0):
                    row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
                else:
                    row.append(types.InlineKeyboardButton(str(day), callback_data="calendar-day-" + str(day)))
            else:
                if month == int(today[5:7]):
                    if day < int(today[8:10]):
                        row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
                    else:
                        row.append(types.InlineKeyboardButton(str(day), callback_data="calendar-day-" + str(day)))
                else:
                    row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
        markup.row(*row)
    row=[]
    row.append(types.InlineKeyboardButton("<",callback_data="previous-month"))
    row.append(types.InlineKeyboardButton(" ",callback_data="ignore"))
    row.append(types.InlineKeyboardButton(">",callback_data="next-month"))
    markup.row(*row)
    return markup


def create_clock(H=0, M=0):
    if H == 24: H = 0
    if H == -1: H = 23
    if M == 60: M = 0
    if M == -1: M = 59
    H = str(H)
    M = str(M)
    if len(H) == 1: H = '0'+H
    if len(M) == 1: M = '0'+M
    markup = types.InlineKeyboardMarkup(row_width=1)
    btnH = types.InlineKeyboardButton(text=H, callback_data="ignore")
    btnM = types.InlineKeyboardButton(text=M, callback_data="ignore")
    markup.row(btnH, btnM)
    btnHUp = types.InlineKeyboardButton("🔼", callback_data="btnHUp"+H+M)
    btnMUp = types.InlineKeyboardButton("🔼", callback_data="btnMUp"+H+M)
    markup.row(btnHUp, btnMUp)
    btnHDown = types.InlineKeyboardButton("🔽", callback_data="btnHDown"+H+M)
    btnMDown = types.InlineKeyboardButton("🔽", callback_data="btnMDown"+H+M)
    markup.row(btnHDown, btnMDown)
    markup.add(types.InlineKeyboardButton("Далее", callback_data="datetime"+H+M))
    return markup