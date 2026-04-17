import telebot
import os
import random
import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== КУРСИ (міняй тут) =====
TON_RATE = 72.3
USDT_RATE = 41.5
STARS_SELL_RATE = 0.40
STARS_MIN_SELL = 50
# =============================

# ===== РЕКВІЗИТИ (міняй тут) =====
CARD_NUMBER = "4441111057153763"
CARD_OWNER = "Євгеній К."
BANK_NAME = "Monobank🐾"
# ==================================

ADMINS = [6227572453, 6794644473]
REVIEWS_CHANNEL_ID = -1003764314898
user_orders = {}

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("💎 Купить TON"), KeyboardButton("💵 Купить USDT"))
    markup.row(KeyboardButton("⭐️ Купить Stars"), KeyboardButton("🌟 Продать Stars"))
    markup.row(KeyboardButton("👤 Профиль"), KeyboardButton("✨ Отзывы"))
    markup.row(KeyboardButton("🛠 Поддержка"), KeyboardButton("🧮 Калькулятор"))
    return markup

def generate_order_id():
    return random.randint(100000, 999999)

def confirm_button(order_id, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить заказ", callback_data=f"confirm_{order_id}_{user_id}"))
    return markup

def leave_comment_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Оставить отзыв", callback_data="leave_comment"))
    return markup

def stars_for_who_buttons():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("👥 Другу", callback_data="stars_friend"),
        InlineKeyboardButton("👤 Себе", callback_data="stars_self")
    )
    return markup

def sell_stars_inline_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⭐️ Продать Stars", callback_data="sell_stars_start"))
    return markup

MENU_BUTTONS = [
    "💎 Купить TON", "💵 Купить USDT",
    "⭐️ Купить Stars", "🌟 Продать Stars",
    "👤 Профиль", "✨ Отзывы",
    "🛠 Поддержка", "🧮 Калькулятор"
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать!\n💼 Выберите действие:",
        reply_markup=main_menu()
    )

# ========== TON ==========

@bot.message_handler(func=lambda m: m.text == "💎 Купить TON")
def buy_ton(message):
    msg = bot.send_message(
        message.chat.id,
        f"💎 Курс TON: {TON_RATE} грн\n\n"
        f"Введите количество TON для заказа:",
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
            f"✅ Количество: {amount} TON\n"
            f"💰 Сумма: {total} грн\n\n"
            f"👛 Введите адрес кошелька TON:\n"
            f"_(или юзернейм, если зачислить на аккаунт)_",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_ton_wallet, amount, total)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введите число! Например: 1.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_wallet(message, amount, total):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    wallet = message.text
    order_id = generate_order_id()
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user_orders[message.chat.id] = {
        "order_id": order_id, "amount": amount, "total": total,
        "wallet": wallet, "crypto": "TON", "date": now
    }

    bot.send_message(
        message.chat.id,
        f"✅ Отлично!\n"
        f"💎 TON будут отправлены на кошелёк\n"
        f"💸 К оплате: *{total} грн*\n\n"
        f"👇 Выберите способ оплаты:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    bot.send_message(
        message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n"
        f"🔢 Карта: `{CARD_NUMBER}`\n"
        f"👤 Получатель: {CARD_OWNER}\n\n"
        f"💬 Оплата не проходит? → 🛠 Поддержка\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 К оплате: *{total} грн*\n"
        f"👛 Кошелёк: `{wallet}`\n"
        f"💎 Криптовалюта: *{amount} TON*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n"
        f"📞 Номер заказа: *#{order_id}*",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_id}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: `{message.chat.id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 Криптовалюта: TON\n"
            f"💰 Количество: *{amount} TON*\n"
            f"💵 К оплате: *{total} грн*\n"
            f"👛 Кошелёк: `{wallet}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает оплаты",
            parse_mode="Markdown"
        )

# ========== USDT ==========

@bot.message_handler(func=lambda m: m.text == "💵 Купить USDT")
def buy_usdt(message):
    msg = bot.send_message(
        message.chat.id,
        f"💵 Курс USDT: {USDT_RATE} грн\n\n"
        f"Введите количество USDT для заказа:",
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
            f"✅ Количество: {amount} USDT\n"
            f"💰 Сумма: {total} грн\n\n"
            f"👛 Введите адрес кошелька TON для получения USDT:\n\n"
            f"⚠️ Комиссия оплачивается вами:\n• TON — 0,15 $\n"
            f"По другим сетям — уточняйте в поддержке.",
            reply_markup=main_menu()
        )
        bot.register_next_step_handler(msg, process_usdt_wallet, amount, total)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введите число! Например: 10.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_wallet(message, amount, total):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    wallet = message.text
    order_id = generate_order_id()
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user_orders[message.chat.id] = {
        "order_id": order_id, "amount": amount, "total": total,
        "wallet": wallet, "crypto": "USDT", "date": now
    }

    bot.send_message(
        message.chat.id,
        f"✅ Отлично!\n"
        f"💵 USDT будут отправлены на кошелёк\n"
        f"💸 К оплате: *{total} грн*\n\n"
        f"👇 Выберите способ оплаты:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    bot.send_message(
        message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n"
        f"🔢 Карта: `{CARD_NUMBER}`\n"
        f"👤 Получатель: {CARD_OWNER}\n\n"
        f"💬 Оплата не проходит? → 🛠 Поддержка\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 К оплате: *{total} грн*\n"
        f"👛 Кошелёк: `{wallet}`\n"
        f"💵 Криптовалюта: *{amount} USDT*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n"
        f"📞 Номер заказа: *#{order_id}*",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_id}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: `{message.chat.id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 Криптовалюта: USDT\n"
            f"💰 Количество: *{amount} USDT*\n"
            f"💵 К оплате: *{total} грн*\n"
            f"👛 Кошелёк: `{wallet}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает оплаты",
            parse_mode="Markdown"
        )

# ========== STARS КУПИТЬ ==========

@bot.message_handler(func=lambda m: m.text == "⭐️ Купить Stars")
def buy_stars(message):
    bot.send_message(
        message.chat.id,
        "⭐️ *Для кого покупаем Telegram Stars?* 👥",
        reply_markup=stars_for_who_buttons(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "stars_friend")
def stars_for_friend(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "👥 Введите юзернейм друга:\n_(например: @username)_",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_stars_username, "friend")

@bot.callback_query_handler(func=lambda call: call.data == "stars_self")
def stars_for_self(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "👤 Введите ваш юзернейм:\n_(например: @username)_",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_stars_username, "self")

def process_stars_username(message, stars_type):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    username_target = message.text
    msg = bot.send_message(
        message.chat.id,
        f"⭐️ Сколько Stars хотите купить?\nВведите количество:",
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, process_stars_amount, stars_type, username_target)

def process_stars_amount(message, stars_type, username_target):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = int(float(message.text.replace(",", ".")))
        order_id = generate_order_id()
        now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        who = "Другу" if stars_type == "friend" else "Себе"

        user_orders[message.chat.id] = {
            "order_id": order_id, "amount": amount, "total": "—",
            "wallet": username_target, "crypto": "Stars", "date": now
        }

        bot.send_message(
            message.chat.id,
            f"✅ Отлично!\n"
            f"⭐️ Stars: *{amount}*\n"
            f"👤 Для: {who} ({username_target})\n\n"
            f"👇 Выберите способ оплаты:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
        bot.send_message(
            message.chat.id,
            f"💳 *Банк {BANK_NAME}*\n"
            f"🔢 Карта: `{CARD_NUMBER}`\n"
            f"👤 Получатель: {CARD_OWNER}\n\n"
            f"💬 Оплата не проходит? → 🛠 Поддержка\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⭐️ Stars: *{amount}*\n"
            f"👤 Для: {who} (`{username_target}`)\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📸 После оплаты отправьте квитанцию\n"
            f"📞 Номер заказа: *#{order_id}*",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

        username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
        for admin_id in ADMINS:
            bot.send_message(
                admin_id,
                f"🆕 *НОВЫЙ ЗАКАЗ #{order_id}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Пользователь: {username}\n"
                f"🆔 ID: `{message.chat.id}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⭐️ Тип: Stars\n"
                f"💰 Количество: *{amount} Stars*\n"
                f"👤 Для: {who} ({username_target})\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⏳ Статус: Ожидает оплаты",
                parse_mode="Markdown"
            )
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введите целое число! Например: 500", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_stars_amount, stars_type, username_target)

# ========== STARS ПРОДАТЬ ==========

@bot.message_handler(func=lambda m: m.text == "🌟 Продать Stars")
def sell_stars(message):
    bot.send_message(
        message.chat.id,
        f"🌟 *Хочешь продать свои звёзды Telegram?*\n"
        f"Тебе к нам!\n\n"
        f"💰 Мы покупаем звёзды по курсу:\n"
        f"1⭐️ = *{STARS_SELL_RATE} грн*\n"
        f"📦 Минимум — *{STARS_MIN_SELL} звёзд*\n\n"
        f"🚀 За продажу *1000⭐️* ты получишь *400 грн* за 5 минут!",
        reply_markup=sell_stars_inline_button(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "sell_stars_start")
def sell_stars_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        f"⭐️ Сколько Stars хотите продать?\n_(минимум {STARS_MIN_SELL})_",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_sell_stars_amount)

def process_sell_stars_amount(message):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = int(float(message.text.replace(",", ".")))
        if amount < STARS_MIN_SELL:
            msg = bot.send_message(
                message.chat.id,
                f"❌ Минимум {STARS_MIN_SELL} Stars! Введите ещё раз:",
                reply_markup=main_menu()
            )
            bot.register_next_step_handler(msg, process_sell_stars_amount)
            return
        total = round(amount * STARS_SELL_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ *{amount} ⭐️ = {total} грн*\n\n"
            f"💳 Введите номер карты для выплаты:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_sell_stars_card, amount, total)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введите целое число! Например: 1000", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_sell_stars_amount)

def process_sell_stars_card(message, amount, total):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    card = message.text
    order_id = generate_order_id()

    bot.send_message(
        message.chat.id,
        f"✅ *Заявка принята!*\n\n"
        f"⭐️ Продаёте: *{amount} Stars*\n"
        f"💰 Получите: *{total} грн*\n"
        f"💳 На карту: `{card}`\n"
        f"📞 Номер заказа: *#{order_id}*\n\n"
        f"⏳ Ожидайте — с вами свяжутся для подтверждения.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🌟 *ПРОДАЖА STARS #{order_id}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: `{message.chat.id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⭐️ Количество: *{amount} Stars*\n"
            f"💰 К выплате: *{total} грн*\n"
            f"💳 Карта: `{card}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает обработки",
            parse_mode="Markdown"
        )

# ========== КВИТАНЦІЯ ==========

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    order_data = user_orders.get(message.chat.id)

    if order_data and order_data.get("pending_comment"):
        save_comment_photo(message)
        return

    order_id = order_data["order_id"] if order_data else "??????"
    photo = message.photo[-1].file_id
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"

    bot.send_photo(
        message.chat.id,
        photo,
        caption=f"✅ Заказ #{order_id} получен!\n"
                f"⏳ Сотрудники проверят квитанцию.\n"
                f"⏰ Обычно 15–70 минут.\n"
                f"⚠️ Рабочее время: 08:00–00:00 (Киев).\n"
                f"📸 Квитанция получена",
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
                    f"✅ Клиент отправил квитанцию",
            reply_markup=confirm_button(order_id, message.chat.id)
        )

# ========== CALLBACK ПОДТВЕРЖДЕНИЕ ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_order(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return

    parts = call.data.split("_")
    order_id = parts[1]
    user_id = int(parts[2])

    order_data = user_orders.get(user_id)
    if order_data:
        crypto = order_data["crypto"]
        emoji = "💎" if crypto == "TON" else ("💵" if crypto == "USDT" else "⭐️")
    else:
        emoji = "💎"
        crypto = "криптовалюта"

    bot.send_message(
        user_id,
        f"✅ *Готово!*\n"
        f"{emoji} {crypto} уже на кошельке\n"
        f"💎 Спасибо, что выбрали нас! ❤️\n\n"
        f"⭐️ Поставьте оценку:",
        reply_markup=leave_comment_button(),
        parse_mode="Markdown"
    )

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Заказ #{order_id} подтверждён!")
    bot.send_message(call.message.chat.id, f"✅ Заказ *#{order_id}* подтверждён, покупатель уведомлён!", parse_mode="Markdown")

# ========== ОТЗЫВ ==========

@bot.callback_query_handler(func=lambda call: call.data == "leave_comment")
def leave_comment(call):
    msg = bot.send_message(call.message.chat.id, "✍️ Напишите ваш отзыв:")
    bot.register_next_step_handler(msg, save_comment)
    bot.answer_callback_query(call.id)

def save_comment(message):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    order_data = user_orders.get(message.chat.id, {})
    order_data["pending_comment"] = message.text
    user_orders[message.chat.id] = order_data
    bot.send_message(message.chat.id, "📸 Теперь отправьте фото для отзыва:")

def save_comment_photo(message):
    order_data = user_orders.get(message.chat.id, {})
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    order_id = order_data.get("order_id", "??????")
    amount = order_data.get("amount", "?")
    crypto = order_data.get("crypto", "?")
    comment = order_data.get("pending_comment", "?")
    date = order_data.get("date", datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    photo = message.photo[-1].file_id

    order_data.pop("pending_comment", None)
    user_orders[message.chat.id] = order_data

    caption = (
        f"📝 Новый отзыв\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Клиент: {username}\n"
        f"💰 Куплено: {amount} {crypto}\n"
        f"💬 Комментарий: {comment}\n"
        f"📅 Дата: {date}"
    )

    bot.send_message(message.chat.id, "⭐ Спасибо за ваш отзыв!", reply_markup=main_menu())
    bot.send_photo(REVIEWS_CHANNEL_ID, photo, caption=caption)
    for admin_id in ADMINS:
        bot.send_photo(admin_id, photo, caption=f"💬 НОВЫЙ ОТЗЫВ\n{caption}")

# ========== МЕНЮ ==========

def handle_menu(message):
    if message.text == "💎 Купить TON":
        buy_ton(message)
    elif message.text == "💵 Купить USDT":
        buy_usdt(message)
    elif message.text == "⭐️ Купить Stars":
        buy_stars(message)
    elif message.text == "🌟 Продать Stars":
        sell_stars(message)
    elif message.text == "👤 Профиль":
        profile(message)
    elif message.text == "✨ Отзывы":
        reviews(message)
    elif message.text == "🛠 Поддержка":
        support(message)
    elif message.text == "🧮 Калькулятор":
        calculator(message)

@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(message):
    bot.send_message(message.chat.id, "👤 Ваш профиль...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "✨ Отзывы")
def reviews(message):
    bot.send_message(message.chat.id, "✨ Отзывы...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛠 Поддержка")
def support(message):
    bot.send_message(message.chat.id, "🛠 Поддержка...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🧮 Калькулятор")
def calculator(message):
    bot.send_message(message.chat.id, "🧮 Калькулятор...", reply_markup=main_menu())

bot.infinity_polling()
