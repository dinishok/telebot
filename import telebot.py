import telebot
from telebot import types
import sqlite3
import os

TOKEN = '8038685111:AAELBHkkMfA5vzcz6zBq0TxNTT5fwlqu9H4'
bot = telebot.TeleBot(TOKEN)

DB_PATH = 'bot_database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        full_name TEXT
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        file_path TEXT
                      )''')
    conn.commit()
    conn.close()

init_db()


def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                   (user_id, username, full_name))
    conn.commit()
    conn.close()


def save_image(user_id, file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO images (user_id, file_path) VALUES (?, ?)', (user_id, file_path))
    conn.commit()
    conn.close()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    username = message.chat.username
    full_name = message.chat.first_name + ' ' + (message.chat.last_name or '')
    add_user(user_id, username, full_name)
    
    bot.send_message(
        user_id,
        f"👋 Привет, {message.chat.first_name}! Я ваш ассистент AITU.\n\n"
        "🎓 Чем могу помочь? Выберите из меню ниже или введите /help для списка команд.",
        reply_markup=main_menu_buttons()
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📋 **Список доступных команд:**\n"
        "/start — Начать работу.\n"
        "/help — Инструкция.\n"
        "/info — Описание бота.\n\n"
        "📌 Вы также можете:\n"
        "• Загружать изображения.\n"
        "• Искать информацию через меню.\n"
        "• Получать ссылки и консультации.",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=['info'])
def info_command(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ **О боте:**\n"
        "Я создан для помощи студентам AITU. Могу предоставить информацию о поступлении, "
        "карте кампуса, а также сохранить ваши фотографии. 🚀",
        parse_mode="Markdown"
    )


def main_menu_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_admission = types.KeyboardButton("📚 Поступление")
    btn_map = types.KeyboardButton("🌎 Карта AITU")
    btn_consultant = types.KeyboardButton("📞 Консультант")
    btn_gallery = types.KeyboardButton("🖼️ Моя галерея")
    markup.add(btn_admission, btn_map)
    markup.add(btn_consultant, btn_gallery)
    return markup


@bot.message_handler(func=lambda message: message.text in ["📚 Поступление", "🌎 Карта AITU", "📞 Консультант", "🖼️ Моя галерея"])
def handle_main_menu(message):
    if message.text == "📚 Поступление":
        bot.send_message(
            message.chat.id,
            "Выберите интересующий вас вопрос:",
            reply_markup=admission_buttons()
        )
    elif message.text == "🌎 Карта AITU":
        bot.send_message(
            message.chat.id,
            "🌍 [Карта кампуса AITU](https://yuujiso.github.io/aitumap/)",
            parse_mode="Markdown"
        )
    elif message.text == "📞 Консультант":
        bot.send_message(
            message.chat.id,
            "💬 Свяжитесь с консультантом: [Перейти в Telegram](https://t.me/dinishok)",
            parse_mode="Markdown"
        )
    elif message.text == "🖼️ Моя галерея":
        show_gallery(message.chat.id)


# def admission_buttons():
#     markup = types.InlineKeyboardMarkup()
#     questions = [
#         ("Какие критерии для поступления?", "Критерии поступления: Минимальный балл - 70.")
#     ]
#     for question, answer in questions:
#         markup.add(types.InlineKeyboardButton(question, callback_data=answer))
#     return markup

@bot.message_handler(func=lambda message: message.text == "📚 Поступление")
def handle_admission(message):
    bot.send_message(
        message.chat.id,
        "Выберите интересующий вас вопрос:",
        reply_markup=admission_buttons()
    )


def admission_buttons():
    markup = types.InlineKeyboardMarkup()
    questions = [
        ("Какие критерии для поступления?", "criteria"),
        ("Сколько стоит обучение?", "cost"),
        ("Сколько длится обучение?", "duration")
    ]
    for question, callback_data in questions:
        markup.add(types.InlineKeyboardButton(question, callback_data=callback_data))
    return markup


@bot.callback_query_handler(func=lambda call: call.data in ["criteria", "cost", "duration"])
def admission_callback(call):
    responses = {
        "criteria": "📌 **Критерии для поступления:**\nМинимальный балл - 70.\nДокументы:\n- Удостоверение личности\n- Аттестат/Диплом",
        "cost": "💰 **Стоимость обучения:**\n570 000 тенге за один учебный год.",
        "duration": "⏳ **Длительность обучения:**\n2 года и 10 месяцев (очная форма)."
    }

    # markup = admission_buttons()
    # # Убираем кнопку с выбранным вопросом
    # for button in markup.keyboard:
    #     if button[0].callback_data == call.data:
    #         markup.keyboard.remove(button)

    # # Редактируем сообщение
    # response = responses.get(call.data, "Информация недоступна.")
    # bot.edit_message_text(
    #     chat_id=call.message.chat.id,
    #     message_id=call.message.message_id,
    #     text=response,
    #     reply_markup=markup,
    #     parse_mode="Markdown"
    # )
    response = responses.get(call.data, "Информация недоступна.")
    bot.send_message(call.message.chat.id, response, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.send_message(call.message.chat.id, call.data)


@bot.message_handler(content_types=['photo'])
def handle_images(message):
    user_id = message.chat.id
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    
    downloaded_file = bot.download_file(file_path)
    save_path = f'images/{file_id}.jpg'
    os.makedirs('images', exist_ok=True)
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    save_image(user_id, save_path)
    bot.send_message(user_id, "📷 Фотография успешно сохранена!")


def show_gallery(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM images WHERE user_id = ?", (user_id,))
    images = cursor.fetchall()
    conn.close()

    if not images:
        bot.send_message(user_id, "🖼️ У вас пока нет сохранённых изображений.")
        return

    for image in images:
        with open(image[0], 'rb') as img_file:
            bot.send_photo(user_id, img_file)


bot.polling(none_stop=True)
