import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict

__all__ = [
    'init_db', 'create_session', 'get_session', 'update_session', 'save_photo',
    'get_session_photos', 'get_all_sessions', 'delete_session', 'session_exists',
]

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'photobooth.db')


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            strip_generated INTEGER DEFAULT 0,
            strip_filename TEXT,
            qr_filename TEXT,
            photo_count INTEGER DEFAULT 0,
            metadata TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            photo_index INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    conn.commit()
    conn.close()


def create_session(session_id: str) -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        'INSERT INTO sessions (id, created_at, status) VALUES (?, ?, ?)',
        (session_id, now, 'active')
    )
    conn.commit()
    conn.close()
    return {"session_id": session_id, "created_at": now, "status": "active"}


def get_session(session_id: str) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_session(session_id: str, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    set_clauses = []
    values = []
    for key, value in kwargs.items():
        if key in ('status', 'strip_generated', 'strip_filename', 'qr_filename', 'photo_count', 'metadata'):
            set_clauses.append(f'{key} = ?')
            values.append(value)
    if set_clauses:
        values.append(session_id)
        query = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    conn.close()


def save_photo(session_id: str, photo_index: int, filename: str, filepath: str) -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        'INSERT INTO photos (session_id, photo_index, filename, filepath, created_at) VALUES (?, ?, ?, ?, ?)',
        (session_id, photo_index, filename, filepath, now)
    )
    cursor.execute(
        'UPDATE sessions SET photo_count = (SELECT COUNT(*) FROM photos WHERE session_id = ?) WHERE id = ?',
        (session_id, session_id)
    )
    conn.commit()
    photo_id = cursor.lastrowid
    conn.close()
    return {"id": photo_id, "session_id": session_id, "photo_index": photo_index, "filename": filename}


def get_session_photos(session_id: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM photos WHERE session_id = ? ORDER BY photo_index',
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_sessions() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_session(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM photos WHERE session_id = ?', (session_id,))
    cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()


def session_exists(session_id: str) -> bool:
    return get_session(session_id) is not None
