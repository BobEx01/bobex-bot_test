import sqlite3

class Database:
    def __init__(self, db_path='bobex.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                is_premium INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0
            )
        ''')
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

    def add_user(self, user_id):
        self.cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        self.conn.commit()

    def set_premium(self, user_id, value=1):
        self.cursor.execute('UPDATE users SET is_premium = ? WHERE user_id = ?', (value, user_id))
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()

    def add_balance(self, user_id, amount):
        self.cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        self.conn.commit()

    def add_ad(self, user_id, cargo_desc, vazn, tolov, is_premium=0):
        self.cursor.execute('''
            INSERT INTO ads (user_id, cargo_desc, vazn, tolov, is_premium)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, cargo_desc, vazn, tolov, is_premium))
        self.conn.commit()

    def get_ads(self, is_premium=None):
        if is_premium is None:
            self.cursor.execute('SELECT * FROM ads')
        else:
            self.cursor.execute('SELECT * FROM ads WHERE is_premium = ?', (is_premium,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
