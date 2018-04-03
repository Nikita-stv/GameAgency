from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types
import time


secret = "GUID"
bot = telebot.TeleBot('245704344:AAFRsXlQJA_HMWF6RQ7zdXvjkASHqlnexN0', threaded=False)


#-----------------------------------------------------------------------------------------------------
# Webhook

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://4b4bdaa8.ngrok.io/{}".format(secret))

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200



#-----------------------------------------------------------------------------------------------------
# Блок с параметрами

progress = {0: 0}
answer = {1: ['кот', 'кошка', 'cat'], 2: ['дуб'], 3: ['рубин', 'изумруд']}        # вручную указанные ответы
tasks = {1: 'Кто такой Матроскин?', 2: 'Какое дерево имеет желуди?', 3: 'Красный или зеленый драгоценный камень.'}
start_time = datetime(2018, 3, 15, 11, 49, 0)       # вручную указанная дата
tasks_id = []


#-----------------------------------------------------------------------------------------------------
# 1.Функция вывода заданий к уровням

def task_of_levels(chat_id, level, message_id):
    if level <= len(tasks):
        title = 'Задание №{}'.format(level)
        text = tasks[level]
        bot.send_message(chat_id, title + "\n" + text)
        if level == 1:
            tasks_id.append(message_id + 1)
    else:
        bot.send_message(chat_id, "Игра закончена!")

#-----------------------------------------------------------------------------------------------------
# 2.Реакция на сообщение с командой /start


@bot.message_handler(commands=['start'])                # инициализация бота
def start_handler(message):
    chat_id = message.chat.id
    time_message = datetime.fromtimestamp(message.date)
    if chat_id not in progress:
        if time_message < start_time:
            bot.send_message(chat_id, 'Еще рано, игра начнется -- {}'.format(start_time))
        else:
            progress[chat_id] = 1
            task_of_levels(chat_id, progress[chat_id], message.message_id)
    else:
        bot.send_message(chat_id, 'Вы уже в игре!')


#-----------------------------------------------------------------------------------------------------
# 3. Обработка ответов и вызов функции формирования задания

@bot.message_handler(regexp='^\.')
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    mess_id = message.message_id
    if chat_id in progress:
        level = progress[chat_id]
        value = answer[level]
        if text[1:] in value:
            #bot.send_message(chat_id, 'Поздравляю, Вы правильно ответили!')
            #tasks_id.append(message.message_id)                              # записываем message_id правильного ответа
            #dm = tasks_id[-1] - tasks_id[0]                                  # определяем есть ли промежуточные сообщения
            #if dm > 1:
            #    for i in range(tasks_id[0]+1, tasks_id[-1]):                 # если да, то удаляем сообщения
            #        bot.delete_message(chat_id, i)                           # между заданием и правильным ответом
            #del tasks_id[0:]                                                 # очишаем список промежут. сообщений
            progress[chat_id] += 1

            tasks_id.append(message.message_id + 2)  # записываем id задания
            task_of_levels(chat_id, progress[chat_id], message.message_id)

        else:
            bot.send_message(chat_id, "Неверно, попробуйте еще!")
            time.sleep(2)
            bot.delete_message(chat_id, mess_id + 1)


#-----------------------------------------------------------------------------------------------------
# 4.Выход из игры

@bot.message_handler(commands=['exit'])
def exit_handler(message):
    chat_id = message.chat.id
    if chat_id in progress:
        del progress[chat_id]
        bot.send_message(chat_id, 'Вы вышли из игры!')


#-----------------------------------------------------------------------------------------------------
@bot.channel_post_handler(content_types=['text'])
def channel_handler(message):
    print("up")
    bot.send_message(chat_id="@test_channel", text="Сообщение от бота")
    #bot.send_message("@shpak_chann", text="Сообщение от бота")

#-----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run()
