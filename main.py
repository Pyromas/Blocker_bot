import telebot
import sqlite3
from config import TOKEN  
from logic import DB_Manager
from config import DB_NAME
db = DB_Manager(DB_NAME)

API_TOKEN = TOKEN
bot = telebot.TeleBot(API_TOKEN)

# Подключение к базе данных
def get_db_connection():
    conn = DB_Manager
    return conn

# Функция для добавления запрещённой ссылки
@bot.message_handler(commands=['addlink'])
def add_link(message):
    if not message.from_user.username == 'admin_username':  # Указать имя администратора
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    link = message.text.split()[1]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO banned_links (link) VALUES (?)", (link,))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"Ссылка {link} успешно добавлена в список запрещённых.")

# Функция для удаления запрещённой ссылки
@bot.message_handler(commands=['dellink'])
def del_link(message):
    if not message.from_user.username == 'admin_username':  # Указать имя администратора
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    link = message.text.split()[1]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM banned_links WHERE link=?", (link,))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"Ссылка {link} успешно удалена из списка запрещённых.")

# Функция для проверки наличия ссылки в списке запрещённых
def is_link_banned(link):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM banned_links WHERE link=?", (link,))
    banned_link = cursor.fetchone()
    conn.close()
    return banned_link is not None

# Функция для добавления варна пользователю
def add_warning(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT warnings FROM user_warnings WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        warnings = result[0] + 1
        cursor.execute("UPDATE user_warnings SET warnings=? WHERE user_id=?", (warnings, user_id))
    else:
        warnings = 1
        cursor.execute("INSERT INTO user_warnings (user_id, warnings) VALUES (?, ?)", (user_id, warnings))

    conn.commit()
    conn.close()
    return warnings

# Хендлер для проверки всех сообщений
@bot.message_handler(func=lambda message: True)
def check_message(message):
    if message.entities:
        for entity in message.entities:
            if entity.type == 'url':
                url = message.text[entity.offset:entity.offset + entity.length]
                if is_link_banned(url):
                    warnings = add_warning(message.from_user.id)
                    bot.delete_message(message.chat.id, message.message_id)
                    if warnings < 3:
                        bot.reply_to(message, f"Запрещённая ссылка. У вас {warnings}/3 варнов. При достижении 3-х вы получите бан.")
                    else:
                        bot.kick_chat_member(message.chat.id, message.from_user.id)
                        bot.send_message(message.chat.id, f"{message.from_user.first_name} забанен за превышение количества варнов.")
                    break

bot.infinity_polling()
