import sqlite3
from constants import SUBJECTS

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()


def create_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        password TEXT,
        logged_in BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT
        )
        ''')
    conn.commit()

    # Проверка на заполненность таблицы subjects
    cursor.execute('SELECT COUNT(*) FROM subjects')
    count = cursor.fetchone()[0]

    if not count:
        for subject in SUBJECTS:
            cursor.execute('INSERT INTO subjects (subject_name) VALUES (?)', (subject,))
        conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subjects (
            us_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            user_id INTEGER,
            score INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    conn.commit()


