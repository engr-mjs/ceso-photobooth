import os
import uuid
import json
import base64
from datetime import datetime
from typing import Optional

from . import database as db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SESSIONS_DIR = os.path.join(BASE_DIR, 'sessions')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
STRIPS_DIR = os.path.join(PHOTOS_DIR, 'strips')
ORIGINALS_DIR = os.path.join(PHOTOS_DIR, 'originals')
QRCODES_DIR = os.path.join(BASE_DIR, 'qrcodes')
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'settings.json')


def get_settings() -> dict:
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def generate_session_id() -> str:
    return str(uuid.uuid4())[:12]


def create_session_dirs(session_id: str) -> str:
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def get_session_dir(session_id: str) -> Optional[str]:
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    if os.path.exists(session_dir):
        return session_dir
    return None


def save_captured_photo(session_id: str, photo_index: int, image_data_b64: str) -> dict:
    session_dir = create_session_dirs(session_id)

    header, data = image_data_b64.split(',', 1) if ',' in image_data_b64 else ('', image_data_b64)
    image_bytes = base64.b64decode(data)

    filename = f"photo_{photo_index + 1}.png"
    filepath = os.path.join(session_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_bytes)

    original_path = os.path.join(ORIGINALS_DIR, session_id)
    os.makedirs(original_path, exist_ok=True)
    original_filepath = os.path.join(original_path, filename)
    with open(original_filepath, 'wb') as f:
        f.write(image_bytes)

    db.save_photo(session_id, photo_index, filename, filepath)

    photo_count = len(db.get_session_photos(session_id))
    db.update_session(session_id, photo_count=photo_count)

    return {
        "success": True,
        "photo_index": photo_index,
        "filename": filename,
        "filepath": filepath,
        "message": f"Photo {photo_index + 1} saved successfully"
    }


def get_session_metadata(session_id: str) -> dict:
    session = db.get_session(session_id)
    if not session:
        return None

    session_dir = get_session_dir(session_id)
    metadata_path = os.path.join(session_dir, 'metadata.json') if session_dir else None

    metadata = {}
    if metadata_path and os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

    return {
        "session_id": session_id,
        "created_at": session['created_at'],
        "status": session['status'],
        "strip_generated": bool(session['strip_generated']),
        "photo_count": session['photo_count'],
        "metadata": metadata
    }


def cleanup_old_sessions():
    settings = get_settings()
    max_age_hours = settings.get('max_session_age_hours', 24)
    sessions = db.get_all_sessions()
    now = datetime.now()

    for session in sessions:
        try:
            created = datetime.fromisoformat(session['created_at'])
            age_hours = (now - created).total_seconds() / 3600
            if age_hours > max_age_hours:
                session_dir = get_session_dir(session['id'])
                if session_dir:
                    import shutil
                    shutil.rmtree(session_dir, ignore_errors=True)
                db.delete_session(session['id'])
        except Exception:
            continue
