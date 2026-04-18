import telebot
import os
import random
import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ===== КУРСИ (міняй тут) =====
TON_BUY_RATE = 72.3
TON_SELL_RATE = 70.0      # Курс продажи TON

USDT_BUY_RATE = 41.5
USDT_SELL_RATE = 40.0     # Курс продажи USDT

STARS_BUY_RATE = 0.76     # 100 Stars = 76 грн
STARS_SELL_RATE = 0.40
STARS_MIN_SELL = 500
# =============================

# ===== РЕКВІЗИТИ (міняй тут) =====
CARD_NUMBER = "4441111057153763"
CARD_OWNER = "Євгеній К."
BANK_NAME = "Monobank🐾"
# ==================================

ADMINS = [6227572453, 6794644473]
REVIEWS_CHANNEL_ID = -1003764314898
user_orders = {}

# Счетчик отзывов
review_counter = 1

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    # ID ваших кастомных эмодзи
    EMOJI_TON = "5078343973303485905"
    EMOJI_USDT = "5080137014775383220"
    EMOJI_STARS_BUY = "5469641199348363998"
    EMOJI_STARS_SELL = "5469744063815102906"
    EMOJI_PROFILE = "5280781432824802048"
    EMOJI_REVIEWS = "5303138782004924588"
    EMOJI_SUPPORT = "5413623448440160154"
    EMOJI_CALC = "5303214794336125778"
    
    # Первый ряд - синий (TON и USDT)
    markup.row(
        KeyboardButton("TON", style="primary", icon_custom_emoji_id=EMOJI_TON),
        KeyboardButton("USDT", style="primary", icon_custom_emoji_id=EMOJI_USDT)
    )
    # Второй ряд - синий (Stars покупка и продажа)
    markup.row(
        KeyboardButton("Купить Stars", style="primary", icon_custom_emoji_id=EMOJI_STARS_BUY),
        KeyboardButton("Продать Stars", style="primary", icon_custom_emoji_id=EMOJI_STARS_SELL)
    )
    # Третий ряд - зеленый (Профиль и Отзывы)
    markup.row(
        KeyboardButton("Профиль", style="success", icon_custom_emoji_id=EMOJI_PROFILE),
        KeyboardButton("Отзывы", style="success", icon_custom_emoji_id=EMOJI_REVIEWS)
    )
    # Четвертый ряд - красный (Поддержка и Калькулятор)
    markup.row(
        KeyboardButton("Поддержка", style="danger", icon_custom_emoji_id=EMOJI_SUPPORT),
        KeyboardButton("Калькулятор", style="danger", icon_custom_emoji_id=EMOJI_CALC)
    )
    return markup
    
MENU_BUTTONS = [
    "TON", "USDT",
    "Купить Stars", "Продать Stars",
    "Профиль", "Отзывы",
    "Поддержка", "Калькулятор"
]

def generate_order_id():
    return random.randint(100000, 999999)

def confirm_button(order_id, user_id, action_type="buy"):
    markup = InlineKeyboardMarkup()
    if action_type == "buy":
        markup.add(InlineKeyboardButton("✅ Подтвердить заказ", callback_data=f"confirm_{order_id}_{user_id}"))
    else:
        markup.add(InlineKeyboardButton("✅ Подтвердить выплату", callback_data=f"confirm_sell_{order_id}_{user_id}"))
    return markup

def confirm_sell_stars_button(order_id, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить продажу Stars", callback_data=f"confirm_sell_stars_{order_id}_{user_id}"))
    return markup

def leave_comment_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Оставить отзыв", callback_data="leave_comment"))
    return markup

def ton_inline_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💎 Купить TON", callback_data="ton_buy"),
        InlineKeyboardButton("💸 Продать TON", callback_data="ton_sell")
    )
    return markup

def usdt_inline_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💵 Купить USDT", callback_data="usdt_buy"),
        InlineKeyboardButton("💸 Продать USDT", callback_data="usdt_sell")
    )
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

# ========== START ==========

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать!\n💼 Выберите действие:",
        reply_markup=main_menu()
    )

# ========== TON & USDT MAIN HANDLER ==========

@bot.message_handler(func=lambda m: m.text == "TON")
def ton_menu(message):
    bot.send_message(
        message.chat.id,
        f"💎 *TON*\n\n"
        f"Курс покупки: *{TON_BUY_RATE} грн*\n"
        f"Курс продажи: *{TON_SELL_RATE} грн*\n\n"
        f"Выберите действие:",
        reply_markup=ton_inline_menu(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "USDT")
def usdt_menu(message):
    bot.send_message(
        message.chat.id,
        f"💵 *USDT*\n\n"
        f"Курс покупки: *{USDT_BUY_RATE} грн*\n"
        f"Курс продажи: *{USDT_SELL_RATE} грн*\n\n"
        f"Выберите действие:",
        reply_markup=usdt_inline_menu(),
        parse_mode="Markdown"
    )

# ========== TON BUY ==========
@bot.callback_query_handler(func=lambda call: call.data == "ton_buy")
def buy_ton_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        f"💎 Курс TON: {TON_BUY_RATE} грн\n\nВведите количество TON для заказа:",
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_amount(message):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * TON_BUY_RATE, 2)
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
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    wallet = message.text
    order_id = generate_order_id()
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user_orders[message.chat.id] = {
        "order_id": order_id, "amount": amount, "total": total,
        "wallet": wallet, "crypto": "TON", "date": now, "type": "buy"
    }
    bot.send_message(
        message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n"
        f"🔢 Карта: `{CARD_NUMBER}`\n"
        f"👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💎 Сумма: *{amount} TON*\n"
        f"💰 К оплате: *{total} грн*\n"
        f"👛 Кошелёк: `{wallet}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n"
        f"📞 Номер заказа: *#{order_id}*",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_id} (ПОКУПКА TON)*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: `{message.chat.id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 Количество: *{amount} TON*\n"
            f"💵 К оплате: *{total} грн*\n"
            f"👛 Кошелёк: `{wallet}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает оплаты",
            parse_mode="Markdown"
        )

# ========== TON SELL ==========
@bot.callback_query_handler(func=lambda call: call.data == "ton_sell")
def sell_ton_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        f"💸 *Продажа TON*\nКурс: {TON_SELL_RATE} грн\n\n"
        f"Введите количество TON для продажи:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_sell_ton_amount)

def process_sell_ton_amount(message):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * TON_SELL_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ *{amount} TON = {total} грн*\n\n💳 Введите номер карты для выплаты:",
            reply_markup=main_menu(), parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_sell_ton_card, amount, total)
    except (ValueError, AttributeError):
        msg = bot.send_message(message.chat.id, "❌ Введите число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_sell_ton_amount)

def process_sell_ton_card(message, amount, total):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    card = message.text
    order_id = generate_order_id()
    user_orders[message.chat.id] = {"order_id": order_id, "amount": amount, "total": total, "crypto": "TON", "type": "sell"}
    
    bot.send_message(
        message.chat.id,
        f"✅ *Заявка на продажу TON принята!*\n\n"
        f"💰 Вы получите: *{total} грн*\n"
        f"💳 На карту: `{card}`\n"
        f"📞 Номер заказа: *#{order_id}*\n\n"
        f"⏳ Ожидайте подтверждения.",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🔄 *ПРОДАЖА TON #{order_id}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: `{message.chat.id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 Продаёт: *{amount} TON*\n"
            f"💰 К выплате: *{total} грн*\n"
            f"💳 Карта: `{card}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает выплаты",
            parse_mode="Markdown",
            reply_markup=confirm_button(order_id, message.chat.id, action_type="sell")
        )

# ========== USDT BUY ==========
@bot.callback_query_handler(func=lambda call: call.data == "usdt_buy")
def buy_usdt_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        f"💵 Курс USDT: {USDT_BUY_RATE} грн\n\nВведите количество USDT для заказа:",
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_amount(message):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * USDT_BUY_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ Количество: {amount} USDT\n💰 Сумма: {total} грн\n\n"
            f"👛 Введите адрес кошелька TON для получения USDT:\n\n"
            f"⚠️ Комиссия оплачивается вами:\n• TON — 0,15 $\n"
            f"По другим сетям — уточняйте в поддержке.",
            reply_markup=main_menu()
        )
        bot.register_next_step_handler(msg, process_usdt_wallet, amount, total)
    except (ValueError, AttributeError):
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
        "wallet": wallet, "crypto": "USDT", "date": now, "type": "buy"
    }
    bot.send_message(
        message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n"
        f"🔢 Карта: `{CARD_NUMBER}`\n"
        f"👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 Сумма: *{amount} USDT*\n"
        f"💰 К оплате: *{total} грн*\n"
        f"👛 Кошелёк: `{wallet}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n"
        f"📞 Номер заказа: *#{order_id}*",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_id} (ПОКУПКА USDT)*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: `{message.chat.id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 Количество: *{amount} USDT*\n"
            f"💵 К оплате: *{total} грн*\n"
            f"👛 Кошелёк: `{wallet}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает оплаты",
            parse_mode="Markdown"
        )

# ========== USDT SELL ==========
@bot.callback_query_handler(func=lambda call: call.data == "usdt_sell")
def sell_usdt_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        f"💸 *Продажа USDT*\nКурс: {USDT_SELL_RATE} грн\n\n"
        f"Введите количество USDT для продажи:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_sell_usdt_amount)

def process_sell_usdt_amount(message):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * USDT_SELL_RATE, 2)
        msg = bot.send_message(
            message.chat.id,
            f"✅ *{amount} USDT = {total} грн*\n\n💳 Введите номер карты для выплаты:",
            reply_markup=main_menu(), parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_sell_usdt_card, amount, total)
    except (ValueError, AttributeError):
        msg = bot.send_message(message.chat.id, "❌ Введите число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_sell_usdt_amount)

def process_sell_usdt_card(message, amount, total):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    card = message.text
    order_id = generate_order_id()
    user_orders[message.chat.id] = {"order_id": order_id, "amount": amount, "total": total, "crypto": "USDT", "type": "sell"}
    
    bot.send_message(
        message.chat.id,
        f"✅ *Заявка на продажу USDT принята!*\n\n"
        f"💰 Вы получите: *{total} грн*\n"
        f"💳 На карту: `{card}`\n"
        f"📞 Номер заказа: *#{order_id}*\n\n"
        f"⏳ Ожидайте подтверждения.",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"🔄 *ПРОДАЖА USDT #{order_id}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {username}\n"
            f"🆔 ID: `{message.chat.id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 Продаёт: *{amount} USDT*\n"
            f"💰 К выплате: *{total} грн*\n"
            f"💳 Карта: `{card}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает выплаты",
            parse_mode="Markdown",
            reply_markup=confirm_button(order_id, message.chat.id, action_type="sell")
        )

# ========== STARS ==========

@bot.message_handler(func=lambda m: m.text == "Купить Stars")
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
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_stars_username, "friend")

@bot.callback_query_handler(func=lambda call: call.data == "stars_self")
def stars_for_self(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "👤 Введите ваш юзернейм:\n_(например: @username)_",
        reply_markup=main_menu(), parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_stars_username, "self")

def process_stars_username(message, stars_type):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    username_target = message.text
    user_orders[message.chat.id] = {
        "stars_type": stars_type,
        "username_target": username_target,
        "awaiting_stars_amount": True
    }
    bot.send_message(
        message.chat.id,
        "⭐️ Сколько Stars хотите купить?\nВыберите или введите своё количество:",
        reply_markup=stars_amount_buttons()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("stars_qty_"))
def stars_qty_selected(call):
    bot.answer_callback_query(call.id)
    amount = int(call.data.split("_")[2])
    order_data = user_orders.get(call.message.chat.id, {})
    finish_stars_order(
        call.message, amount,
        order_data.get("stars_type", "self"),
        order_data.get("username_target", "")
    )

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
        f"💳 *Банк {BANK_NAME}*\n"
        f"🔢 Карта: `{CARD_NUMBER}`\n"
        f"👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⭐️ Stars: *{amount}* — *{total} грн*\n"
        f"👤 Для: {who} (`{username_target}`)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 К оплате: *{total} грн*\n"
        f"📸 После оплаты отправьте квитанцию\n"
        f"📞 Номер заказа: *#{order_id}*",
        reply_markup=main_menu(), parse_mode="Markdown"
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
            f"⭐️ Stars: *{amount}* — *{total} грн*\n"
            f"👤 Для: {who} ({username_target})\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Статус: Ожидает оплаты",
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda m: m.text == "Продать Stars")
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
        reply_markup=main_menu(), parse_mode="Markdown"
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
            f"✅ *{amount} ⭐️ = {total} грн*\n\n💳 Введите номер карты для выплаты:",
            reply_markup=main_menu(), parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_sell_stars_card, amount, total)
    except (ValueError, AttributeError):
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
        reply_markup=main_menu(), parse_mode="Markdown"
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
            parse_mode="Markdown",
            reply_markup=confirm_sell_stars_button(order_id, message.chat.id)
        )

# ========== CALLBACK: ПОДТВЕРЖДЕНИЕ ПРОДАЖИ STARS ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_sell_stars_"))
def confirm_sell_stars_order(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    parts = call.data.split("_")
    order_id = parts[3]
    user_id = int(parts[4])
    bot.send_message(
        user_id,
        f"🌟 *Продажа Telegram Stars выполнена!*\n\n"
        f"⭐️ Звёзды получены, выплата отправлена на вашу карту.\n"
        f"💎 Спасибо, что выбрали нас! ❤️",
        reply_markup=leave_comment_button(), parse_mode="Markdown"
    )
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
    bot.send_photo(
        message.chat.id, photo,
        caption=f"✅ Заказ #{order_id} получен!\n"
                f"⏳ Сотрудники проверят квитанцию.\n"
                f"⏰ Обычно 15–70 минут.\n"
                f"⚠️ Рабочее время: 08:00–00:00 (Киев).",
        reply_markup=main_menu()
    )
    for admin_id in ADMINS:
        bot.send_photo(
            admin_id, photo,
            caption=f"📸 КВИТАНЦИЯ по заказу #{order_id}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 Пользователь: {username}\n"
                    f"🆔 ID: {message.chat.id}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Клиент отправил квитанцию",
            reply_markup=confirm_button(order_id, message.chat.id, action_type="buy")
        )

# ========== CALLBACK: ПОДТВЕРЖДЕНИЕ ПОКУПКИ / ПРОДАЖИ ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") and not call.data.startswith("confirm_sell_stars_"))
def confirm_order(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    parts = call.data.split("_")
    
    if parts[1] == "sell": # confirm_sell_12345_67890
        order_id = parts[2]
        user_id = int(parts[3])
        bot.send_message(
            user_id,
            f"✅ *Выплата произведена!*\n\n"
            f"💰 Средства отправлены на вашу карту.\n"
            f"💎 Спасибо, что выбрали нас! ❤️",
            reply_markup=leave_comment_button(), parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, f"✅ Продажа #{order_id} подтверждена!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, f"✅ Продажа *#{order_id}* подтверждена, клиент уведомлён!", parse_mode="Markdown")
    else:
        order_id = parts[1]
        user_id = int(parts[2])
        order_data = user_orders.get(user_id)
        if order_data:
            crypto = order_data["crypto"]
            emoji = "💎" if crypto == "TON" else ("💵" if crypto == "USDT" else "⭐️")
        else:
            emoji, crypto = "💎", "криптовалюта"
        bot.send_message(
            user_id,
            f"✅ *Готово!*\n{emoji} {crypto} уже на кошельке\n💎 Спасибо, что выбрали нас! ❤️",
            reply_markup=leave_comment_button(), parse_mode="Markdown"
        )
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, f"✅ Заказ #{order_id} подтверждён!")
        bot.send_message(call.message.chat.id, f"✅ Заказ *#{order_id}* подтверждён, покупатель уведомлён!", parse_mode="Markdown")

# ========== ОТЗЫВ ==========

@bot.callback_query_handler(func=lambda call: call.data == "leave_comment")
def leave_comment_cb(call):
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
    global review_counter
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
    
    review_number = review_counter
    review_counter += 1
    
    caption = (
        f"📝 *Отзыв #{review_number}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Клиент: {username}\n"
        f"💰 Куплено: {amount} {crypto}\n"
        f"💬 Комментарий: {comment}\n"
        f"📅 Дата: {date}"
    )
    bot.send_message(message.chat.id, "⭐ Спасибо за ваш отзыв!", reply_markup=main_menu())
    bot.send_photo(REVIEWS_CHANNEL_ID, photo, caption=caption, parse_mode="Markdown")
    for admin_id in ADMINS:
        bot.send_photo(admin_id, photo, caption=f"💬 НОВЫЙ ОТЗЫВ\n{caption}", parse_mode="Markdown")

# ========== МЕНЮ ==========

def handle_menu(message):
    if message.text == "TON":
        ton_menu(message)
    elif message.text == "USDT":
        usdt_menu(message)
    elif message.text == "Купить Stars":
        buy_stars(message)
    elif message.text == "Продать Stars":
        sell_stars(message)
    elif message.text == "Профиль":
        profile(message)
    elif message.text == "Отзывы":
        reviews(message)
    elif message.text == "Поддержка":
        support(message)
    elif message.text == "Калькулятор":
        calculator(message)

@bot.message_handler(func=lambda m: m.text == "Профиль")
def profile(message):
    bot.send_message(message.chat.id, "👤 Ваш профиль...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "Отзывы")
def reviews(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Перейти в канал отзывов", url="https://t.me/BlackrStars"))
    bot.send_message(
        message.chat.id,
        "💬 *Отзывы наших клиентов*\n\n"
        "💎 Смотрите реальные скриншоты полученной криптовалюты и Telegram Stars в нашем канале:\n\n"
        "Спасибо, что выбираете нас! 💎",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "Поддержка")
def support(message):
    bot.send_message(message.chat.id, "🛠 Поддержка...", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "Калькулятор")
def calculator(message):
    bot.send_message(message.chat.id, "🧮 Калькулятор...", reply_markup=main_menu())

bot.infinity_polling()
