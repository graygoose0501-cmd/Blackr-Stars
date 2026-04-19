import telebot
import os
import random
import datetime
import pytz
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
BOT_USERNAME = "BlackrStars_Bot"  # ← замени на юзернейм бота без @

bot = telebot.TeleBot(TOKEN)

# ===== НАСТРОЙКА ВРЕМЕНИ =====
KYIV_TZ = pytz.timezone('Europe/Kiev')

def get_kyiv_time():
    return datetime.datetime.now(KYIV_TZ)

def format_kyiv_time(dt=None):
    if dt is None:
        dt = get_kyiv_time()
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date_only(dt=None):
    if dt is None:
        dt = get_kyiv_time()
    return dt.strftime("%d.%m.%Y")
# ==============================

# ===== КУРСЫ =====
TON_BUY_RATE = 72.3
TON_SELL_RATE = 72.3
USDT_BUY_RATE = 41.5
USDT_SELL_RATE = 41.5
STARS_BUY_RATE = 0.76
STARS_SELL_RATE = 0.76
STARS_MIN_SELL = 50
STARS_MIN_BUY = 50
# =================

# ===== РЕКВИЗИТЫ =====
CARD_NUMBER = "4441111057153763"
CARD_OWNER = "Євгеній К."
BANK_NAME = "Monobank🐾"
# =====================

ADMINS = [6227572453, 6794644473]
REVIEWS_CHANNEL_ID = -1003764314898
user_orders = {}

review_counter = 3761
order_counter = 1

# ===== ХРАНИЛИЩЕ ПОЛЬЗОВАТЕЛЕЙ =====
user_data = {}
total_stars_withdrawn = 0
pending_reviews = {}
support_tickets = {}
ticket_counter = 1

# ===== ОТЗЫВЫ: храним для каких заказов уже оставлен отзыв =====
reviewed_orders = set()

def get_or_create_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "reg_date": format_date_only(),
            "stars_balance": 0,
            "referrer_id": None,
            "referrals": [],
            "bought_stars": 0,
            "bought_ton": 0.0,
            "bought_usdt": 0.0,
        }
    return user_data[user_id]

def get_status(total_orders):
    if total_orders >= 50:
        return "💎 VIP клиент"
    elif total_orders >= 20:
        return "🥇 Золотой клиент"
    elif total_orders >= 10:
        return "🥈 Серебряный клиент"
    elif total_orders >= 3:
        return "🥉 Постоянный клиент"
    else:
        return "🥉 Обычный клиент"

def generate_order_number():
    global order_counter
    n = order_counter
    order_counter += 1
    return n

# ===== МЕНЮ =====
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

def handle_menu(message):
    t = message.text
    if t == "TON": ton_menu(message)
    elif t == "USDT": usdt_menu(message)
    elif t == "Купить Stars": buy_stars(message)
    elif t == "Продать Stars": sell_stars(message)
    elif t == "Профиль": profile(message)
    elif t == "Отзывы": reviews(message)
    elif t == "Поддержка": support(message)
    elif t == "Калькулятор": calculator(message)

# ===== INLINE КНОПКИ =====
def confirm_button(order_number, user_id, action_type="buy", order_info=""):
    markup = InlineKeyboardMarkup()
    if action_type == "buy":
        markup.add(InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_payment_{order_number}_{user_id}"))
    else:
        markup.add(InlineKeyboardButton("✅ Подтвердить выплату", callback_data=f"confirm_sell_{order_number}_{user_id}"))
    return markup

def confirm_delivery_button(order_number, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Подтвердить выдачу", callback_data=f"confirm_{order_number}_{user_id}"))
    return markup

def confirm_sell_stars_button(order_number, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить продажу Stars", callback_data=f"confirm_sell_stars_{order_number}_{user_id}"))
    return markup

def leave_comment_button(order_number):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Оставить отзыв", callback_data=f"leave_comment_{order_number}"))
    return markup

# ===== КЛАВИАТУРА ОЦЕНКИ — одна строка, как на фото =====
def rating_keyboard():
    markup = InlineKeyboardMarkup(row_width=5)
    markup.add(
        InlineKeyboardButton("⭐1", callback_data="rating_1"),
        InlineKeyboardButton("⭐2", callback_data="rating_2"),
        InlineKeyboardButton("⭐3", callback_data="rating_3"),
        InlineKeyboardButton("⭐4", callback_data="rating_4"),
        InlineKeyboardButton("⭐5", callback_data="rating_5"),
    )
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

def for_who_buttons(crypto_type):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("👤 Себе", callback_data=f"{crypto_type}_self"),
        InlineKeyboardButton("👥 Другу", callback_data=f"{crypto_type}_friend")
    )
    return markup

def sell_stars_inline_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⭐️ Продать Stars", callback_data="sell_stars_start"))
    return markup

def stars_amount_keyboard():
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
    markup.add(InlineKeyboardButton("✏️ Указать своё количество", callback_data="stars_custom"))
    return markup

def support_inline_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("✉️ Написать", callback_data="support_write"))
    return markup

def support_cancel_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("❌ Отменить", callback_data="support_cancel"))
    return markup

def admin_reply_keyboard(user_id, ticket_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💬 Ответить", callback_data=f"admin_reply_{user_id}_{ticket_id}"),
        InlineKeyboardButton("✅ Закрыть тикет", callback_data=f"admin_close_{user_id}_{ticket_id}")
    )
    return markup

def support_reply_keyboard(ticket_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("❌ Закрыть тикет", callback_data=f"user_close_{ticket_id}"))
    return markup

# ========== КАЛЬКУЛЯТОР — только Stars ==========
def calculator_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("⭐️ Stars → 💰 Грн", callback_data="calc_stars_to_uah"),
        InlineKeyboardButton("💰 Грн → ⭐️ Stars", callback_data="calc_uah_to_stars")
    )
    return markup

# ========== START ==========

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    user_id = message.chat.id
    is_new = user_id not in user_data
    ud = get_or_create_user(user_id)

    if is_new and len(args) > 1:
        try:
            referrer_id = int(args[1])
            if referrer_id != user_id and referrer_id in user_data:
                ud["referrer_id"] = referrer_id
                user_data[referrer_id]["stars_balance"] += 1
                user_data[referrer_id]["referrals"].append(user_id)
                ref_name = message.from_user.first_name or "Новый пользователь"
                try:
                    bot.send_message(
                        referrer_id,
                        f"🎉 *По вашей реферальной ссылке зарегистрировался новый пользователь!*\n\n"
                        f"👤 {ref_name}\n"
                        f"⭐️ Вам начислена *1 звезда* на баланс!\n"
                        f"💫 Текущий баланс: *{user_data[referrer_id]['stars_balance']} ⭐️*",
                        parse_mode="Markdown"
                    )
                except:
                    pass
        except (ValueError, IndexError):
            pass

    bot.send_message(
        user_id,
        "👋 Добро пожаловать!\n💼 Выберите действие:",
        reply_markup=main_menu()
    )

# ========== TON МЕНЮ ==========

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

@bot.callback_query_handler(func=lambda call: call.data == "ton_buy")
def buy_ton_start(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "💎 *Для кого покупаем TON?*",
                     reply_markup=for_who_buttons("ton"), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "ton_self")
def ton_for_self(call):
    bot.answer_callback_query(call.id)
    user_orders[call.message.chat.id] = {
        "ton_type": "self",
        "username_target": f"@{call.from_user.username}" if call.from_user.username else f"ID{call.message.chat.id}"
    }
    msg = bot.send_message(call.message.chat.id,
                           f"💎 Курс TON: {TON_BUY_RATE} грн\n\nВведите количество TON:",
                           reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_ton_amount)

@bot.callback_query_handler(func=lambda call: call.data == "ton_friend")
def ton_for_friend(call):
    bot.answer_callback_query(call.id)
    user_orders[call.message.chat.id] = {"ton_type": "friend"}
    msg = bot.send_message(call.message.chat.id,
                           "👥 Введите юзернейм друга:\n_(например: @username)_",
                           reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_ton_friend_username)

def process_ton_friend_username(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    user_orders[message.chat.id]["username_target"] = message.text
    msg = bot.send_message(message.chat.id,
                           f"💎 Курс TON: {TON_BUY_RATE} грн\n\nВведите количество TON:",
                           reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_amount(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * TON_BUY_RATE, 2)
        msg = bot.send_message(message.chat.id,
                               f"✅ {amount} TON = {total} грн\n\n👛 Введите адрес кошелька TON:",
                               reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_ton_wallet, amount, total)
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите число! Например: 1.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_ton_amount)

def process_ton_wallet(message, amount, total):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    wallet = message.text
    order_number = generate_order_number()
    now = format_kyiv_time()
    ton_data = user_orders.get(message.chat.id, {})
    who = "Другу" if ton_data.get("ton_type") == "friend" else "Себе"
    username_target = ton_data.get("username_target", wallet)

    user_orders[message.chat.id] = {
        "order_number": order_number, "amount": amount, "total": total,
        "wallet": wallet, "crypto": "TON", "date": now, "type": "buy"
    }
    ud = get_or_create_user(message.chat.id)
    ud["bought_ton"] = round(ud.get("bought_ton", 0) + amount, 4)

    bot.send_message(message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n🔢 Карта: `{CARD_NUMBER}`\n👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💎 Сумма: *{amount} TON*\n💰 К оплате: *{total} грн*\n"
        f"👛 Кошелёк: `{wallet}`\n👤 Для: {who} ({username_target})\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n📞 Заказ: *#{order_number}*",
        reply_markup=main_menu(), parse_mode="Markdown")

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_number} (TON)*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"💎 *{amount} TON* | 💵 *{total} грн*\n👛 `{wallet}`\n👤 {who} ({username_target})\n🕐 {now}\n⏳ Ожидает оплаты",
            parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "ton_sell")
def sell_ton_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
                           f"💸 *Продажа TON*\nКурс: {TON_SELL_RATE} грн\n\nВведите количество TON:",
                           reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_sell_ton_amount)

def process_sell_ton_amount(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * TON_SELL_RATE, 2)
        msg = bot.send_message(message.chat.id,
                               f"✅ *{amount} TON = {total} грн*\n\n💳 Введите номер карты:",
                               reply_markup=main_menu(), parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_sell_ton_card, amount, total)
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_sell_ton_amount)

def process_sell_ton_card(message, amount, total):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    card = message.text
    order_number = generate_order_number()
    now = format_kyiv_time()
    user_orders[message.chat.id] = {"order_number": order_number, "amount": amount,
                                     "total": total, "crypto": "TON", "type": "sell", "date": now}
    bot.send_message(message.chat.id,
        f"✅ *Заявка на продажу TON принята!*\n\n💰 Получите: *{total} грн*\n"
        f"💳 На карту: `{card}`\n📞 Заказ: *#{order_number}*\n\n⏳ Ожидайте подтверждения.",
        reply_markup=main_menu(), parse_mode="Markdown")
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🔄 *ПРОДАЖА TON #{order_number}*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"💎 *{amount} TON* | 💰 *{total} грн*\n💳 `{card}`\n🕐 {now}\n⏳ Ожидает выплаты",
            parse_mode="Markdown",
            reply_markup=confirm_button(order_number, message.chat.id, action_type="sell"))

# ========== USDT МЕНЮ ==========

@bot.message_handler(func=lambda m: m.text == "USDT")
def usdt_menu(message):
    bot.send_message(message.chat.id,
        f"💵 *USDT*\n\nКурс покупки: *{USDT_BUY_RATE} грн*\nКурс продажи: *{USDT_SELL_RATE} грн*\n\nВыберите действие:",
        reply_markup=usdt_inline_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "usdt_buy")
def buy_usdt_start(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "💵 *Для кого покупаем USDT?*",
                     reply_markup=for_who_buttons("usdt"), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "usdt_self")
def usdt_for_self(call):
    bot.answer_callback_query(call.id)
    user_orders[call.message.chat.id] = {
        "usdt_type": "self",
        "username_target": f"@{call.from_user.username}" if call.from_user.username else f"ID{call.message.chat.id}"
    }
    msg = bot.send_message(call.message.chat.id,
                           f"💵 Курс USDT: {USDT_BUY_RATE} грн\n\nВведите количество USDT:",
                           reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_usdt_amount)

@bot.callback_query_handler(func=lambda call: call.data == "usdt_friend")
def usdt_for_friend(call):
    bot.answer_callback_query(call.id)
    user_orders[call.message.chat.id] = {"usdt_type": "friend"}
    msg = bot.send_message(call.message.chat.id,
                           "👥 Введите юзернейм друга:\n_(например: @username)_",
                           reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_usdt_friend_username)

def process_usdt_friend_username(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    user_orders[message.chat.id]["username_target"] = message.text
    msg = bot.send_message(message.chat.id,
                           f"💵 Курс USDT: {USDT_BUY_RATE} грн\n\nВведите количество USDT:",
                           reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_amount(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * USDT_BUY_RATE, 2)
        msg = bot.send_message(message.chat.id,
            f"✅ {amount} USDT = {total} грн\n\n👛 Введите адрес кошелька TON для получения USDT:\n\n"
            f"⚠️ Комиссия: TON — 0,15 $", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_usdt_wallet, amount, total)
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите число! Например: 10.5", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_usdt_amount)

def process_usdt_wallet(message, amount, total):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    wallet = message.text
    order_number = generate_order_number()
    now = format_kyiv_time()
    usdt_data = user_orders.get(message.chat.id, {})
    who = "Другу" if usdt_data.get("usdt_type") == "friend" else "Себе"
    username_target = usdt_data.get("username_target", wallet)

    user_orders[message.chat.id] = {
        "order_number": order_number, "amount": amount, "total": total,
        "wallet": wallet, "crypto": "USDT", "date": now, "type": "buy"
    }
    ud = get_or_create_user(message.chat.id)
    ud["bought_usdt"] = round(ud.get("bought_usdt", 0) + amount, 4)

    bot.send_message(message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n🔢 Карта: `{CARD_NUMBER}`\n👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 Сумма: *{amount} USDT*\n💰 К оплате: *{total} грн*\n"
        f"👛 Кошелёк: `{wallet}`\n👤 Для: {who} ({username_target})\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📸 После оплаты отправьте квитанцию\n📞 Заказ: *#{order_number}*",
        reply_markup=main_menu(), parse_mode="Markdown")

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_number} (USDT)*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"💵 *{amount} USDT* | 💵 *{total} грн*\n👛 `{wallet}`\n👤 {who} ({username_target})\n🕐 {now}\n⏳ Ожидает оплаты",
            parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "usdt_sell")
def sell_usdt_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
                           f"💸 *Продажа USDT*\nКурс: {USDT_SELL_RATE} грн\n\nВведите количество USDT:",
                           reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_sell_usdt_amount)

def process_sell_usdt_amount(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = float(message.text.replace(",", "."))
        total = round(amount * USDT_SELL_RATE, 2)
        msg = bot.send_message(message.chat.id,
                               f"✅ *{amount} USDT = {total} грн*\n\n💳 Введите номер карты:",
                               reply_markup=main_menu(), parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_sell_usdt_card, amount, total)
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_sell_usdt_amount)

def process_sell_usdt_card(message, amount, total):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    card = message.text
    order_number = generate_order_number()
    now = format_kyiv_time()
    user_orders[message.chat.id] = {"order_number": order_number, "amount": amount,
                                     "total": total, "crypto": "USDT", "type": "sell", "date": now}
    bot.send_message(message.chat.id,
        f"✅ *Заявка на продажу USDT принята!*\n\n💰 Получите: *{total} грн*\n"
        f"💳 На карту: `{card}`\n📞 Заказ: *#{order_number}*\n\n⏳ Ожидайте подтверждения.",
        reply_markup=main_menu(), parse_mode="Markdown")
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🔄 *ПРОДАЖА USDT #{order_number}*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"💵 *{amount} USDT* | 💰 *{total} грн*\n💳 `{card}`\n🕐 {now}\n⏳ Ожидает выплаты",
            parse_mode="Markdown",
            reply_markup=confirm_button(order_number, message.chat.id, action_type="sell"))

# ========== STARS КУПИТЬ ==========

@bot.message_handler(func=lambda m: m.text == "Купить Stars")
def buy_stars(message):
    bot.send_message(message.chat.id, "⭐️ *Для кого покупаем Telegram Stars?*",
                     reply_markup=for_who_buttons("stars"), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "stars_self")
def stars_for_self(call):
    bot.answer_callback_query(call.id)
    user_orders[call.message.chat.id] = {
        "stars_type": "self",
        "username_target": f"@{call.from_user.username}" if call.from_user.username else f"ID{call.message.chat.id}",
        "awaiting_stars_amount": True
    }
    bot.send_message(call.message.chat.id,
                     f"⭐️ Выберите количество Stars или укажите своё\n_(минимум {STARS_MIN_BUY})_:",
                     reply_markup=stars_amount_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "stars_friend")
def stars_for_friend(call):
    bot.answer_callback_query(call.id)
    user_orders[call.message.chat.id] = {"stars_type": "friend"}
    msg = bot.send_message(call.message.chat.id,
                           "👥 Введите юзернейм друга:\n_(например: @username)_",
                           reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_stars_friend_username)

def process_stars_friend_username(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    user_orders[message.chat.id] = {
        "stars_type": "friend",
        "username_target": message.text,
        "awaiting_stars_amount": True
    }
    bot.send_message(message.chat.id,
                     f"⭐️ Выберите количество Stars или укажите своё\n_(минимум {STARS_MIN_BUY})_:",
                     reply_markup=stars_amount_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("stars_qty_"))
def stars_qty_selected(call):
    bot.answer_callback_query(call.id)
    amount = int(call.data.split("_")[2])
    order_data = user_orders.get(call.message.chat.id, {})
    finish_stars_order(call.message, amount,
                       order_data.get("stars_type", "self"),
                       order_data.get("username_target", ""))

@bot.callback_query_handler(func=lambda call: call.data == "stars_custom")
def stars_custom_amount(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
                           f"✏️ Введите количество Stars _(минимум {STARS_MIN_BUY})_:",
                           reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_stars_custom_amount)

def process_stars_custom_amount(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = int(float(message.text.replace(",", ".")))
        if amount < STARS_MIN_BUY:
            msg = bot.send_message(message.chat.id,
                                   f"❌ Минимум {STARS_MIN_BUY} Stars! Введите ещё раз:",
                                   reply_markup=main_menu())
            bot.register_next_step_handler(msg, process_stars_custom_amount)
            return
        order_data = user_orders.get(message.chat.id, {})
        finish_stars_order(message, amount,
                           order_data.get("stars_type", "self"),
                           order_data.get("username_target", ""))
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите целое число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_stars_custom_amount)

def finish_stars_order(message, amount, stars_type, username_target):
    order_number = generate_order_number()
    now = format_kyiv_time()
    who = "Другу" if stars_type == "friend" else "Себе"
    total = round(amount * STARS_BUY_RATE, 2)

    user_orders[message.chat.id] = {
        "order_number": order_number, "amount": amount, "total": total,
        "wallet": username_target, "crypto": "Stars", "date": now, "type": "buy"
    }
    ud = get_or_create_user(message.chat.id)
    ud["bought_stars"] = ud.get("bought_stars", 0) + amount

    bot.send_message(message.chat.id,
        f"💳 *Банк {BANK_NAME}*\n🔢 Карта: `{CARD_NUMBER}`\n👤 Получатель: {CARD_OWNER}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⭐️ Stars: *{amount}* — *{total} грн*\n"
        f"👤 Для: {who} (`{username_target}`)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 К оплате: *{total} грн*\n"
        f"📸 После оплаты отправьте квитанцию\n📞 Заказ: *#{order_number}*",
        reply_markup=main_menu(), parse_mode="Markdown")

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🆕 *НОВЫЙ ЗАКАЗ #{order_number} (Stars)*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"⭐️ *{amount} Stars* — *{total} грн*\n👤 {who} ({username_target})\n🕐 {now}\n⏳ Ожидает оплаты",
            parse_mode="Markdown")

# ========== STARS ПРОДАТЬ ==========

@bot.message_handler(func=lambda m: m.text == "Продать Stars")
def sell_stars(message):
    bot.send_message(message.chat.id,
        f"🌟 *Хочешь продать свои звёзды Telegram?*\n\n"
        f"💰 Курс: 1⭐️ = *{STARS_SELL_RATE} грн*\n"
        f"📦 Минимум — *{STARS_MIN_SELL} звёзд*\n\n"
        f"🚀 За *1000⭐️* получишь *{round(STARS_SELL_RATE * 1000)} грн* за 5 минут!",
        reply_markup=sell_stars_inline_button(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "sell_stars_start")
def sell_stars_start(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
                           f"⭐️ Сколько Stars хотите продать?\n_(минимум {STARS_MIN_SELL})_",
                           reply_markup=main_menu(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_sell_stars_amount)

def process_sell_stars_amount(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = int(float(message.text.replace(",", ".")))
        if amount < STARS_MIN_SELL:
            msg = bot.send_message(message.chat.id,
                                   f"❌ Минимум {STARS_MIN_SELL} Stars! Введите ещё раз:",
                                   reply_markup=main_menu())
            bot.register_next_step_handler(msg, process_sell_stars_amount)
            return
        total = round(amount * STARS_SELL_RATE, 2)
        msg = bot.send_message(message.chat.id,
                               f"✅ *{amount} ⭐️ = {total} грн*\n\n💳 Введите номер карты для выплаты:",
                               reply_markup=main_menu(), parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_sell_stars_card, amount, total)
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите целое число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_sell_stars_amount)

def process_sell_stars_card(message, amount, total):
    global total_stars_withdrawn
    if message.text in MENU_BUTTONS: handle_menu(message); return
    card = message.text
    order_number = generate_order_number()
    now = format_kyiv_time()
    total_stars_withdrawn += amount

    user_orders[message.chat.id] = {
        "order_number": order_number, "amount": amount, "total": total,
        "crypto": "Stars", "type": "sell", "date": now
    }

    bot.send_message(message.chat.id,
        f"✅ *Заявка принята!*\n\n⭐️ Продаёте: *{amount} Stars*\n"
        f"💰 Получите: *{total} грн*\n💳 На карту: `{card}`\n"
        f"📞 Заказ: *#{order_number}*\n\n⏳ Ожидайте подтверждения.",
        reply_markup=main_menu(), parse_mode="Markdown")

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    for admin_id in ADMINS:
        bot.send_message(admin_id,
            f"🌟 *ПРОДАЖА STARS #{order_number}*\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n"
            f"⭐️ *{amount} Stars* | 💰 *{total} грн*\n💳 `{card}`\n🕐 {now}\n⏳ Ожидает обработки",
            parse_mode="Markdown",
            reply_markup=confirm_sell_stars_button(order_number, message.chat.id))

# ========== ПОДТВЕРЖДЕНИЯ ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_sell_stars_"))
def confirm_sell_stars_order(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    parts = call.data.split("_")
    order_number = parts[3]
    user_id = int(parts[4])

    order_data = user_orders.get(user_id, {})
    amount = order_data.get("amount", "?")
    total = order_data.get("total", "?")

    bot.send_message(user_id,
        f"🌟 *Продажа Telegram Stars выполнена!*\n\n"
        f"⭐️ Звёзды получены, выплата отправлена на вашу карту.\n"
        f"💎 Спасибо, что выбрали нас! ❤️",
        reply_markup=leave_comment_button(order_number), parse_mode="Markdown")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Продажа Stars #{order_number} подтверждена!")
    bot.send_message(call.message.chat.id,
        f"✅ Продажа Stars *#{order_number}* подтверждена!\n"
        f"⭐️ *{amount} Stars* | 💰 *{total} грн*", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_payment_"))
def confirm_payment(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    parts = call.data.split("_")
    order_number = parts[2]
    user_id = int(parts[3])

    order_data = user_orders.get(user_id, {})
    amount = order_data.get("amount", "?")
    total = order_data.get("total", "?")
    crypto = order_data.get("crypto", "?")

    bot.send_message(user_id,
        f"✅ *Оплата прошла успешно!*\n\n"
        f"⏳ Ожидайте выдачи вашего заказа.",
        parse_mode="Markdown")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Оплата #{order_number} подтверждена!")
    bot.send_message(call.message.chat.id,
        f"✅ Оплата *#{order_number}* подтверждена!\n"
        f"{'⭐️' if crypto == 'Stars' else ('💎' if crypto == 'TON' else '💵')} *{amount} {crypto}* | 💰 *{total} грн*\n\n"
        f"Теперь подтвердите выдачу:",
        reply_markup=confirm_delivery_button(order_number, user_id),
        parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") and not call.data.startswith("confirm_sell_stars_") and not call.data.startswith("confirm_sell_") and not call.data.startswith("confirm_payment_") and not call.data.startswith("confirm_ref_"))
def confirm_order(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    parts = call.data.split("_")
    if parts[1] == "sell":
        order_number = parts[2]
        user_id = int(parts[3])

        order_data = user_orders.get(user_id, {})
        amount = order_data.get("amount", "?")
        total = order_data.get("total", "?")
        crypto = order_data.get("crypto", "?")

        bot.send_message(user_id,
            f"✅ *Выплата произведена!*\n\n💰 Средства отправлены на вашу карту.\n💎 Спасибо, что выбрали нас! ❤️",
            reply_markup=leave_comment_button(order_number), parse_mode="Markdown")
        bot.answer_callback_query(call.id, f"✅ Продажа #{order_number} подтверждена!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id,
            f"✅ Продажа *#{order_number}* подтверждена!\n"
            f"💎 *{amount} {crypto}* | 💰 *{total} грн*", parse_mode="Markdown")
    else:
        order_number = parts[1]
        user_id = int(parts[2])
        order_data = user_orders.get(user_id)

        if order_data:
            crypto = order_data["crypto"]
            amount = order_data.get("amount", "?")
            total = order_data.get("total", "?")
            if crypto == "Stars":
                emoji = "⭐️"
                done_text = (
                    f"✅ *Готово!*\n"
                    f"⭐️ Звёзды уже выданы\n"
                    f"💎 Спасибо, что выбрали нас! ❤️"
                )
            elif crypto == "TON":
                emoji = "💎"
                done_text = (
                    f"✅ *Готово!*\n"
                    f"💎 TON уже на кошельке\n"
                    f"💎 Спасибо, что выбрали нас! ❤️"
                )
            else:
                emoji = "💵"
                done_text = (
                    f"✅ *Готово!*\n"
                    f"💵 USDT уже на кошельке\n"
                    f"💎 Спасибо, что выбрали нас! ❤️"
                )
        else:
            emoji, crypto, amount, total = "💎", "криптовалюта", "?", "?"
            done_text = (
                f"✅ *Готово!*\n"
                f"💎 Криптовалюта уже на кошельке\n"
                f"💎 Спасибо, что выбрали нас! ❤️"
            )

        bot.send_message(user_id, done_text,
            reply_markup=leave_comment_button(order_number), parse_mode="Markdown")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, f"✅ Выдача #{order_number} подтверждена!")
        bot.send_message(call.message.chat.id,
            f"🚀 Выдача *#{order_number}* подтверждена!\n"
            f"{emoji} *{amount} {crypto}* | 💰 *{total} грн*", parse_mode="Markdown")

# ========== КВИТАНЦИЯ ==========

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    review_data = pending_reviews.get(message.chat.id, {})
    if review_data.get("status") == "waiting_photo":
        save_comment_photo(message)
        return

    order_data = user_orders.get(message.chat.id)
    order_number = order_data["order_number"] if order_data else "??????"
    photo = message.photo[-1].file_id
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"

    if order_data:
        crypto = order_data.get("crypto", "")
        amount = order_data.get("amount", "")
        total = order_data.get("total", "")
        if crypto == "Stars":
            order_info = f"⭐️ *{amount} Stars* — *{total} грн*"
        elif crypto == "TON":
            order_info = f"💎 *{amount} TON* — *{total} грн*"
        else:
            order_info = f"💵 *{amount} USDT* — *{total} грн*"
    else:
        order_info = ""

    bot.send_photo(message.chat.id, photo,
        caption=f"✅ Заказ #{order_number} получен!\n⏳ Проверка 15–70 минут.\n⚠️ Рабочее время: 08:00–00:00 (Киев).",
        reply_markup=main_menu())
    for admin_id in ADMINS:
        bot.send_photo(admin_id, photo,
            caption=f"📸 КВИТАНЦИЯ #{order_number}\n👤 {username} | ID: {message.chat.id}\n{order_info}",
            reply_markup=confirm_button(order_number, message.chat.id, action_type="buy"),
            parse_mode="Markdown")

# ========== ОТЗЫВ ==========

@bot.callback_query_handler(func=lambda call: call.data.startswith("leave_comment_"))
def leave_comment_cb(call):
    bot.answer_callback_query(call.id)
    order_number_str = call.data.split("leave_comment_")[1]

    if order_number_str in reviewed_orders:
        bot.send_message(call.message.chat.id,
            "❌ *Вы уже оставили отзыв к этому заказу.*\n\nОтзыв можно оставить только один раз.",
            parse_mode="Markdown")
        return

    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass

    pending_reviews[call.message.chat.id] = {
        "status": "waiting_rating",
        "order_number": order_number_str
    }

    # Отправляем сообщение с оценкой и сохраняем его message_id для последующего удаления
    sent = bot.send_message(
        call.message.chat.id,
        "⭐️ *Выберите оценку:*",
        reply_markup=rating_keyboard(),
        parse_mode="Markdown"
    )
    # Сохраняем message_id чтобы потом удалить
    pending_reviews[call.message.chat.id]["rating_msg_id"] = sent.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith("rating_"))
def rating_selected(call):
    bot.answer_callback_query(call.id)
    rating = int(call.data.split("_")[1])
    chat_id = call.message.chat.id
    review_data = pending_reviews.get(chat_id, {})
    review_data["rating"] = rating
    review_data["status"] = "waiting_text"
    pending_reviews[chat_id] = review_data

    # Удаляем сообщение с кнопками оценки
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass

    msg = bot.send_message(chat_id, "✍️ Напишите ваш отзыв:", reply_markup=main_menu())
    bot.register_next_step_handler(msg, save_comment_text)

def save_comment_text(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    review_data = pending_reviews.get(message.chat.id, {})
    review_data["comment"] = message.text
    review_data["status"] = "waiting_photo"
    pending_reviews[message.chat.id] = review_data
    skip_markup = InlineKeyboardMarkup()
    skip_markup.add(InlineKeyboardButton("⏭ Пропустить фото", callback_data="skip_review_photo"))
    bot.send_message(message.chat.id, "📸 Отправьте фото для отзыва или пропустите:", reply_markup=skip_markup)

@bot.callback_query_handler(func=lambda call: call.data == "skip_review_photo")
def skip_review_photo(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
    review_data = pending_reviews.get(call.message.chat.id, {})
    if not review_data:
        bot.send_message(call.message.chat.id, "❌ Ошибка! Начните заново.", reply_markup=main_menu())
        return
    save_comment_no_photo(call.message.chat.id, call.from_user)

def build_review_stats(user_id, order_data):
    """Формирует строку статистики для отзыва: текущий заказ + всего куплено"""
    ud = user_data.get(user_id, {})
    bought_stars_total = ud.get("bought_stars", 0)
    bought_ton_total = ud.get("bought_ton", 0.0)
    bought_usdt_total = ud.get("bought_usdt", 0.0)

    crypto = order_data.get("crypto", "")
    amount = order_data.get("amount", 0)

    lines = []

    # Текущий заказ
    if crypto == "Stars":
        lines.append(f"⭐️ Куплено Stars: *{amount}*")
    elif crypto == "TON":
        lines.append(f"💎 Куплено TON: *{amount}*")
    elif crypto == "USDT":
        lines.append(f"💵 Куплено USDT: *{amount}*")

    # Всего накопительно — только для того же типа что и текущий заказ
    if crypto == "Stars" and bought_stars_total > 0:
        lines.append(f"⭐️ Куплено Stars всего: *{bought_stars_total}*")
    elif crypto == "TON" and bought_ton_total > 0:
        lines.append(f"💎 Куплено TON всего: *{bought_ton_total}*")
    elif crypto == "USDT" and bought_usdt_total > 0:
        lines.append(f"💵 Куплено USDT всего: *{bought_usdt_total}*")

    return "\n".join(lines) if lines else "—"

def build_caption(review_number, client_name, comment, date, stars_display, stats):
    return (
        f"📊 *Отзыв №{review_number}*\n"
        f"🆔 Клиент: {client_name}\n"
        f"📝 Комментарий: {comment}\n"
        f"📅 Дата: {date}\n"
        f"🌟 Оценка: {stars_display}\n\n"
        f"📈 Статистика покупок:\n{stats}\n\n"
        f"🎯 FluxStar Bot — ваш надёжный партнёр! 🚀"
    )

def save_comment_no_photo(chat_id, user_obj):
    """Сохранение отзыва без фото"""
    global review_counter
    review_data = pending_reviews.get(chat_id, {})
    if not review_data:
        bot.send_message(chat_id, "❌ Ошибка! Начните заново.", reply_markup=main_menu())
        return

    rating = review_data.get("rating", 5)
    comment = review_data.get("comment", "")
    order_number_str = review_data.get("order_number", "")
    user_name = user_obj.first_name or "Клиент"
    date = format_date_only()

    if order_number_str:
        reviewed_orders.add(order_number_str)

    review_number = review_counter
    review_counter += 1

    stars_display = "⭐️" * rating
    order_data = user_orders.get(chat_id, {})
    stats = build_review_stats(chat_id, order_data)

    username_display = user_obj.username
    client_name = username_display if username_display else user_name

    caption = build_caption(review_number, client_name, comment, date, stars_display, stats)

    bot.send_message(chat_id, "⭐ Спасибо за ваш отзыв!", reply_markup=main_menu())
    bot.send_message(REVIEWS_CHANNEL_ID, caption, parse_mode="Markdown")
    for admin_id in ADMINS:
        bot.send_message(admin_id, f"💬 НОВЫЙ ОТЗЫВ\n{caption}", parse_mode="Markdown")

    if chat_id in pending_reviews:
        del pending_reviews[chat_id]

def save_comment_photo(message):
    global review_counter
    review_data = pending_reviews.get(message.chat.id, {})
    if not review_data:
        bot.send_message(message.chat.id, "❌ Ошибка! Начните заново.", reply_markup=main_menu()); return

    rating = review_data.get("rating", 5)
    comment = review_data.get("comment", "")
    order_number_str = review_data.get("order_number", "")
    user_name = message.from_user.first_name or "Клиент"
    date = format_date_only()
    photo = message.photo[-1].file_id

    if order_number_str:
        reviewed_orders.add(order_number_str)

    review_number = review_counter
    review_counter += 1

    stars_display = "⭐️" * rating
    order_data = user_orders.get(message.chat.id, {})
    stats = build_review_stats(message.chat.id, order_data)

    username_display = message.from_user.username
    client_name = username_display if username_display else user_name

    caption = build_caption(review_number, client_name, comment, date, stars_display, stats)

    bot.send_message(message.chat.id, "⭐ Спасибо за ваш отзыв!", reply_markup=main_menu())
    bot.send_photo(REVIEWS_CHANNEL_ID, photo, caption=caption, parse_mode="Markdown")
    for admin_id in ADMINS:
        bot.send_photo(admin_id, photo, caption=f"💬 НОВЫЙ ОТЗЫВ\n{caption}", parse_mode="Markdown")

    if message.chat.id in pending_reviews:
        del pending_reviews[message.chat.id]

# ========== ПРОФИЛЬ ==========

@bot.message_handler(func=lambda m: m.text == "Профиль")
def profile(message):
    user_id = message.chat.id
    ud = get_or_create_user(user_id)

    user_obj = message.from_user
    name = user_obj.first_name or "Не указано"
    username_str = f"@{user_obj.username}" if user_obj.username else "не указан"

    reg_date = ud.get("reg_date", format_date_only())
    stars_balance = ud.get("stars_balance", 0)
    referrals_count = len(ud.get("referrals", []))
    bought_stars = ud.get("bought_stars", 0)
    bought_ton = ud.get("bought_ton", 0.0)
    bought_usdt = ud.get("bought_usdt", 0.0)

    total_orders = (1 if bought_stars > 0 else 0) + (1 if bought_ton > 0 else 0) + (1 if bought_usdt > 0 else 0)
    status = get_status(total_orders)

    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    profile_text = (
        f"👤 *Ваш профиль* 🌟\n\n"
        f"🆔 ID: `{user_id}` 🔑\n"
        f"👤 Имя пользователя: {username_str} 📛\n"
        f"📅 Дата регистрации: {reg_date} ⏰\n\n"
        f"⭐️ Реферальный баланс: *{stars_balance} ⭐️* ✨\n"
        f"👥 Приглашено друзей: *{referrals_count}*\n"
        f"🔗 Ваша ссылка: `{ref_link}`\n\n"
        f"🏆 Статус: {status}\n\n"
        f"📊 *Статистика покупок:* 📈\n"
        f"⭐️ Купленные звёзды: *{bought_stars}* ✨\n"
        f"💎 Купленные TON: *{bought_ton}* 🚀\n"
        f"💵 Купленные USDT: *{bought_usdt}* 💸"
    )

    profile_markup = InlineKeyboardMarkup()
    profile_markup.add(InlineKeyboardButton("⭐️ Вывести реферальные звёзды", callback_data="ref_withdraw_menu"))
    bot.send_message(user_id, profile_text, reply_markup=profile_markup, parse_mode="Markdown")

# ========== ВЫВОД РЕФЕРАЛЬНЫХ ЗВЁЗД ==========

def ref_withdraw_amounts_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("15 ⭐️", callback_data="ref_withdraw_15"),
        InlineKeyboardButton("25 ⭐️", callback_data="ref_withdraw_25"),
    )
    markup.row(
        InlineKeyboardButton("50 ⭐️", callback_data="ref_withdraw_50"),
        InlineKeyboardButton("100 ⭐️", callback_data="ref_withdraw_100"),
    )
    markup.add(InlineKeyboardButton("❌ Отмена", callback_data="ref_withdraw_cancel"))
    return markup

def confirm_ref_withdraw_button(order_number, user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить вывод Stars", callback_data=f"confirm_ref_withdraw_{order_number}_{user_id}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "ref_withdraw_menu")
def ref_withdraw_menu(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    ud = get_or_create_user(user_id)
    balance = ud.get("stars_balance", 0)
    bot.send_message(
        user_id,
        f"⭐️ *Вывод реферальных звёзд*\n\n"
        f"💫 Ваш баланс: *{balance} ⭐️*\n\n"
        f"Выберите количество для вывода:",
        reply_markup=ref_withdraw_amounts_keyboard(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "ref_withdraw_cancel")
def ref_withdraw_cancel(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("❌ Вывод отменён.", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ref_withdraw_") and "_" in call.data and call.data.split("_")[2].isdigit())
def ref_withdraw_amount(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    ud = get_or_create_user(user_id)
    balance = ud.get("stars_balance", 0)
    amount = int(call.data.split("_")[2])

    if balance < amount:
        bot.send_message(
            user_id,
            f"❌ *Недостаточно звёзд!*\n\n"
            f"💫 Ваш баланс: *{balance} ⭐️*\n"
            f"🔢 Запрошено: *{amount} ⭐️*\n\n"
            f"Пригласите больше друзей по реферальной ссылке!",
            parse_mode="Markdown"
        )
        return

    bot.edit_message_text(
        f"⭐️ Вывод *{amount} ⭐️*\n\n👤 Введите юзернейм Telegram для получения звёзд:\n_(например: @username)_",
        user_id, call.message.message_id, parse_mode="Markdown"
    )
    msg = bot.send_message(user_id, "✏️ Введите юзернейм:", reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_ref_withdraw_username, amount)

def process_ref_withdraw_username(message, amount):
    if message.text in MENU_BUTTONS:
        handle_menu(message)
        return
    user_id = message.chat.id
    ud = get_or_create_user(user_id)
    balance = ud.get("stars_balance", 0)

    if balance < amount:
        bot.send_message(user_id,
            f"❌ *Недостаточно звёзд!* Баланс: *{balance} ⭐️*",
            reply_markup=main_menu(), parse_mode="Markdown")
        return

    username_target = message.text
    order_number = generate_order_number()
    now = format_kyiv_time()
    ud["stars_balance"] -= amount

    user_orders[user_id] = {
        "order_number": order_number, "amount": amount,
        "total": 0, "wallet": username_target,
        "crypto": "Stars", "date": now, "type": "ref_withdraw"
    }

    bot.send_message(
        user_id,
        f"✅ *Заявка на вывод принята!*\n\n"
        f"⭐️ Выводите: *{amount} Stars*\n"
        f"👤 На аккаунт: `{username_target}`\n"
        f"📞 Номер заказа: *#{order_number}*\n\n"
        f"💫 Остаток на балансе: *{ud['stars_balance']} ⭐️*\n\n"
        f"⏳ Stars будут отправлены в ближайшее время.",
        reply_markup=main_menu(), parse_mode="Markdown"
    )

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            f"⭐️ *ВЫВОД РЕФ. STARS #{order_number}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 {username} | 🆔 `{user_id}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⭐️ Количество: *{amount} Stars*\n"
            f"👤 На аккаунт: `{username_target}`\n"
            f"🕐 {now}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏳ Ожидает отправки",
            parse_mode="Markdown",
            reply_markup=confirm_ref_withdraw_button(order_number, user_id)
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_ref_withdraw_"))
def confirm_ref_withdraw(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    parts = call.data.split("_")
    order_number = parts[3]
    user_id = int(parts[4])
    bot.send_message(
        user_id,
        f"🎉 *Реферальные звёзды отправлены!*\n\n"
        f"⭐️ Stars зачислены на ваш аккаунт.\n"
        f"💎 Спасибо за использование нашего сервиса! ❤️",
        reply_markup=leave_comment_button(order_number), parse_mode="Markdown"
    )
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Вывод Stars #{order_number} подтверждён!")
    bot.send_message(call.message.chat.id,
                     f"✅ Вывод Stars *#{order_number}* подтверждён, клиент уведомлён!",
                     parse_mode="Markdown")

# ========== ОТЗЫВЫ ==========

@bot.message_handler(func=lambda m: m.text == "Отзывы")
def reviews(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Перейти в канал отзывов", url="https://t.me/BlackrStars"))
    bot.send_message(message.chat.id,
        "💬 *Отзывы наших клиентов*\n\n"
        "💎 Смотрите реальные скриншоты полученной криптовалюты и Telegram Stars в нашем канале:\n\n"
        "Спасибо, что выбираете нас! 💎",
        reply_markup=markup, parse_mode="Markdown")

# ========== ПОДДЕРЖКА ==========

@bot.message_handler(func=lambda m: m.text == "Поддержка")
def support(message):
    bot.send_message(message.chat.id,
        "😊 *Есть вопросы?* Нажимай «Написать» — мы с радостью поможем! 😺\n\n"
        "🤔 *Частые вопросы:*\n\n"
        "1️⃣ *Сколько ждать выполнение заказа?*\n"
        "— Обычно от 5 до 70 минут.",
        reply_markup=support_inline_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "support_write")
def support_write(call):
    global ticket_counter
    bot.answer_callback_query(call.id)
    ticket_id = ticket_counter
    ticket_counter += 1
    support_tickets[call.message.chat.id] = {
        "ticket_id": ticket_id, "status": "waiting_message",
        "user_id": call.message.chat.id,
        "username": f"@{call.from_user.username}" if call.from_user.username else f"ID: {call.message.chat.id}"
    }
    msg = bot.send_message(call.message.chat.id,
        f"📩 *Тикет #{ticket_id}*\n\nВведите ваш запрос:",
        reply_markup=support_cancel_keyboard(), parse_mode="Markdown")
    support_tickets[call.message.chat.id]["message_id"] = msg.message_id

@bot.callback_query_handler(func=lambda call: call.data == "support_cancel")
def support_cancel(call):
    bot.answer_callback_query(call.id)
    if call.message.chat.id in support_tickets:
        del support_tickets[call.message.chat.id]
    bot.edit_message_text("❌ *Запрос отменен*", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.send_message(call.message.chat.id,
        "😊 *Есть вопросы?* Нажимай «Написать»!\n\n1️⃣ *Сколько ждать заказ?*\n— От 5 до 70 минут.",
        reply_markup=support_inline_keyboard(), parse_mode="Markdown")

@bot.message_handler(
    func=lambda m: m.chat.id in support_tickets and support_tickets[m.chat.id].get("status") == "waiting_message",
    content_types=['text', 'photo', 'document'])
def handle_support_message(message):
    ticket_data = support_tickets[message.chat.id]
    ticket_id = ticket_data["ticket_id"]
    username = ticket_data["username"]
    try:
        bot.edit_message_reply_markup(message.chat.id, ticket_data["message_id"], reply_markup=None)
    except: pass
    bot.send_message(message.chat.id,
        f"✅ *Тикет #{ticket_id} отправлен!*\n⏳ Ожидайте ответа.",
        reply_markup=main_menu(), parse_mode="Markdown")
    admin_msg = (f"📩 *НОВЫЙ ТИКЕТ #{ticket_id}*\n━━━━━━━━━━━━━━━━━━\n"
                 f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n")
    for admin_id in ADMINS:
        try:
            if message.content_type == 'text':
                bot.send_message(admin_id, admin_msg + f"💬 *Сообщение:*\n{message.text}",
                                 reply_markup=admin_reply_keyboard(message.chat.id, ticket_id), parse_mode="Markdown")
            elif message.content_type == 'photo':
                caption = message.caption or ""
                bot.send_photo(admin_id, message.photo[-1].file_id,
                               caption=admin_msg + "📸 Фото" + (f"\n{caption}" if caption else ""),
                               reply_markup=admin_reply_keyboard(message.chat.id, ticket_id), parse_mode="Markdown")
            elif message.content_type == 'document':
                bot.send_document(admin_id, message.document.file_id,
                                  caption=admin_msg + f"📎 `{message.document.file_name}`",
                                  reply_markup=admin_reply_keyboard(message.chat.id, ticket_id), parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка: {e}")
    support_tickets[message.chat.id]["status"] = "waiting_reply"

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_reply_"))
def admin_reply_start(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    bot.answer_callback_query(call.id)
    parts = call.data.split("_")
    user_id = int(parts[2])
    ticket_id = int(parts[3])
    msg = bot.send_message(call.message.chat.id,
                           f"💬 *Ответ на тикет #{ticket_id}*\n\nВведите ответ:",
                           parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_admin_reply, user_id, ticket_id)

def process_admin_reply(message, user_id, ticket_id):
    try:
        bot.send_message(user_id,
            f"💬 *Поддержка | Тикет #{ticket_id}*\n\n{message.text}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n📩 Чтобы ответить — напишите в этот чат.",
            parse_mode="Markdown", reply_markup=support_reply_keyboard(ticket_id))
        support_tickets[user_id] = {"ticket_id": ticket_id, "status": "waiting_user_reply", "user_id": user_id}
        bot.send_message(message.chat.id, f"✅ *Ответ отправлен!* Тикет #{ticket_id}", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ *Ошибка!* Пользователь заблокировал бота.", parse_mode="Markdown")

@bot.message_handler(
    func=lambda m: m.chat.id in support_tickets and support_tickets[m.chat.id].get("status") == "waiting_user_reply",
    content_types=['text', 'photo', 'document'])
def handle_user_reply(message):
    ticket_data = support_tickets[message.chat.id]
    ticket_id = ticket_data["ticket_id"]
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.chat.id}"
    support_tickets[message.chat.id]["status"] = "waiting_reply"
    bot.send_message(message.chat.id, f"✅ *Ответ отправлен!* Тикет #{ticket_id}", parse_mode="Markdown")
    admin_msg = (f"📩 *ОТВЕТ | Тикет #{ticket_id}*\n━━━━━━━━━━━━━━━━━━\n"
                 f"👤 {username} | 🆔 `{message.chat.id}`\n━━━━━━━━━━━━━━━━━━\n")
    for admin_id in ADMINS:
        try:
            if message.content_type == 'text':
                bot.send_message(admin_id, admin_msg + f"💬 {message.text}",
                                 reply_markup=admin_reply_keyboard(message.chat.id, ticket_id), parse_mode="Markdown")
            elif message.content_type == 'photo':
                bot.send_photo(admin_id, message.photo[-1].file_id, caption=admin_msg + "📸 Фото",
                               reply_markup=admin_reply_keyboard(message.chat.id, ticket_id), parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_close_"))
def admin_close_ticket(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    parts = call.data.split("_")
    user_id = int(parts[2])
    ticket_id = int(parts[3])
    if user_id in support_tickets: del support_tickets[user_id]
    try:
        bot.send_message(user_id, f"🔒 *Тикет #{ticket_id} закрыт*\n\nСпасибо за обращение!", parse_mode="Markdown")
    except: pass
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, f"✅ Тикет #{ticket_id} закрыт!")
    bot.send_message(call.message.chat.id, f"✅ *Тикет #{ticket_id} закрыт!*", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("user_close_"))
def user_close_ticket(call):
    ticket_id = int(call.data.split("_")[2])
    if call.message.chat.id in support_tickets: del support_tickets[call.message.chat.id]
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, "✅ Тикет закрыт!")
    bot.send_message(call.message.chat.id, f"🔒 *Тикет #{ticket_id} закрыт*\n\nСпасибо за обращение!", parse_mode="Markdown")

# ========== КАЛЬКУЛЯТОР ==========

@bot.message_handler(func=lambda m: m.text == "Калькулятор")
def calculator(message):
    bot.send_message(message.chat.id, "🧮 *Калькулятор Stars*\n\nВыбери направление 👇",
                     reply_markup=calculator_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_"))
def calculator_handler(call):
    bot.answer_callback_query(call.id)
    action = call.data
    prompts = {
        "calc_stars_to_uah": (f"⭐️ *Stars → Грн*\nКурс: *{STARS_SELL_RATE} грн*\n\nВведите количество Stars:", process_calc_stars_to_uah),
        "calc_uah_to_stars": (f"💰 *Грн → Stars*\nКурс: *{STARS_BUY_RATE} грн*\n\nВведите сумму в гривнах:", process_calc_uah_to_stars),
    }
    if action in prompts:
        text, handler = prompts[action]
        msg = bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())
        bot.register_next_step_handler(msg, handler)

def process_calc_stars_to_uah(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = int(float(message.text.replace(",", ".")))
        bot.send_message(message.chat.id,
            f"⭐️ *Результат:*\n\n{amount} Stars = *{round(amount * STARS_SELL_RATE, 2)} грн*",
            parse_mode="Markdown", reply_markup=calculator_keyboard())
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите целое число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_calc_stars_to_uah)

def process_calc_uah_to_stars(message):
    if message.text in MENU_BUTTONS: handle_menu(message); return
    try:
        amount = float(message.text.replace(",", "."))
        bot.send_message(message.chat.id,
            f"💰 *Результат:*\n\n{amount} грн = *{int(amount / STARS_BUY_RATE)} Stars*",
            parse_mode="Markdown", reply_markup=calculator_keyboard())
    except:
        msg = bot.send_message(message.chat.id, "❌ Введите число!", reply_markup=main_menu())
        bot.register_next_step_handler(msg, process_calc_uah_to_stars)

bot.infinity_polling()
