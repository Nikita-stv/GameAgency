from datetime import datetime, date, time as dtime
from flask import Flask, request
import telebot
from telebot import types
import time
from db_handler import db_handler
from alchemy import Admins, Levels, Gameplay, Games
from tcalendar import create_calendar, create_clock
from configparser import ConfigParser
from telebot import apihelper
import string
import random
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

apihelper.proxy = {'https':'http://127.0.0.1:1080'}


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.
#--------------------------------------------------------------------------------------------------

def read_config(filename='config.ini', section='bot'):
    parser = ConfigParser()
    parser.read(filename)
    cf = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            cf[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return cf

#-----------------------------------------------------------------------------------------------------
cf = read_config()

bot = telebot.TeleBot(cf['token'], threaded=False)
db = db_handler()

db_admins = Admins
db_levels = Levels
db_gameplay = Gameplay
db_games = Games
#db_session = session
#-----------------------------------------------------------------------------------------------------
# Webhook

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="{}/{}".format(cf['url'], cf['secret']))

app = Flask(__name__)

@app.route('/{}'.format(cf['secret']), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200

# -----------------------------------------------------------------------------------------------------


engine = create_engine('mysql+mysqlconnector://root:Stavstat12@127.0.0.1:3306/ga2')
Session = sessionmaker(bind=engine)                           # Инициализация сессии
session = Session()



# -----------------------------------------------------------------------------------------------------
# Блок с параметрами

games = []
id_game = 0


# -----------------------------------------------------------------------------------------------------
#Работы с КАНАЛОМ

@bot.channel_post_handler(func=lambda c:True)
def channel_handler(message):
    print("up")
    bot.send_message(chat_id="@shpak_chann", text="Сообщение от бота")

# -----------------------------------------------------------------------------------------------------
# Декоратор для проверки на административные права

def admin_handler(func):
    def wrapper(arg):
        if arg.from_user.id in list(map(lambda x: x[0], session.query(db_admins.t_id))):
            return func(arg)
        else:
            bot.reply_to(arg, "Вы не являетесь администратором!")
    return wrapper

# -----------------------------------------------------------------------------------------------------
# Функция ответа на команду start с выводом InlineKeyboard. Пример.

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    itembtnA = types.InlineKeyboardButton("A", callback_data="aaa")
    itembtnB = types.InlineKeyboardButton("B", callback_data="bbb")
    markup.row(itembtnA, itembtnB)
    bot.send_message(chat_id, "Задание №1 \n Текст задания.", reply_markup=markup)


# ------------------------------------------------------------------------------------------------------
# Формирование новой игры


def setdescription(message):
    chat_id = message.chat.id
    description = message.text
    new_game.description = description
    sent = bot.send_message(chat_id=chat_id, text="Введите количество уровней:")
    bot.register_next_step_handler(message=sent, callback=get_calendar)

def setname(message):
    chat_id = message.chat.id
    name = message.text
    new_game.name = name
    sent = bot.send_message(chat_id, "Введите описание игры:")
    bot.register_next_step_handler(message=sent, callback=setdescription)

@bot.message_handler(commands=['new_game'])
@admin_handler
def new_handler(message):
    global new_game
    new_game = db_games('None', 'None', 0, '2018-05-24 16:00:00', 0, 'None')
    session.add(new_game)
    chat_id = message.chat.id
    sent = bot.send_message(chat_id, "Введите название игры:")
    bot.register_next_step_handler(message=sent, callback=setname)


# -----------------------------------------------------------------------------------------------------
# Блок для вывода интерактивного календаря для выбора даты игры и обработки ответа пользователя, время начала игры 00:00

current_shown_dates={}
def get_calendar(message, edit=False):
    number_of_levels = message.text
    new_game.number_of_levels = number_of_levels
    now = datetime.now()
    chat_id = message.chat.id
    mess = message.message_id
    date = (now.year,now.month)
    current_shown_dates[chat_id] = date #Saving the current date in a dict
    markup = create_calendar(now.year,now.month)
    if edit == False:
        bot.send_message(text="Укажите дату начала игры:", chat_id=message.chat.id, reply_markup=markup)
    else:
        bot.edit_message_text(text="Укажите дату начала игры:", chat_id=message.chat.id, message_id=mess, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
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
        bot.edit_message_text(text="Укажите дату начала игры:", chat_id=chat_id, message_id=mess, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
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
        bot.edit_message_text(text="Укажите дату начала игры:", chat_id=chat_id, message_id=mess, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass


@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    chat_id = call.message.chat.id
    global day
    day = call.data[13:]
    bot.edit_message_text(text="🕒 *Укажите время начала игры* 🕒", chat_id=chat_id, message_id=call.message.message_id,
                              reply_markup=create_clock(), parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data[0:8] == 'datetime')
def datetimes(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if (saved_date is not None):
        d = date(int(saved_date[0]), int(saved_date[1]), int(day))
        t = dtime(int(call.data[8:10]), int(call.data[10:]))
        dt = datetime.combine(d, t)
#        if len(games) > 1:  # формирование даты для новой игры
#            games.append(str(dt))  # записываем дату проведения во временный список
#            games.insert(0, int(time.time()))  # формируем id игры
#            games.append(call.from_user.id)  # записываем владельца созданной игры
#            games.append(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))  # уникальный код игры
#            markup = types.InlineKeyboardMarkup(row_width=1)
#            itembtnA = types.InlineKeyboardButton("Создать", callback_data="create")
#            itembtnB = types.InlineKeyboardButton("Ввести заново", callback_data="anew")
#            markup.row(itembtnA, itembtnB)
#            bot.edit_message_text(
#                text="Название игры: *{}*\nОписание: *{}.*\nКоличество уровней: *{}*\nДата начала игры: *{}*\nКод игры: *{}*".format(
#                    games[1], games[2], games[3], games[4], games[6]), chat_id=chat_id, message_id=call.message.message_id,
#                reply_markup=markup, parse_mode="Markdown")
#            bot.answer_callback_query(call.id, text="")
#        else:  # редактирование даты игры
#            global param
#            param = 'egdate'
#            update_game(message=call.message, date=dt)
#            del games[:]
        new_game.date = str(dt)
        new_game.owner = call.from_user.id
        new_game.code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))  # уникальный код игры
        markup = types.InlineKeyboardMarkup(row_width=1)
        itembtnA = types.InlineKeyboardButton("Создать", callback_data="create")
        itembtnB = types.InlineKeyboardButton("Ввести заново", callback_data="anew")
        markup.row(itembtnA, itembtnB)
        bot.edit_message_text(
            text="Название игры: *{}*\nОписание: *{}.*\nКоличество уровней: *{}*\nДата начала игры: *{}*\nКод игры: *{}*"
            .format(new_game.name, new_game.description, new_game.number_of_levels, new_game.date, new_game.code),
            chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id, text="")

    else:
        # Do something to inform of the error
        pass

# -----------------------------------------------------------------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data[0:6] == 'btnHUp')
def hour_up(call):
    chat_id = call.message.chat.id
    hour = int(call.data[6:8])+1
    minute = int(call.data[8:])
    bot.edit_message_text(text="🕒 *Укажите время начала игры* 🕒", chat_id=chat_id, message_id=call.message.message_id,
                          reply_markup=create_clock(H=hour, M=minute), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data[0:8] == 'btnHDown')
def hour_down(call):
    chat_id = call.message.chat.id
    hour = int(call.data[8:10])-1
    minute = int(call.data[10:])
    bot.edit_message_text(text="🕒 *Укажите время начала игры* 🕒", chat_id=chat_id, message_id=call.message.message_id,
                          reply_markup=create_clock(H=hour, M=minute), parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data[0:6] == 'btnMUp')
def minute_up(call):
    chat_id = call.message.chat.id
    hour = int(call.data[6:8])
    minute = int(call.data[8:]) + 1
    bot.edit_message_text(text="🕒 *Укажите время начала игры* 🕒", chat_id=chat_id, message_id=call.message.message_id,
                          reply_markup=create_clock(H=hour, M=minute), parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data[0:8] == 'btnMDown')
def minute_down(call):
    chat_id = call.message.chat.id
    hour = int(call.data[8:10])
    minute = int(call.data[10:]) - 1
    bot.edit_message_text(text="🕒 *Укажите время начала игры* 🕒", chat_id=chat_id, message_id=call.message.message_id,
                          reply_markup=create_clock(H=hour, M=minute), parse_mode="Markdown")

# -----------------------------------------------------------------------------------------------------
# Запись собраной инф. об игре из временного списка в базу


@bot.callback_query_handler(func=lambda call: call.data == 'create')
def set_game(call):
    current_game = new_game
    session.commit()
    chat_id = call.message.chat.id
    mess = call.message.message_id
    for i in range(int(current_game.number_of_levels)):
        session.add(db_levels(current_game.id, i+1, 'None', 'None', 'None', 'None'))
    session.commit()
    #list_of_games = db.sample('owner', call.from_user.id)
    list_of_games = session.query(db_games).filter_by(owner=call.from_user.id).all()
    my_games(chat_id, list_of_games, mess=mess, send=False)


@bot.callback_query_handler(func=lambda call: call.data == 'anew')
def anew(call):
    del games[:]
    chat_id = call.message.chat.id
    sent = bot.edit_message_text(text="Введите название игры:", chat_id=chat_id,message_id=call.message.message_id)
    bot.register_next_step_handler(message=sent, callback=setname)


# -----------------------------------------------------------------------------------------------------
# Вывод списка игр созданных текущим пользователем (администратором)

def my_games(chat_id, list_of_games, send=True, mess=None):
    markup = types.InlineKeyboardMarkup(row_width=3)
    #print(list())
    for i in list_of_games:
        itembtn = types.InlineKeyboardButton(i.name + " 🔧", callback_data="edit1" + str(i.id))
        markup.row(itembtn)
    if send:
        bot.send_message(chat_id, "🎲 Список игр 🎲", reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=chat_id, text="🎲 Список игр 🎲", message_id=mess, reply_markup=markup)


@bot.message_handler(commands=['my_games'])
@admin_handler
def mygame_handler(message):
    chat_id = message.chat.id
    #list_of_games = db.sample('owner', message.from_user.id)
    list_of_games = session.query(db_games).filter_by(owner=message.from_user.id).all()
    my_games(chat_id, list_of_games)


# ------------------------------------------------------------------------------------------------------
# Если нажато "Del", то удалить выбранную игру

@bot.callback_query_handler(func=lambda call: call.data[0:3] == 'del')
def del_game(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    #db.delete('del_game', call.data[3:])
    #db.delete('del_all_lev', call.data[3:])
    session.query(db_games).filter_by(id=call.data[3:]).delete()
    session.query(db_levels).filter_by(game_id=call.data[3:]).delete()
    session.commit()
    #list_of_games = db.sample('owner', call.from_user.id)
    list_of_games = session.query(db_games).filter_by(owner=call.from_user.id).all()
    #my_games(chat_id, list_of_games, send=False, mess=mess)
    my_games(chat_id, list_of_games)

# ------------------------------------------------------------------------------------------------------
# Если нажато "Back", то изменить текущее сообщение на предыдущее

@bot.callback_query_handler(func=lambda call: call.data[0:5] == 'back1')
def back_mess(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    list_of_games = session.query(db_games).filter_by(owner=call.from_user.id).all()
    #my_games(chat_id, list_of_games, send=False, mess=mess)
    my_games(chat_id, list_of_games)

# ------------------------------------------------------------------------------------------------------
# Интерфейс игр

@bot.callback_query_handler(func=lambda call: call.data[0:5] == 'edit1')
def edit_mess(call):
    bot.answer_callback_query(callback_query_id=call.id, text="Готово!")
    chat_id = call.message.chat.id
    mess = call.message.message_id
    btn = types.InlineKeyboardButton("📣", callback_data="egname" + call.data[5:])
    btn1 = types.InlineKeyboardButton("📝", callback_data="egdscr" + call.data[5:])
    btn2 = types.InlineKeyboardButton("📅", callback_data="egdate" + call.data[5:])
    btn3 = types.InlineKeyboardButton("📚", callback_data="levels" + call.data[5:])
    btn4 = types.InlineKeyboardButton("⬅️", callback_data="back" + call.data[5:])
    btn5 = types.InlineKeyboardButton("❗🗑❗️", callback_data="del" + call.data[5:])
    markup = types.InlineKeyboardMarkup(1)
    markup.row(btn, btn1, btn2, btn3)
    markup.row(btn4, btn5)
    #property = db.sample('games', call.data[4:])[0]
    property = session.query(db_games).filter_by(id=call.data[5:]).first()
    bot.edit_message_text(text="📣 *Название игры*\n{}\n\n📝 *Описание*\n{}\n\n📅 *Дата начала игры*\n{}\n\n"
                               "📚 *Количество уровней*\n{}\n\n🎛 *Код игры*\n{}\n"
                               "--------------------------------------------------\n⬇️*Нажми, чтобы изменить*⬇️"
                               .format(property.name, property.description, property.date, property.number_of_levels, property.code),
                          chat_id=chat_id, message_id=mess, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)

# ------------------------------------------------------------------------------------------------------
# Редактирование игр


def update_name(message):
    chat_id = message.chat.id
    btn = types.InlineKeyboardButton("Далее", callback_data="edit1" + str(id_game))
    markup = types.InlineKeyboardMarkup(1)
    markup.add(btn)
    game = session.query(db_games).filter_by(id=id_game).first()
    game.name = message.text
    session.commit()
    bot.send_message(chat_id=chat_id, text=message.text, reply_markup=markup)


def update_dscr(message):
    chat_id = message.chat.id
    btn = types.InlineKeyboardButton("Далее", callback_data="edit1" + str(id_game))
    markup = types.InlineKeyboardMarkup(1)
    markup.add(btn)
    game = session.query(db_games).filter_by(id=id_game).first()
    game.description = message.text
    session.commit()
    bot.send_message(chat_id=chat_id, text=message.text, reply_markup=markup)


# Редактирование имени и описания игры игр
@bot.callback_query_handler(func=lambda call: call.data[0:6] in ['egname', 'egdscr'])
def update_param(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    global id_game, param
    param = call.data[0:6]
    id_game = int(call.data[6:])
    sent = bot.edit_message_text(text="Введите новое значение*", chat_id=chat_id, message_id=mess, reply_markup=None)
    if param == 'egname':
        bot.register_next_step_handler(message=sent, callback=update_name)
    else:
        bot.register_next_step_handler(message=sent, callback=update_dscr)


# Изменение даты игры
@bot.callback_query_handler(func=lambda call: call.data[0:6] == 'egdate')
def update_day(call):
    global id_game
    id_game = int(call.data[6:])
    get_calendar(call.message, edit=True)


# ------------------------------------------------------------------------------------------------------
# Список уровней !!!

@bot.callback_query_handler(func=lambda call: call.data[0:6] == 'levels')
def edit_levels(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    markup = types.InlineKeyboardMarkup(row_width=5)
    #levels = db.select_levels([int(call.data[6:16])])
    levels = session.query(db_levels).filter_by(game_id=int(call.data[6:16])).all()
    lev = ''
    btns=[]
    for i in levels:
        itembtn = types.InlineKeyboardButton(i.sn, callback_data="elevel" + str(i.id))
        btns.append(itembtn)
        t = '%s. %s\n' %(i.sn, i.header)
        lev+=t
    markup.add(*btns)
    btn = types.InlineKeyboardButton("🇨🇭", callback_data="addlev" + call.data[6:])
    btn1 = types.InlineKeyboardButton("⬅️", callback_data="edit1" + call.data[6:])
    markup.row(btn1, btn)
    bot.edit_message_text(text="📚*Уровни*📚\n\n" + lev, chat_id=chat_id, message_id=mess, reply_markup=markup, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data[0:6] == 'elevel')
def edit_level(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    markup = types.InlineKeyboardMarkup(row_width=5)
    #level = db.select_level([int(call.data[6:])])
    level = session.query(db_levels).filter_by(id=int(call.data[6:])).first()
    itembtn  = types.InlineKeyboardButton(text="🏷", callback_data="elhead" + str(level.id))
    itembtn1 = types.InlineKeyboardButton(text="📕", callback_data="eltask" + str(level.id))
    itembtn2 = types.InlineKeyboardButton(text="🔑", callback_data="elansw" + str(level.id))
    itembtn3 = types.InlineKeyboardButton(text="💡", callback_data="eletip" + str(level.id))
    itembtn4 = types.InlineKeyboardButton(text="⬅️", callback_data="levels" + str(level.game_id))
    itembtn5 = types.InlineKeyboardButton(text="❗🗑❗", callback_data="le_del" + str(level.game_id) + str(level.id))
    markup.add(itembtn, itembtn1, itembtn2, itembtn3)
    markup.add(itembtn4, itembtn5)
    bot.edit_message_text(text="🏷 *Название уровня*\n{}\n\n📕 *Задание*\n{}\n\n🔑 *Ответ*\n{}\n\n💡 *Подсказка*\n{}"
                               "\n--------------------------------------------------\n⬇️*Нажми, чтобы изменить*⬇️"
                               .format(str(level.header),str(level.task),str(level.answer),str(level.tip)),
                          chat_id=chat_id, message_id=mess, reply_markup=markup, parse_mode="markdown")


# ------------------------------------------------------------------------------------------------------
# Редактирование параметров уровня

def update_level(message):
    chat_id = message.chat.id
    db.update_game(param=param, value=message.text, id=id_level)
    btn = types.InlineKeyboardButton("Далее", callback_data="elevel" + id_level)
    markup = types.InlineKeyboardMarkup(1)
    markup.add(btn)
    bot.send_message(chat_id=chat_id, text=message.text, reply_markup=markup)


# Изменение параметров уровня
@bot.callback_query_handler(func=lambda call: call.data[0:6] in ['elhead', 'eltask', 'elansw', 'eletip'])
def update_header(call):
    chat_id = call.message.chat.id
    mess = call.message.message_id
    global id_level, param
    param = call.data[0:6]
    id_level = call.data[6:]
    sent = bot.edit_message_text(text="Введите новое значение", chat_id=chat_id, message_id=mess, reply_markup=None)
    bot.register_next_step_handler(message=sent, callback=update_level)

# ------------------------------------------------------------------------------------------------------
# удаление уровня

@bot.callback_query_handler(func=lambda call: call.data[0:6] == 'le_del')
def del_level(call):
    db.delete('del_level', call.data[16:])
    num = db.sample('sn', call.data[6:16])
    for i in range(len(num)):
        db.update_game('sn', i+1, num[i][0])
    db.update_game('nol', len(num), call.data[6:16])
    edit_levels(call)

# добавление уровня

@bot.callback_query_handler(func=lambda call: call.data[0:6] == 'addlev')
def add_level(call):
    num = db.sample('sn', call.data[6:])
    db.add_level(call.data[6:], len(num) + 1)
    db.update_game('nol', len(num)+1, call.data[6:])
    edit_levels(call)


# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
#

def level(message):
    chat_id = message.chat.id
    answer = message.text
    print(answer)


#@bot.callback_query_handler(func=lambda f: f)
def play(message):
    code = message.text
    chat_id = message.chat.id
    game = db.sample('code', code)
    bot.clear_step_handler(message)
    print(game)
    if game:
        bot.send_message(text="{} \n\n{}".format(game[0][1], game[0][2]), chat_id=chat_id)
        levels = db.select_levels([game[0][0]])
        gp_for_chat = db.gameplay_req([game[0][0], chat_id])
        if gp_for_chat:
            current_level = gp_for_chat[0][2]
        else:
            db.gameplay_ins(game[0][0], chat_id, 1)
            current_level = 1
        sent = bot.send_message(text="{} \n\n{}".format(levels[current_level - 1][3], levels[current_level - 1][4]),
                                chat_id=chat_id)
        bot.register_next_step_handler(message=sent, callback=level)
    else:
        sent = bot.send_message(text="🎛 ВВЕДИТЕ КОД ИГРЫ 🎛", chat_id=chat_id)
        bot.register_next_step_handler(message=sent, callback=play)


@bot.message_handler(commands=['play'])
def play_handler(message):
    chat_id = message.chat.id
    sent = bot.send_message(text="🎛 ВВЕДИТЕ КОД ИГРЫ 🎛", chat_id=chat_id)
    bot.register_next_step_handler(message=sent, callback=play)

# ------------------------------------------------------------------------------------------------------





if __name__ == '__main__':
    app.run()

