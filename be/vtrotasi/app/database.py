import sqlite3

DATABASE = "keys.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            status TEXT DEFAULT 'active',
            reset_time DATETIME DEFAULT NULL,
            usage_count INTEGER DEFAULT 0,
            last_used DATETIME DEFAULT NULL
        )
    """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS task_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL UNIQUE,
            file_path TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()
