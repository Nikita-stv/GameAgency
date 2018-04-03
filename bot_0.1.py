import telebot
from telebot import types
from datetime import datetime


token = "245704344:AAFRsXlQJA_HMWF6RQ7zdXvjkASHqlnexN0"
bot = telebot.TeleBot(token)

bot.get_updates(allowed_updates=[""])       # Получать весь массив параметров обновления

#-----------------------------------------------------------------------------------------------------

progress = {0: 0}
answer = {1: ['кот', 'кошка', 'cat'], 2: ['береза', 'дуб'], 3: ['рубин', 'изумруд']}        # вручную указанные ответы
tasks = {1: 'Кто такой Матроскин?', 2: 'Какое дерево имеет желуди?', 3: 'Красный или зеленый драгоценный камень.'}
start_time = datetime(2018, 3, 15, 11, 49, 0)       # вручную указанная дата

#-----------------------------------------------------------------------------------------------------
# 1.Вывод заданий к уровням

def task_of_levels(chat_id, level):
    title = 'Задание №{}'.format(level)
    text = tasks[level]
    bot.send_message(chat_id, title)
    #markup = types.InlineKeyboardMarkup()
    #itembtn1 = types.InlineKeyboardButton("Ответить", callback_data="test")
    #markup.row(itembtn1)
    bot.send_message(chat_id, text)


#-----------------------------------------------------------------------------------------------------
# 2.Реакция на сообщение с командой /start


@bot.message_handler(commands=['start'])                # инициализация бота
def start_handler(message):
    chat_id = message.chat.id
    time_message = datetime.fromtimestamp(message.date)
    if chat_id not in progress:
        if time_message < start_time:
            bot.send_message(chat_id, 'Еще рано, игра начнется {}'.format(start_time))
        else:
            progress[chat_id] = 1
            task_of_levels(chat_id, progress[chat_id])
    else:
        bot.send_message(chat_id, 'Вы уже в игре!')


#-----------------------------------------------------------------------------------------------------
# 3.Отправка заданий для 2+ уровней

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    if chat_id in progress:
        level = progress[chat_id]
        value = answer[level]
        print(value)
        if text in value:
            bot.send_message(chat_id, 'Поздравляю, Вы правильно ответили!')
            progress[chat_id] += 1
            task_of_levels(chat_id, progress[chat_id])
        else:
            bot.send_message(chat_id, "Неверно, попробуйте еще!")



#-----------------------------------------------------------------------------------------------------
# 4.Выход из игры

@bot.message_handler(commands=['exit'])
def exit_handler(message):
    chat_id = message.chat.id
    if chat_id in progress:
        del progress[chat_id]
        bot.send_message(chat_id, 'Вы вышли из игры!')

#-----------------------------------------------------------------------------------------------------





bot.polling()

