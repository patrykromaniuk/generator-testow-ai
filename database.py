import sqlite3
import datetime

DB_NAME = 'testy.db'

def init_db():
    """Tworzy tabele: historii i użytkowników"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            filename TEXT,
            generated_date TEXT,
            content TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, password_hash):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT username, password_hash FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def save_to_db(username, filename, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('INSERT INTO history (username, filename, generated_date, content) VALUES (?, ?, ?, ?)', 
              (username, filename, date_str, content))
    conn.commit()
    conn.close()

def get_history(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, filename, generated_date, content FROM history WHERE username = ? ORDER BY id DESC', (username,))
    data = c.fetchall()
    conn.close()
    return data