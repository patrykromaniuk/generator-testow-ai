import sqlite3
import datetime

def init_db():
    """Tworzy tabelę w bazie, jeśli nie istnieje"""
    conn = sqlite3.connect('testy.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            generated_date TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(filename, content):
    """Zapisuje nowy test do historii"""
    conn = sqlite3.connect('testy.db')
    c = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('INSERT INTO history (filename, generated_date, content) VALUES (?, ?, ?)', 
              (filename, date_str, content))
    conn.commit()
    conn.close()

def get_history():
    """Pobiera listę zapisanych testów"""
    conn = sqlite3.connect('testy.db')
    c = conn.cursor()
    c.execute('SELECT id, filename, generated_date, content FROM history ORDER BY id DESC')
    data = c.fetchall()
    conn.close()
    return data