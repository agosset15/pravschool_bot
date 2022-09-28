import sqlite3


class Database:
    def __init__(self, db_file1, db_file2):
        self.connection = sqlite3.connect(db_file1)
        self.conn = sqlite3.connect(db_file2)
        self.cur = self.conn.cursor()
        self.cursor = self.connection.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS `users`
        (id INTEGER, name VARCHAR, uname VARCHAR, class INTEGER, teacher INTEGER)
        """)
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS `admins`
        (id INTEGER, name VARCHAR, uname VARCHAR, paswd VARCHAR)
        """)
        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS `chat`
                (id INTEGER, class INTEGER)
                """)

        self.cursor.execute('CREATE TABLE IF NOT EXISTS `rasp` (id_day int, rasp text)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS `uchitel_kab` (id_day int, rasp text)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS `uchitel_rasp` (id_day int, rasp text)')

        self.conn.commit()
        self.connection.commit()

    def user_exists(self, user_id):
        with self.conn:
            result = self.cur.execute("SELECT * FROM `users` WHERE `id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, name, username, clas, tchr):
        with self.conn:
            return self.cur.execute("INSERT INTO users values (:id, :name, :uname, :class, :teacher);",
                                    {'id': user_id,
                                     'name': name,
                                     'uname': username,
                                     'class': clas,
                                     'teacher': tchr})

    def add_chat(self, chat_id: int, clas: int):
        with self.conn:
            return self.cur.execute("INSERT INTO chat values (:id, :class);",
                                    {'id': chat_id,
                                     'class': clas})

    def is_chat(self, chat_id: int):
        with self.conn:
            result = self.cur.execute("SELECT * FROM `chat` WHERE `id` = ?", (chat_id,)).fetchall()
            return bool(len(result))

    def chat(self, chat_id: int):
        with self.conn:
            result = self.cur.execute("SELECT * FROM `users` WHERE `id` = ?", (chat_id,)).fetchone()[0]
            return result

    def add_admin(self, user_id, name, uname, paswd):
        with self.conn:
            return self.cur.execute("INSERT INTO admins values (:id, :name, :uname, :paswd);",
                                    {'id': user_id,
                                     'name': name,
                                     'uname': uname,
                                     'paswd': paswd})

    def admin_exists(self, user_id):
        with self.conn:
            result = self.cur.execute("SELECT * FROM `admins` WHERE `id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def admin(self, user_id):
        with self.conn:
            result = self.cur.execute("SELECT paswd FROM `admins` WHERE `id` = ?", (user_id,)).fetchone()[0]
            return result

    def del_user(self, user_id):
        with self.conn:
            return self.cur.execute("DELETE from `users` where `id` = ?", (user_id,))

    def teacher(self, user_id):
        with self.conn:
            return self.cur.execute("SELECT teacher FROM `users` WHERE `id` = ?", (user_id,)).fetchone()[0]

    def teacher_rasp(self, id_day):
        with self.connection:
            return self.cursor.execute("SELECT rasp FROM `uchitel_rasp` WHERE `id_day` = ?", (id_day,)).fetchone()[0]

    def kab(self, id_day):
        with self.connection:
            return self.cursor.execute("SELECT rasp FROM `uchitel_kab` WHERE `id_day` = ?", (id_day,)).fetchone()[0]

    def what_class(self, user_id):
        with self.conn:
            return self.cur.execute("SELECT class FROM `users` WHERE `id` = ?", (user_id,)).fetchone()[0]

    def what_name(self, user_id):
        with self.conn:
            return self.cur.execute("SELECT name FROM `users` WHERE `id` = ?", (user_id,)).fetchone()[0]

    def day(self, clas):
        with self.connection:
            return self.cursor.execute("SELECT rasp FROM `rasp` WHERE id_day = ?", (clas,)).fetchone()[0]

    def count(self):
        with self.conn:
            return self.cur.execute('SELECT Count(*) FROM `users`').fetchone()[0]

    def delall(self):
        with self.connection:
            self.cursor.execute("DELETE FROM rasp")
            self.cursor.execute("DELETE FROM uchitel_kab")
            self.cursor.execute("DELETE FROM uchitel_rasp")
            self.connection.commit()

    def week(self, clas: int):
        with self.connection:
            data = []
            for i in range(1, 6):
                cls = float(int(clas) + i/10)
                data.append(self.cursor.execute("SELECT rasp FROM `rasp` WHERE id_day = ?", (cls,)).fetchone()[0])
            return data

    def teacher_week(self, id: int):
        with self.connection:
            data = []
            for i in range(1, 6):
                cls = float(int(id) + i/10)
                data.append(self.cursor.execute("SELECT rasp FROM `uchitel_rasp` WHERE `id_day` = ?", (cls,)).fetchone()[0])
            return data

    def ad(self):
        with self.conn:
            self.cur.execute("SELECT id FROM users")
            userbase = []
            while True:
                row = self.cur.fetchone()
                if row is None:
                    break
                userbase.append(row)
            return userbase
