from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types
import time
from db_handler import db_handler
from telegramcalendar import create_calendar
from configparser import ConfigParser


#--------------------------------------------------------------------------------------------------

def read_config(filename='config.ini', section='bot'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
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
#Работы с КАНАЛОМ

@bot.channel_post_handler(func=lambda c:True)
def channel_handler(message):
    print("up")
    bot.send_message(chat_id="@shpak_chann", text="Сообщение от бота")

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
# -----------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------
# Декоратор для проверки на административные права

def admin_handler(func):
    def wrapper(arg):
        if arg.from_user.id in db.search_admin():
            return func(arg)
        else:
            bot.reply_to(arg, "Вы не являетесь администратором!")
    return wrapper














