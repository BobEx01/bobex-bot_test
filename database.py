import sqlite3

class Database:
    def __init__(self, db_name='bobex.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, username, first_name, last_name):
        try:
            self.cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def get_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()
