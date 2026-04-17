import telebot
import os
import random
import datetime
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== КУРСИ (міняй тут) =====
TON_RATE = 72.3
USDT_RATE = 41.5
STARS_BUY_RATE = 0.76        # курс покупки: 100 Stars = 76 грн (0.76 грн за 1 звезду)
STARS_SELL_RATE = 0.40
STARS_MIN_SELL = 50
# =============================

# ===== РЕКВІЗИТИ (міняй тут) =====
CARD_NUMBER = "4441111057153763"
CARD_OWNER = "Євгеній К."
BANK_NAME = "Monobank🐾"
# ==================================

# ===== URL твоей WebApp (замени на свой!) =====
# Загрузи keyboard.html на GitHub Pages, Vercel, или любой HTTPS хостинг
# и вставь прямую ссылку сюда. Обязательно HTTPS!
WEBAPP_URL = "https://YOUR_USERNAME.github.io/your-repo/keyboard.html"
# ================================================

ADMINS = [6227572453, 6794644473]
REVIEWS_CHANNEL_ID = -1003764314898
user_orders = {}

def main_menu():
    """Одна кнопка-меню — открывает WebApp с цветными кнопками"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("🗂 Меню", web_app=WebAppInfo(url=WEBAPP_URL)))
    return markup

def confirm_button(order_id, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить заказ", callback_data=f"confirm_{order_id}_{user_id}"))
    return markup

def confirm_sell_stars_button(order_id, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить продажу Stars", callback_data=f"confirm_sell_stars_{order_id}_{user_id}"))
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

def stars_amount_buttons():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(f"50 ⭐️ — {round(50 * STARS_BUY_RATE)} грн", callback_data="stars_qty_50"),
        InlineKeyboardButton(f"100 ⭐️ — {round(100 * STARS_BUY_RATE)} грн", callback_data="stars_qty_100"),
    )
    markup.row(
        InlineKeyboardButton(f"250 ⭐️ — {round(250 * STARS_BUY_RATE)} грн", callback_data="stars_qty_250"),
        InlineKeyboardButton(f"500 ⭐️ — {round(500 * STARS_BUY_RATE)} грн", callback_data="stars_qty_500"),
    )
    markup.row(
        InlineKeyboardButton(f"1000 ⭐️ — {round(1000 * STARS_BUY_RATE)} грн", callback_data="stars_qty_1000"),
        InlineKeyboardButton(f"2500 ⭐️ — {round(2500 * STARS_BUY_RATE)} грн", callback_data="stars_qty_2500"),
    )
    return markup

def generate_order_id():
    return random.randint(100000, 999999)

# ========== START ==========

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать!\n💼 Нажмите кнопку *Меню* ниже 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ========== ОБРАБОТКА WebApp данных ==========

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    data = message.web_app_data.data
    if data == "💎 Купить TON":
        buy_ton(message)
    elif data == "💵 Купить USDT":
        buy_usdt(message)
    elif data == "⭐️ Купить Stars":
        buy_stars(message)
    elif data == "🌟 Продать Stars":
        sell_stars(message)
    elif data == "👤 Профиль":
        profile(message)
    elif data == "✨ Отзывы":
        reviews(message)
    elif data == "🛠 Поддержка":
        support(message)
    elif data == "🧮 Калькулятор":
        calculator(message)

# ========== TON ==========

def buy_ton(message):
    msg = bot.send_message(
        message.chat.id,
        f"💎 Курс TON: {TON_RATE} грн\n\nВведите количество TON для заказа:",
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_amount(message):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * TON_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ Количество: {amount} TON\n💰 Сумма: {total} грн\n\n"
            f"👛 Введите адрес кошелька TON:\n_(или юзернейм для зачисления на аккаунт)_",
            reply_markup=main_menu(), parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_ton_wallet, amount, total)
    except (ValueError, AttributeError):
        msg = bot.send_message(message.chat.id, "❌ Введите число! Например: 1.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_wallet(message, amount, total):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
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
        f"💳 *Банк {BANK_NAME}*\n🔢 Карта: `{CARD_NUMBER}`\n👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 К оплате: *{total} грн*\n👛 Кошелёк: `{wallet}`\n💎 Сумма: *{amount} TON*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n📞 Заказ: *#{order_id}*",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_id}*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"💎 TON: *{amount}* | 💵 *{total} грн*\n👛 `{wallet}`\n⏳ Ожидает оплаты",
            parse_mode="Markdown")

# ========== USDT ==========

def buy_usdt(message):
    msg = bot.send_message(
        message.chat.id,
        f"💵 Курс USDT: {USDT_RATE} грн\n\nВведите количество USDT для заказа:",
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_amount(message):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * USDT_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ Количество: {amount} USDT\n💰 Сумма: {total} грн\n\n"
            f"👛 Введите адрес кошелька TON для получения USDT:\n\n"
            f"⚠️ Комиссия: TON — 0,15 $",
            reply_markup=main_menu()
        )
        bot.register_next_step_handler(msg, process_usdt_wallet, amount, total)
    except (ValueError, AttributeError):
        msg = bot.send_message(message.chat.id, "❌ Введите число! Например: 10.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_wallet(message, amount, total):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
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
        f"💳 *Банк {BANK_NAME}*\n🔢 Карта: `{CARD_NUMBER}`\n👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 К оплате: *{total} грн*\n👛 Кошелёк: `{wallet}`\n💵 Сумма: *{amount} USDT*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n📞 Заказ: *#{order_id}*",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_id}*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"💵 USDT: *{amount}* | 💵 *{total} грн*\n👛 `{wallet}`\n⏳ Ожидает оплаты",
            parse_mode="Markdown")

# ========== STARS КУПИТЬ ==========

def buy_stars(message):
    bot.send_message(
        message.chat.id,
        "⭐️ *Для кого покупаем Telegram Stars?* 👥",
        reply_markup=stars_for_who_buttons(), parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "stars_friend")
def stars_for_friend(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
        "👥 Введите юзернейм друга:\n_(например: @username)_",
        reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_stars_username, "friend")

@bot.callback_query_handler(func=lambda call: call.data == "stars_self")
def stars_for_self(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
        "👤 Введите ваш юзернейм:\n_(например: @username)_",
        reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_stars_username, "self")

def process_stars_username(message, stars_type):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
        return
    username_target = message.text
    user_orders[message.chat.id] = {
        "stars_type": stars_type,
        "username_target": username_target,
        "awaiting_stars_amount": True
    }
    bot.send_message(message.chat.id,
        "⭐️ Сколько Stars хотите купить?\nВыберите или введите своё количество:",
        reply_markup=stars_amount_buttons())

@bot.callback_query_handler(func=lambda call: call.data.startswith("stars_qty_"))
def stars_qty_selected(call):
    bot.answer_callback_query(call.id)
    amount = int(call.data.split("_")[2])
    order_data = user_orders.get(call.message.chat.id, {})
    finish_stars_order(call.message, amount,
        order_data.get("stars_type", "self"),
        order_data.get("username_target", ""))

def finish_stars_order(message, amount, stars_type, username_target):
    order_id = generate_order_id()
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    who = "Другу" if stars_type == "friend" else "Себе"
    total = round(amount * STARS_BUY_RATE, 2)
    user_orders[message.chat.id] = {
        "order_id": order_id, "amount": amount, "total": total,
        "wallet": username_target, "crypto": "Stars", "date": now
    }
    bot.send_message(
        message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n🔢 Карта: `{CARD_NUMBER}`\n👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⭐️ Stars: *{amount}* — *{total} грн*\n"
        f"👤 Для: {who} (`{username_target}`)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 К оплате: *{total} грн*\n"
        f"📸 После оплаты отправьте квитанцию\n📞 Заказ: *#{order_id}*",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_id}*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"⭐️ Stars: *{amount}* — *{total} грн* | Для: {who} ({username_target})\n⏳ Ожидает оплаты",
            parse_mode="Markdown")

# ========== STARS ПРОДАТЬ ==========

def sell_stars(message):
    bot.send_message(
        message.chat.id,
        f"🌟 *Хочешь продать звёзды Telegram?*\n\n"
        f"💰 Курс: 1⭐️ = *{STARS_SELL_RATE} грн*\n"
        f"📦 Минимум — *{STARS_MIN_SELL} звёзд*\n\n"
        f"🚀 За *1000⭐️* получишь *400 грн* за 5 минут!",
        reply_markup=sell_stars_inline_button(), parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "sell_stars_start")
def sell_stars_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
        f"⭐️ Сколько Stars хотите продать?\n_(минимум {STARS_MIN_SELL})_",
        reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_sell_stars_amount)

def process_sell_stars_amount(message):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
        return
    try:
        amount = int(float(message.text.replace(",", ".")))
        if amount < STARS_MIN_SELL:
            msg = bot.send_message(message.chat.id,
                f"❌ Минимум {STARS_MIN_SELL} Stars! Введите ещё раз:", reply_markup=main_menu())
            bot.register_next_step_handler(msg, process_sell_stars_amount)
            return
        total = round(amount * STARS_SELL_RATE, 2)
        msg = bot.send_message(message.chat.id,
            f"✅ *{amount} ⭐️ = {total} грн*\n\n💳 Введите номер карты для выплаты:",
            reply_markup=main_menu(), parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_sell_stars_card, amount, total)
    except (ValueError, AttributeError):
        msg = bot.send_message(message.chat.id, "❌ Введите целое число! Например: 1000", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_sell_stars_amount)

def process_sell_stars_card(message, amount, total):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
        return
    card = message.text
    order_id = generate_order_id()
    bot.send_message(
        message.chat.id,
        f"✅ *Заявка принята!*\n\n"
        f"⭐️ Продаёте: *{amount} Stars*\n💰 Получите: *{total} грн*\n"
        f"💳 На карту: `{card}`\n📞 Заказ: *#{order_id}*\n\n⏳ Ожидайте подтверждения.",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🌟 *ПРОДАЖА STARS #{order_id}*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"⭐️ Количество: *{amount}* | 💰 К выплате: *{total} грн*\n💳 Карта: `{card}`\n⏳ Ожидает обработки",
            parse_mode="Markdown",
            reply_markup=confirm_sell_stars_button(order_id, message.chat.id))

# ========== CALLBACK: ПОДТВЕРЖДЕНИЕ ПРОДАЖИ STARS ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_sell_stars_"))
def confirm_sell_stars_order(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    parts = call.data.split("_")
    order_id = parts[3]
    user_id = int(parts[4])
    bot.send_message(user_id,
        f"🌟 *Продажа Telegram Stars выполнена!*\n\n"
        f"⭐️ Звёзды получены, выплата отправлена на вашу карту.\n"
        f"💎 Спасибо, что выбрали нас! ❤️",
        reply_markup=leave_comment_button(), parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Продажа Stars #{order_id} подтверждена!")
    bot.send_message(call.message.chat.id, f"✅ Продажа Stars *#{order_id}* подтверждена!", parse_mode="Markdown")

# ========== КВИТАНЦИЯ ==========

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    order_data = user_orders.get(message.chat.id)
    if order_data and order_data.get("pending_comment"):
        save_comment_photo(message)
        return
    order_id = order_data["order_id"] if order_data else "??????"
    photo = message.photo[-1].file_id
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    bot.send_photo(message.chat.id, photo,
        caption=f"✅ Заказ #{order_id} получен!\n⏳ Проверка 15–70 минут.\n⚠️ Рабочее время: 08:00–00:00 (Киев).",
        reply_markup=main_menu())
    for admin_id in ADMINS:
        bot.send_photo(admin_id, photo,
            caption=f"📸 КВИТАНЦИЯ #{order_id}\n👤 {username} | ID: {message.chat.id}",
            reply_markup=confirm_button(order_id, message.chat.id))

# ========== CALLBACK: ПОДТВЕРЖДЕНИЕ ПОКУПКИ ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") and not call.data.startswith("confirm_sell_stars_"))
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
        emoji, crypto = "💎", "криптовалюта"
    bot.send_message(user_id,
        f"✅ *Готово!*\n{emoji} {crypto} уже на кошельке\n💎 Спасибо, что выбрали нас! ❤️",
        reply_markup=leave_comment_button(), parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Заказ #{order_id} подтверждён!")
    bot.send_message(call.message.chat.id, f"✅ Заказ *#{order_id}* подтверждён!", parse_mode="Markdown")

# ========== ОТЗЫВ ==========

@bot.callback_query_handler(func=lambda call: call.data == "leave_comment")
def leave_comment_cb(call):
    msg = bot.send_message(call.message.chat.id, "✍️ Напишите ваш отзыв:")
    bot.register_next_step_handler(msg, save_comment)
    bot.answer_callback_query(call.id)

def save_comment(message):
    if message.content_type == 'web_app_data':
        handle_web_app_data(message)
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
    caption = (f"📝 Новый отзыв\n━━━━━━━━━━━━━━━━━━\n"
               f"👤 {username}\n💰 {amount} {crypto}\n💬 {comment}\n📅 {date}")
    bot.send_message(message.chat.id, "⭐ Спасибо за ваш отзыв!", reply_markup=main_menu())
    bot.send_photo(REVIEWS_CHANNEL_ID, photo, caption=caption)
    for admin_id in ADMINS:
        bot.send_photo(admin_id, photo, caption=f"💬 НОВЫЙ ОТЗЫВ\n{caption}")

# ========== РАЗДЕЛЫ ==========

def profile(message):
    bot.send_message(message.chat.id, "👤 Ваш профиль...", reply_markup=main_menu())

def reviews(message):
    bot.send_message(message.chat.id, "✨ Отзывы...", reply_markup=main_menu())

def support(message):
    bot.send_message(message.chat.id, "🛠 Поддержка...", reply_markup=main_menu())

def calculator(message):
    bot.send_message(message.chat.id, "🧮 Калькулятор...", reply_markup=main_menu())

bot.infinity_polling()
