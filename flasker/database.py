import sqlite3

DATABASE = "/data/schedules.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # スケジュール
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

    # アクセスカウンター
    conn.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INTEGER PRIMARY KEY,
            count INTEGER NOT NULL
        )
    """)
    conn.execute("INSERT OR IGNORE INTO counter (id, count) VALUES (1, 0)")

    # ここ好き
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kokosuki (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            comment TEXT,
            minute INTEGER,
            second INTEGER,
            thumbnail TEXT
        )
    """)

    # コラボ
    conn.execute("""
        CREATE TABLE IF NOT EXISTS collab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            author TEXT,
            thumbnail TEXT
        )
    """)

    conn.commit()
    conn.close()

# アクセスカウンター
def get_count():
    conn = get_db()
    row = conn.execute("SELECT count FROM counter WHERE id = 1").fetchone()
    conn.close()
    return row["count"]

def increment_count():
    conn = get_db()
    conn.execute("UPDATE counter SET count = count + 1 WHERE id = 1")
    conn.commit()
    conn.close()
