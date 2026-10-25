import sqlite3
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "arbitrage_hub.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_type TEXT NOT NULL,
        ticker TEXT NOT NULL,
        display_name TEXT NOT NULL,
        quantity REAL NOT NULL,
        avg_cost REAL NOT NULL,
        cost_currency TEXT NOT NULL DEFAULT 'USD',
        purchase_date TEXT,
        broker TEXT,
        notes TEXT,
        manual_price REAL,
        manual_price_source TEXT,
        manual_price_updated TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_type TEXT NOT NULL,
        ticker TEXT NOT NULL,
        display_name TEXT NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(asset_type, ticker)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS opportunity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_pair TEXT NOT NULL,
        buy_source TEXT NOT NULL,
        sell_source TEXT NOT NULL,
        buy_price REAL NOT NULL,
        sell_price REAL NOT NULL,
        gross_spread_pct REAL NOT NULL,
        net_spread_pct REAL NOT NULL,
        est_net_profit REAL NOT NULL,
        capital_amount REAL NOT NULL,
        fee_assumptions TEXT,
        status TEXT NOT NULL,
        rejection_reason TEXT,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_type TEXT NOT NULL,
        symbol TEXT NOT NULL,
        display_name_ar TEXT NOT NULL,
        display_name_en TEXT NOT NULL,
        old_price REAL NOT NULL,
        new_price REAL NOT NULL,
        change_pct REAL NOT NULL,
        currency TEXT NOT NULL,
        formatted_time TEXT NOT NULL,
        date_day TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_snapshots (
        symbol TEXT PRIMARY KEY,
        price REAL NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def execute_query(sql: str, params: tuple = ()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def fetch_all(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
