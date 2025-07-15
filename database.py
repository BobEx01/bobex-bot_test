import sqlite3

class Dadabase:
    def __init__(self, db_name='bobex.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Foydalanuvchilar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                is_premium INTEGER DEFAULT 0
            )
        ''')

        # E'lonlar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                cargo_desc TEXT,
                vazn REAL,
                tolov INTEGER,
                is_premium INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    # Foydalanuvchini qo'shish
    def add_user(self, user_id):
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (user_id) VALUES (?)
        ''', (user_id,))
        self.conn.commit()

    # Foydalanuvchini premium qilish
    def set_premium(self, user_id):
        self.cursor.execute('''
            UPDATE users SET is_premium = 1 WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()

    # Premium foydalanuvchimi tekshirish
    def is_premium(self, user_id):
        self.cursor.execute('''
            SELECT is_premium FROM users WHERE user_id = ?
        ''', (user_id,))
        result = self.cursor.fetchone()
        return result[0] == 1 if result else False

    # E'lon qo'shish
    def add_ad(self, user_id, cargo_desc, vazn, tolov, is_premium=0):
        self.cursor.execute('''
            INSERT INTO ads (user_id, cargo_desc, vazn, tolov, is_premium) 
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, cargo_desc, vazn, tolov, is_premium))
        self.conn.commit()

    # Barcha e'lonlarni olish
    def get_all_ads(self):
        self.cursor.execute('''
            SELECT * FROM ads
        ''')
        return self.cursor.fetchall()

    # Foydalanuvchining e'lonlarini olish
    def get_user_ads(self, user_id):
        self.cursor.execute('''
            SELECT * FROM ads WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchall()
