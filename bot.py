import telebot
import os
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== КУРСИ (міняй тут) =====
TON_RATE = 72.3
USDT_RATE = 41.5
# =============================

# ===== РЕКВІЗИТИ (міняй тут) =====
CARD_NUMBER = "4441111057153763"
CARD_OWNER = "Євгеній К."
BANK_NAME = "Monobank🐾"
# ==================================

ADMINS = [6227572453, 6794644473]
user_orders = {}

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("💎 Купити TON"), KeyboardButton("💵 Купити USDT"))
    markup.row(KeyboardButton("👤 Профіль"), KeyboardButton("⭐ Відгуки"))
    markup.row(KeyboardButton("🛠 Служба підтримки"), KeyboardButton("🧮 Калькулятор"))
    return markup

def generate_order_id():
    return random.randint(100000, 999999)

def confirm_button(order_id, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Підтвердити заказ", callback_data=f"confirm_{order_id}_{user_id}"))
    return markup

def leave_comment_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Залишити коментар", callback_data="leave_comment"))
    return markup

MENU_BUTTONS = ["💎 Купити TON", "💵 Купити USDT", "👤 Профіль", "⭐ Відгуки", "🛠 Служба підтримки", "🧮 Калькулятор"]

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
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * TON_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ Количество: {amount} TON | Сумма: {total} грн\n\n"
            f"Введите адрес вашего кошелька сети TON, на который нужно отправить TON.\n"
            f"Если TON нужны на аккаунт, напишите, что их нужно зачислить на юзернейм.",
            reply_markup=main_menu()
        )
        bot.register_next_step_handler(msg, process_ton_wallet, amount, total)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введіть число! Наприклад: 1.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_wallet(message, amount, total):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    wallet = message.text
    order_id = generate_order_id()
    user_orders[message.chat.id] = {"order_id": order_id, "amount": amount, "total": total, "wallet": wallet, "crypto": "TON"}

    bot.send_message(
        message.chat.id,
        f"✅ Хорошо!\nНа этот кошелек будут отправлены TON:\n"
        f"💸 К оплате: {total} грн\n\n"
        f"Выберите удобный способ оплаты👇",
        reply_markup=main_menu()
    )
    bot.send_message(
        message.chat.id,
        f"💳 Банк {BANK_NAME}\n"
        f"Карта: {CARD_NUMBER}\n"
        f"Получатель: {CARD_OWNER}\n\n"
        f"💬 Оплата не проходит?\nНапишите нам в поддержку!\n\n"
        f"💰 К оплате: {total} грн\n"
        f"👛 TON на кошелёк: {wallet}\n"
        f"💎 Сумма криптовалюты: {amount} TON\n\n"
        f"📸 После оплаты отправьте сюда квитанцию:\n"
        f"📞 Номер заказа: #{order_id}",
        reply_markup=main_menu()
    )

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🆕 НОВЫЙ ЗАКАЗ #{order_id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: {message.chat.id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 Криптовалюта: TON\n"
            f"💰 Количество: {amount} TON\n"
            f"💵 Сумма к оплате: {total} грн\n"
            f"👛 Кошелёк: {wallet}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает оплаты"
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
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * USDT_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ Количество: {amount} USDT | Сумма: {total} грн\n\n"
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
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    wallet = message.text
    order_id = generate_order_id()
    user_orders[message.chat.id] = {"order_id": order_id, "amount": amount, "total": total, "wallet": wallet, "crypto": "USDT"}

    bot.send_message(
        message.chat.id,
        f"✅ Хорошо!\nНа этот кошелек будут отправлены USDT:\n"
        f"💸 К оплате: {total} грн\n\n"
        f"Выберите удобный способ оплаты👇",
        reply_markup=main_menu()
    )
    bot.send_message(
        message.chat.id,
        f"💳 Банк {BANK_NAME}\n"
        f"Карта: {CARD_NUMBER}\n"
        f"Получатель: {CARD_OWNER}\n\n"
        f"💬 Оплата не проходит?\nНапишите нам в поддержку!\n\n"
        f"💰 К оплате: {total} грн\n"
        f"👛 USDT на кошелёк: {wallet}\n"
        f"💵 Сумма криптовалюты: {amount} USDT\n\n"
        f"📸 После оплаты отправьте сюда квитанцию:\n"
        f"📞 Номер заказа: #{order_id}",
        reply_markup=main_menu()
    )

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🆕 НОВЫЙ ЗАКАЗ #{order_id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: {message.chat.id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 Криптовалюта: USDT\n"
            f"💰 Количество: {amount} USDT\n"
            f"💵 Сумма к оплате: {total} грн\n"
            f"👛 Кошелёк: {wallet}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает оплаты"
        )

# ========== КВИТАНЦІЯ ==========

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    order_data = user_orders.get(message.chat.id)
    order_id = order_data["order_id"] if order_data else "??????"
    photo = message.photo[-1].file_id
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"

    bot.send_photo(
        message.chat.id,
        photo,
        caption=f"✅ Заказ #{order_id} получен.\n"
                f"⏳ Сейчас сотрудники проверят вашу квитанцию.\n"
                f"⏰ Обычно это занимает 15–70 минут.\n"
                f"⚠️ Рабочее время: 08:00–00:00 (Киев).\n"
                f"📸 Ваша квитанция получена",
        reply_markup=main_menu()
    )

    for admin_id in ADMINS:
        bot.send_photo(
            admin_id,
            photo,
            caption=f"📸 КВИТАНЦИЯ по заказу #{order_id}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 Пользователь: {username}\n"
                    f"🆔 ID: {message.chat.id}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Клиент отправил квитанцию об оплате",
            reply_markup=confirm_button(order_id, message.chat.id)
        )

# ========== CALLBACK ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_order(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ У вас нет доступа!")
        return

    parts = call.data.split("_")
    order_id = parts[1]
    user_id = int(parts[2])

    crypto = "💎"
    order_data = user_orders.get(user_id)
    if order_data:
        crypto = "💎" if order_data["crypto"] == "TON" else "💵"

    bot.send_message(
        user_id,
        f"✅ Готово!\n"
        f"{crypto} Криптовалюта уже на кошельке\n"
        f"💎 Спасибо, что выбрали нас! ❤️\n"
        f"⭐️ Поставьте оценку:",
        reply_markup=leave_comment_button()
    )

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Заказ #{order_id} підтверджено!")
    bot.send_message(call.message.chat.id, f"✅ Заказ #{order_id} підтверджено і покупецьповідомлений!")

@bot.callback_query_handler(func=lambda call: call.data == "leave_comment")
def leave_comment(call):
    msg = bot.send_message(call.message.chat.id, "✍️ Напишіть ваш коментар:")
    bot.register_next_step_handler(msg, save_comment)
    bot.answer_callback_query(call.id)

def save_comment(message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    order_data = user_orders.get(message.chat.id)
    order_id = order_data["order_id"] if order_data else "??????"

    bot.send_message(message.chat.id, "⭐ Дякуємо за ваш відгук!", reply_markup=main_menu())

    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"💬 НОВЫЙ ОТЗЫВ\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"📞 Заказ: #{order_id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💬 {message.text}"
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
