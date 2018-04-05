import telebot
from telebot import types
from datetime import datetime


token = "token"
bot = telebot.TeleBot(token)

bot.get_updates(allowed_updates=[""])       # Получать весь массив параметров обновления

#-----------------------------------------------------------------------------------------------------
# Блок с параметрами

progress = {0: 0}
answer = {1: ['кот', 'кошка', 'cat'], 2: ['дуб'], 3: ['рубин', 'изумруд']}        # вручную указанные ответы
tasks = {1: 'Кто такой Матроскин?', 2: 'Какое дерево имеет желуди?', 3: 'Красный или зеленый драгоценный камень.'}
start_time = datetime(2018, 3, 15, 11, 49, 0)       # вручную указанная дата
tasks_id = []


#-----------------------------------------------------------------------------------------------------
# 1.Вывод заданий к уровням
# 1.1 удаление сообщений

def task_of_levels(chat_id, level, message_id):
    title = 'Задание №{}'.format(level)
    text = tasks[level]
    bot.send_message(chat_id, title)
    markup = types.ForceReply()
    bot.send_message(chat_id, text, reply_markup=markup)
    if level == 1:
        tasks_id.append(message_id + 2)
    #print(tasks_id)

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
            task_of_levels(chat_id, progress[chat_id], message.message_id)
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
        if text in value:
            bot.send_message(chat_id, 'Поздравляю, Вы правильно ответили!')
            tasks_id.append(message.message_id)                              # записываем message_id правильного ответа
            dm = tasks_id[-1] - tasks_id[0]                                  # определяем есть ли промежуточные сообщения
            if dm > 1:
                for i in range(tasks_id[0]+1, tasks_id[-1]):                 # если да, то удаляем сообщения
                    bot.delete_message(chat_id, i)                           # между заданием и правильным ответом
            del tasks_id[0:]                                                 # очишаем список промежут. сообщений
            tasks_id.append(message.message_id + 3)                          # записываем id задания
            progress[chat_id] += 1
            task_of_levels(chat_id, progress[chat_id], message.message_id)

        else:
            bot.send_message(chat_id, "Неверно, попробуйте еще!")
            task_of_levels(chat_id, progress[chat_id], message.message_id)


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

