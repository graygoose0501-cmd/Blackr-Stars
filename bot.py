import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== КУРСИ (міняй тут) =====
TON_RATE = 72.3
USDT_RATE = 41.5
# =============================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("💎 Купити TON"), KeyboardButton("💵 Купити USDT"))
    markup.row(KeyboardButton("👤 Профіль"), KeyboardButton("⭐ Відгуки"))
    markup.row(KeyboardButton("🛠 Служба підтримки"), KeyboardButton("🧮 Калькулятор"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привіт! Вибери дію:", reply_markup=main_menu())

# ========== TON ==========

@bot.message_handler(func=lambda m: m.text == "💎 Купити TON")
def buy_ton(message):
    msg = bot.send_message(
        message.chat.id,
        f"💱 На данный момент курс TON: {TON_RATE} грн\nВведите количество TON, которое вы хотите заказать.",
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_amount(message):
    if message.text in ["💎 Купити TON", "💵 Купити USDT", "👤 Профіль", "⭐ Відгуки", "🛠 Служба підтримки", "🧮 Калькулятор"]:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = amount * TON_RATE
        msg = bot.send_message(
            message.chat.id,
            f"✅ Количество: {amount} TON | Сумма: {total:.2f} грн\n\n"
            f"Введите адрес вашего кошелька сети TON, на который нужно отправить TON.\n"
            f"Если TON нужны на аккаунт, напишите, что их нужно зачислить на юзернейм.",
            reply_markup=main_menu()
        )
        bot.register_next_step_handler(msg, process_ton_wallet, amount, total)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введіть число! Наприклад: 1.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_wallet(message, amount, total):
    if message.text in ["💎 Купити TON", "💵 Купити USDT", "👤 Профіль", "⭐ Відгуки", "🛠 Служба підтримки", "🧮 Калькулятор"]:
        handle_menu(message)
        return
    wallet = message.text
    bot.send_message(
        message.chat.id,
        f"📋 Ваша заявка:\n💎 TON: {amount}\n💰 Сума: {total:.2f} грн\n👛 Гаманець: {wallet}\n\nЗаявка прийнята! Очікуйте.",
        reply_markup=main_menu()
    )

# ========== USDT ==========

@bot.message_handler(func=lambda m: m.text == "💵 Купити USDT")
def buy_usdt(message):
    msg = bot.send_message(
        message.chat.id,
        f"💱 На данный момент курс USDT: {USDT_RATE} грн\nВведите количество USDT, которое вы хотите заказать.",
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_amount(message):
    if message.text in ["💎 Купити TON", "💵 Купити USDT", "👤 Профіль", "⭐ Відгуки", "🛠 Служба підтримки", "🧮 Калькулятор"]:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = amount * USDT_RATE
        msg = bot.send_message(
            message.chat.id,
            f"✅ Количество: {amount} USDT | Сумма: {total:.2f} грн\n\n"
            f"Введите адрес вашего кошелька в сети TON, на который нужно отправить USDT\n"
            f"Комиссия за перевод оплачивается вами:\n• TON — 0,15 $\n"
            f"По другим сетям уточняйте информацию в службе поддержки.",
            reply_markup=main_menu()
        )
        bot.register_next_step_handler(msg, process_usdt_wallet, amount, total)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введіть число! Наприклад: 10.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_wallet(message, amount, total):
    if message.text in ["💎 Купити TON", "💵 Купити USDT", "👤 Профіль", "⭐ Відгуки", "🛠 Служба підтримки", "🧮 Калькулятор"]:
        handle_menu(message)
        return
    wallet = message.text
    bot.send_message(
        message.chat.id,
        f"📋 Ваша заявка:\n💵 USDT: {amount}\n💰 Сума: {total:.2f} грн\n👛 Гаманець: {wallet}\n\nЗаявка прийнята! Очікуйте.",
        reply_markup=main_menu()
    )

# ========== МЕНЮ ==========

def handle_menu(message):
    if message.text == "💎 Купити TON":
        buy_ton(message)
    elif message.text == "💵 Купити USDT":
        buy_usdt(message)
    elif message.text == "👤 Профіль":
        profile(message)
    elif message.text == "⭐ Відгуки":
        reviews(message)
    elif message.text == "🛠 Служба підтримки":
        support(message)
    elif message.text == "🧮 Калькулятор":
        calculator(message)

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
