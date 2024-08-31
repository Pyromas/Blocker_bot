import sqlite3
from config import DB_NAME


class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()

            cur.execute('''CREATE TABLE IF NOT EXISTS blocked_links (
                            id INTEGER PRIMARY KEY, 
                            links TEXT)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY, 
                            chat_id INTEGER, 
                            warning_count INTEGER DEFAULT 0)''')
            conn.commit()

    # Добавление ссылки в черный список
    def add_link(self, chat_id, link):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()

            cur.execute(f'SELECT links FROM blocked_links WHERE id = {chat_id}')
            links = eval(cur.fetchall()[0][0])

            links.append(link)
            links = str(links)

            cur.execute(f"""UPDATE blocked_links
                        SET links = {links}
                        WHERE id = {chat_id};""")
            conn.commit()

    # Удаление ссылки из черного списка
    def del_link(self, chat_id, link):#Ответы: 1 -> такой ссылки нет в чёрном списке, 2 -> ссылка удалена
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()

            cur.execute(f'SELECT links FROM blocked_links WHERE id = {chat_id}')
            links = eval(cur.fetchall()[0][0])

            try:
                links.remove(link)
            except ValueError:
                return 1
            else:
                links = str(links)

                cur.execute(f"""UPDATE blocked_links
                            SET links = {links}
                            WHERE id = {chat_id};""")
                conn.commit()
                return 2

    # Получение количества варнов пользователя
    def get_warning_count(self, user_id, chat_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT warning_count
                        FROM users 
                        WHERE user_id = {user_id} AND chat_id = {chat_id}""") 
            result = cur.fetchone()
            return result[0] if result else 0

    # Получение списка запрещённых ссылок в определённой группе 
    def get_blocked_links(self, chat_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT links
                        FROM blocked_links 
                        WHERE id = {chat_id}""")
            result = eval(cur.fetchall()[0][0])
            return result

    # Добавление варна пользователю
    def add_warning(self, user_id, chat_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            warning_count = self.get_warning_count(user_id, chat_id) + 1
            cur.execute(f"""UPDATE users
                            SET user_warnings = {warning_count}
                            WHERE id = {user_id} AND chat_id = {chat_id}""")
            conn.commit()
            return warning_count
        
    # Проверка сообщения на наличие заблокированных ссылок
    def check_message_for_links(self, chat_id, message_text):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(f"""SELECT links
                        FROM blocked_links
                        WHERE id = {chat_id}""")
            links = eval(cur.fetchall()[0][0])

            for link in links:
                if link in message_text:
                    return True
            return False

if __name__ == '__main__':
    db = DB_Manager(DB_NAME)
    db.create_table()
    db.add_link(1, "https://google.com")
