import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ForceReply

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== КУРСИ (міняй тут) =====
TON_RATE = 72.3
USDT_RATE = 41.5
# =============================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("💎 Купити TON"), KeyboardButton("💵 Купити USDT"))
    markup.row(KeyboardButton("👤 Профіль"), KeyboardButton("⭐ Відгуки"))
    markup.row(KeyboardButton("🛠 Служба підтримки"), KeyboardButton("🧮 Калькулятор"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привіт! Вибери дію:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💎 Купити TON")
def buy_ton(message):
    msg = bot.send_message(
        message.chat.id,
        f"💱 На данный момент курс TON: {TON_RATE} грн\nВведите количество TON, которое вы хотите заказать.",
        reply_markup=ForceReply()
    )
    bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_amount(message):
    try:
        amount = float(message.text)
        total = amount * TON_RATE
        bot.send_message(message.chat.id, f"✅ Ви хочете купити {amount} TON\nСума: {total:.2f} грн", reply_markup=main_menu())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введіть число!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💵 Купити USDT")
def buy_usdt(message):
    msg = bot.send_message(
        message.chat.id,
        f"💱 На данный момент курс USDT: {USDT_RATE} грн\nВведите количество USDT, которое вы хотите заказать.",
        reply_markup=ForceReply()
    )
    bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_amount(message):
    try:
        amount = float(message.text)
        total = amount * USDT_RATE
        bot.send_message(message.chat.id, f"✅ Ви хочете купити {amount} USDT\nСума: {total:.2f} грн", reply_markup=main_menu())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введіть число!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "👤 Профіль")
def profile(message):
    bot.send_message(message.chat.id, "Твій профіль...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "⭐ Відгуки")
def reviews(message):
    bot.send_message(message.chat.id, "Відгуки...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛠 Служба підтримки")
def support(message):
    bot.send_message(message.chat.id, "Підтримка...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🧮 Калькулятор")
def calculator(message):
    bot.send_message(message.chat.id, "Калькулятор...", reply_markup=main_menu())

bot.infinity_polling()
