import aiosqlite
import os
import json
from datetime import datetime
from typing import Optional

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "photobooth.db")


async def get_database() -> aiosqlite.Connection:
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_database():
    db = await get_database()
    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                photo1_path TEXT,
                photo2_path TEXT,
                photo3_path TEXT,
                strip_path TEXT,
                qr_path TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id ON sessions(session_id)
        """)
        await db.commit()
    finally:
        await db.close()


async def create_session(session_id: str, metadata: dict = None) -> dict:
    db = await get_database()
    try:
        metadata_json = json.dumps(metadata) if metadata else None
        await db.execute(
            "INSERT INTO sessions (session_id, metadata) VALUES (?, ?)",
            (session_id, metadata_json)
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def update_session(session_id: str, **kwargs) -> dict:
    db = await get_database()
    try:
        set_clauses = []
        values = []
        for key, value in kwargs.items():
            if key in ("photo1_path", "photo2_path", "photo3_path", "strip_path", "qr_path", "metadata"):
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return None

        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(session_id)

        query = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE session_id = ?"
        await db.execute(query, values)
        await db.commit()

        cursor = await db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def get_session(session_id: str) -> Optional[dict]:
    db = await get_database()
    try:
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def get_all_sessions(limit: int = 100, offset: int = 0) -> list:
    db = await get_database()
    try:
        cursor = await db.execute(
            "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def delete_session(session_id: str) -> bool:
    db = await get_database()
    try:
        cursor = await db.execute(
            "DELETE FROM sessions WHERE session_id = ?", (session_id,)
        )
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()
