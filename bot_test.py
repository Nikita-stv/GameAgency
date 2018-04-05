from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types
import time
import re

secret = "GUID"
bot = telebot.TeleBot('token', threaded=False)


#-----------------------------------------------------------------------------------------------------
# Webhook

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://24fb3edb.ngrok.io/{}".format(secret))

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
start_time = datetime(2018, 3, 15, 11, 49, 0)  # вручную указанная дата
tasks_id = []


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
        #bot.send_message("@shpak_chann", text="Сообщение от бота")


# -----------------------------------------------------------------------------------------------------
# Функция ответа на команду chat

@bot.message_handler(commands=['chat'])
def start_handler(message):
    chat_id = message.chat.id
    print(bot.get_chat_administrators(chat_id))
    bot.send_message(chat_id, "Задание №1 \n Текст задания.")

# -----------------------------------------------------------------------------------------------------
# Функция ответа на команду test, запрос на подтверждение группы
# получение информации о чате (id, название и тип группы) и об администраторах (статус, id, имя, бот или человек)

@bot.message_handler(commands=['test'])
def test_handler(message):
    command_info = []
    chat_id = message.chat.id
    chat_info = bot.get_chat(chat_id)
    command_info.append(chat_info.id)
    command_info.append(chat_info.title)
    command_info.append(chat_info.type)
    #print(chat_info)
    admins = bot.get_chat_administrators(chat_id)
    for i in admins:
        adm = []
        adm.append(i.status)
        adm.append(i.user.id)
        adm.append(i.user.first_name)
        adm.append(i.user.is_bot)
        command_info.append(adm)
        #print(i)
    print(command_info)
    #bot.send_message(chat_id, "Задание №1 \n Текст задания.")


# -----------------------------------------------------------------------------------------------------
# Функция ответа в канал на текст введенный администратором канала (в самом канале).
# Chat_id = названию канала, канал должен быть ПУБЛИЧНЫМ и иметь валидную ссылку


@bot.channel_post_handler(content_types=['text'])
def channel_handler(message):
    print("up")
    if message.text == "Список команд:":
        markup = types.InlineKeyboardMarkup(row_width=1)
        itembtnA = types.InlineKeyboardButton("Команда A", callback_data="aaa")
        itembtnB = types.InlineKeyboardButton("Команда Б", callback_data="bbb")
        itembtnAp = types.InlineKeyboardButton("+", callback_data="+a")
        itembtnBp = types.InlineKeyboardButton("+", callback_data="+b")

        markup.row(itembtnA, itembtnAp)
        markup.row(itembtnB, itembtnBp)
        bot.send_message(chat_id="@shpak_chann", text="Внимание! Чтобы вступить в команду нажмите кнопку \"+\"\nВыбрать команду можно только один раз!!!", reply_markup=markup)
    #bot.send_message("@shpak_chann", text="Сообщение от бота")


# -----------------------------------------------------------------------------------------------------
# Функция ответа на сообщение с префиксом ".", а также с выводом InlineKeyboard


@bot.message_handler(regexp='^\.')
def text_handler(message):
    chat_id = message.chat.id
    mess_id = message.message_id
    mt = message.text[1:]
    print(mt)
    if mt.lower() == "ответ":
        bot.send_message(chat_id, "Задание №2 \n Текст задания.")
    else:
        bot.send_message(chat_id, "Неверно!")
        time.sleep(2)
        bot.delete_message(chat_id, mess_id+1)

# -----------------------------------------------------------------------------------------------------
# Функция ответа на нажатие Inline Button, а также с выводом InlineKeyboard


@bot.callback_query_handler(func=lambda c:True)
def ans(c):
    cid = c.message.chat.id
    mess = c.message.message_id

    if c.data == "aaa":
        markup = types.InlineKeyboardMarkup(1)
        itembtnA = types.InlineKeyboardButton("Вернуться к заданию", callback_data="start")
        markup.row(itembtnA)
        #bot.edit_message_reply_markup(cid, mess, reply_markup=markup)          # изменить inline-кнопку
        #bot.edit_message_text("Подсказка А", cid, mess, reply_markup=markup)   # изменить текст и inline-кнопку

        callid = c.id
        bot.answer_callback_query(callback_query_id=callid, text="Alarm", show_alert=True)
    elif c.data == "bbb":
        markup = types.InlineKeyboardMarkup(1)
        itembtnA = types.InlineKeyboardButton("Вернуться к заданию", callback_data="start")
        markup.row(itembtnA)
        #bot.edit_message_reply_markup(cid, mess, reply_markup=types.ForceReply())
        #bot.edit_message_text("Подсказка B", cid, mess, reply_markup=markup)

        callid = c.id
        bot.answer_callback_query(callback_query_id=callid, text="Alarm", show_alert=False)
    elif c.data == "start":
        start_handler(c.message)

# ------------------------------------------------------------------------------------------------------




if __name__ == '__main__':
    app.run()
