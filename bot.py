import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("💎 Купити TON"), KeyboardButton("💵 Купити USDT"))
    markup.row(KeyboardButton("👤 Профіль"), KeyboardButton("⭐ Відгуки"))
    markup.row(KeyboardButton("🛠 Служба підтримки"), KeyboardButton("🧮 Калькулятор"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привіт! Вибери дію:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text == "💎 Купити TON":
        bot.send_message(message.chat.id, "Купівля TON...")
    elif message.text == "💵 Купити USDT":
        bot.send_message(message.chat.id, "Купівля USDT...")
    elif message.text == "👤 Профіль":
        bot.send_message(message.chat.id, "Твій профіль...")
    elif message.text == "⭐ Відгуки":
        bot.send_message(message.chat.id, "Відгуки...")
    elif message.text == "🛠 Служба підтримки":
        bot.send_message(message.chat.id, "Підтримка...")
    elif message.text == "🧮 Калькулятор":
        bot.send_message(message.chat.id, "Калькулятор...")

bot.infinity_polling()
