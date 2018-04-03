from flask import Flask, request
import telebot
from telebot import types
import time

secret = "GUID"
bot = telebot.TeleBot('245704344:AAFRsXlQJA_HMWF6RQ7zdXvjkASHqlnexN0', threaded=False)

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://87cb0950.ngrok.io/{}".format(secret))
#bot.set_webhook(url="https://unvqiclpji.localtunnel.me/{}".format(secret))

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    print("Message")
    return "ok", 200


@bot.message_handler(commands=['start', 'help'])
def startCommand(message):
    bot.send_message(message.chat.id, 'Hi *' + message.chat.first_name + '*!', reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    app.run()