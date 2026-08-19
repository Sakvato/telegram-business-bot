import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def init_sync(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product TEXT,
                description TEXT,
                quantity INTEGER DEFAULT 1,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

    def add_user_sync(self, user_id, username=None, full_name=None):
        self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        self.conn.commit()

    def get_user_sync(self, user_id):
        cur = self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()

    def add_order_sync(self, user_id, product, description, quantity=1):
        cur = self.conn.execute(
            "INSERT INTO orders (user_id, product, description, quantity) VALUES (?, ?, ?, ?)",
            (user_id, product, description, quantity)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_order_sync(self, order_id):
        cur = self.conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        return cur.fetchone()

    def get_user_orders_sync(self, user_id):
        cur = self.conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        )
        return cur.fetchall()

    def get_all_orders_sync(self, status=None):
        if status:
            cur = self.conn.execute(
                "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC", (status,)
            )
        else:
            cur = self.conn.execute("SELECT * FROM orders ORDER BY created_at DESC")
        return cur.fetchall()

    def update_order_status_sync(self, order_id, status):
        self.conn.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id)
        )
        self.conn.commit()

    def get_stats_sync(self):
        stats = {}
        stats["total_users"] = self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        stats["total_orders"] = self.conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        stats["pending_orders"] = self.conn.execute(
            "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
        ).fetchone()[0]
        stats["completed_orders"] = self.conn.execute(
            "SELECT COUNT(*) FROM orders WHERE status = 'completed'"
        ).fetchone()[0]
        return stats
