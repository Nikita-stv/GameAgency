from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types
import time
from db_handler import db_handler
from telegramcalendar import create_calendar
import itertools

secret = "GUID"
bot = telebot.TeleBot('245704344:AAFRsXlQJA_HMWF6RQ7zdXvjkASHqlnexN0', threaded=False)

db = db_handler()


#-----------------------------------------------------------------------------------------------------
# Webhook

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://64d1a6b4.ngrok.io/{}".format(secret))

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200

# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
# Блок с параметрами

progress = {0: 0}
answer = {1: ['кот', 'кошка', 'cat'], 2: ['дуб'], 3: ['рубин', 'изумруд']}  # вручную указанные ответы
tasks = {1: 'Кто такой Матроскин?', 2: 'Какое дерево имеет желуди?', 3: 'Красный или зеленый драгоценный камень.'}

tasks_id = []
games = []
com_mess = []

# -----------------------------------------------------------------------------------------------------
# Декоратор для проверки на административные права

def admin_handler(func):
    def wrapper(arg):
        if arg.from_user.id in db.search_admin():
            return func(arg)
        else:
            bot.reply_to(arg, "Вы не являетесь администратором!")
    return wrapper

# -----------------------------------------------------------------------------------------------------
# Вывод списка игр для текущего администратора

def my_games(chat_id, list_of_games):
    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in list_of_games:
        itembtn = types.InlineKeyboardButton(i[1] + " 🔧", callback_data="ief"+str(i[0]))
        markup.row(itembtn)
    bot.send_message(chat_id, "Списко игр:", reply_markup=markup)

# -----------------------------------------------------------------------------------------------------

# Функция ответа на команду start с выводом InlineKeyboard

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    itembtnA = types.InlineKeyboardButton("A", callback_data="aaa")
    itembtnB = types.InlineKeyboardButton("B", callback_data="bbb")
    markup.row(itembtnA, itembtnB)
    bot.send_message(chat_id, "Задание №1 \n Текст задания.", reply_markup=markup)

@bot.channel_post_handler(func=lambda c:True)
def channel_handler(message):
    print("up")
    bot.send_message(chat_id="@shpak_chann", text="Сообщение от бота")


# -----------------------------------------------------------------------------------------------------

# Вывод списка игр созданных текущим пользователем (администратором)

@bot.message_handler(commands=['my_games'])
@admin_handler
def mygame_handler(message):
    del com_mess[:]
    del games[:]
    chat_id = message.chat.id
    list_of_games = db.query_with_fetchall([message.from_user.id])
    my_games(chat_id, list_of_games)


# ------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['new_game'])
@admin_handler
def new_handler(message):
    del com_mess[:]
    del games[:]
    chat_id = message.chat.id
    mess_id = message.message_id
    bot.send_message(chat_id, "Введите название игры:")
    com_mess.append(mess_id)


# -----------------------------------------------------------------------------------------------------
# Блок для вывода интерактивного календаря для выбора даты игры и обработки ответа пользователя, время начала игры 00:00


current_shown_dates={}
@bot.message_handler(commands=['calendar'])
def get_calendar(message):
    now = datetime.now() #Current date
    chat_id = message.chat.id
    date = (now.year,now.month)
    current_shown_dates[chat_id] = date #Saving the current date in a dict
    markup= create_calendar(now.year,now.month)
    bot.send_message(message.chat.id, "Укажите дату начала игры:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month+=1
        if month>12:
            month=1
            year+=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text("Укажите дату начала игры:", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month-=1
        if month<1:
            month=12
            year-=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text("Укажите дату начала игры:", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        day=call.data[13:]
        date = datetime(int(saved_date[0]),int(saved_date[1]),int(day),0,0,0)

        games.append(str(date))                 # записываем дату проведения во временный список
        games.insert(0, int(time.time()))       # формируем id игры
        games.append(call.from_user.id)         # записываем владельца созданной игры

        markup = types.InlineKeyboardMarkup(row_width=1)
        itembtnA = types.InlineKeyboardButton("Создать", callback_data="create")
        itembtnB = types.InlineKeyboardButton("Ввести заново", callback_data="anew")
        markup.row(itembtnA, itembtnB)
        bot.send_message(chat_id, "Название игры: {}\nКоличество уровней: {}\nДата начала игры: {}".format(games[1], games[2], games[3]),
                         reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass


# -----------------------------------------------------------------------------------------------------
# Запись собраной инф. об игре из временного списка в базу

@bot.callback_query_handler(func=lambda call: call.data == 'create')
def get_day(call):
    db.insert_games(games)
    del games[:]
    chat_id = call.message.chat.id
    print(call.from_user.id)
    list_of_games = db.query_with_fetchall([call.from_user.id])
    my_games(chat_id, list_of_games)

@bot.callback_query_handler(func=lambda call: call.data == 'anew')
def anew(call):
    del com_mess[:]
    del games[:]
    chat_id = call.message.chat.id
    mess_id = call.message.message_id
    bot.send_message(chat_id, "Введите название игры:")
    com_mess.append(mess_id)

# ------------------------------------------------------------------------------------------------------
# Блок вывода информации о выбранной игре


def info(m):
    if m.text == "✏️ изменить":
        print("up")


@bot.callback_query_handler(func=lambda call: call.data[0:3] == 'ief')
def properties(call):
    chat_id = call.message.chat.id
    property = db.query_with_fetchall2([call.data[3:]])[0]
    markup = types.InlineKeyboardMarkup(1)
    btn = types.InlineKeyboardButton("✏️", callback_data="edit"+str(property[0]))
    btn1 = types.InlineKeyboardButton("⬅️", callback_data="back")
    markup.row(btn, btn1)
    bot.send_message(chat_id, "Название игры: *{}*,\nКоличество уровней: *{}*,\nДата начала игры: *{}*".format(property[1], property[2], property[3]), reply_markup=markup, parse_mode="Markdown")

# ------------------------------------------------------------------------------------------------------
# Если нажато "Back", то просто удалить предыдущее сообщение

@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_mess(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    bot.delete_message(chat_id, mess)

# ------------------------------------------------------------------------------------------------------
# Вывод модуля редактирования параметров игру (путем изменения InlineKeyboard)

@bot.callback_query_handler(func=lambda call: call.data[0:5] == 'edit1')
def edit_mess(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    inline_mess = call.inline_message_id
    name = db.query_with_fetchall2([call.data[4:]])[0][1]
    btn = types.InlineKeyboardButton("Редактировать название", callback_data="name" + call.data[4:])
    btn1 = types.InlineKeyboardButton("Добавить описание к игре", callback_data="description" + call.data[4:])
    btn2 = types.InlineKeyboardButton("Изменить дату", callback_data="datetime" + call.data[4:])
    btn3 = types.InlineKeyboardButton("Редактировать уровни", callback_data="levels" + call.data[4:])
    markup = types.InlineKeyboardMarkup(1)
    markup.add(btn, btn1, btn2, btn3)
    #bot.send_message(chat_id, text=name, reply_markup=markup)
    #bot.edit_message_text(chat_id=chat_id, text=name, message_id=mess, reply_markup=markup)
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=mess, inline_message_id=inline_mess, reply_markup=markup)

# ------------------------------------------------------------------------------------------------------
# Переделать с использование lambda: проверка на условие

@bot.message_handler(content_types=['text'])
def set_game_handler(message):
    chat_id = message.chat.id
    mess_id = message.message_id
    if len(com_mess) == 1:
        text = message.text.lower()
        games.append(text)
        bot.send_message(chat_id, "Введите количество уровней:")
        com_mess.append(mess_id)
    elif len(com_mess) == 2:
        text = message.text
        try:
            text = int(text)
            games.append(text)
            get_calendar(message)
            com_mess.append(mess_id)
        except ValueError:
            bot.send_message(chat_id, "Введите количество уровней:")
    elif len(com_mess) == 3:
        del com_mess[:]


# ------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run()

