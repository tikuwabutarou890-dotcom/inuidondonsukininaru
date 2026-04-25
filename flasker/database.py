import sqlite3

def get_db():
    conn = sqlite3.connect("/data/schedules.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            thumbnail TEXT
        )
    """)
    conn.commit()
    conn.close()

