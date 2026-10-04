import os
import uuid
import json
import base64
from datetime import datetime
from typing import Optional

from . import blobstore
from . import config_store
from . import database as db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SESSIONS_DIR = os.path.join(BASE_DIR, 'sessions')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
STRIPS_DIR = os.path.join(PHOTOS_DIR, 'strips')
ORIGINALS_DIR = os.path.join(PHOTOS_DIR, 'originals')
QRCODES_DIR = os.path.join(BASE_DIR, 'qrcodes')


def get_settings() -> dict:
    return config_store.get_settings()


def generate_session_id() -> str:
    return str(uuid.uuid4())[:12]


def create_session_dirs(session_id: str) -> str:
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    if not blobstore.IS_VERCEL:
        os.makedirs(session_dir, exist_ok=True)
    return session_dir


def get_session_dir(session_id: str) -> Optional[str]:
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    if os.path.exists(session_dir):
        return session_dir
    return None


def save_photo_bytes(session_id: str, photo_index: int, image_bytes: bytes) -> dict:
    filename = f"photo_{photo_index + 1}.png"
    key = f"sessions/{session_id}/{filename}"
    blobstore.put_bytes(key, image_bytes, content_type='image/png')

    if not blobstore.IS_VERCEL:
        blobstore.put_bytes(
            f"photos/originals/{session_id}/{filename}", image_bytes,
            content_type='image/png',
        )

    db.save_photo(session_id, photo_index, filename, key)

    return {
        "success": True,
        "photo_index": photo_index,
        "filename": filename,
        "filepath": key,
        "message": f"Photo {photo_index + 1} saved successfully"
    }


def save_captured_photo(session_id: str, photo_index: int, image_data_b64: str) -> dict:
    header, data = image_data_b64.split(',', 1) if ',' in image_data_b64 else ('', image_data_b64)
    image_bytes = base64.b64decode(data)
    return save_photo_bytes(session_id, photo_index, image_bytes)


def get_session_metadata(session_id: str) -> dict:
    session = db.get_session(session_id)
    if not session:
        return None

    metadata = {}
    raw_metadata = session.get('metadata')
    if raw_metadata:
        try:
            metadata = json.loads(raw_metadata)
        except (ValueError, TypeError):
            metadata = {}

    return {
        "session_id": session_id,
        "created_at": session['created_at'],
        "status": session['status'],
        "strip_generated": bool(session['strip_generated']),
        "photo_count": session['photo_count'],
        "metadata": metadata
    }


def cleanup_old_sessions():
    if blobstore.IS_VERCEL:
        _cleanup_expired_blob_sessions()
        return

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


def _cleanup_expired_blob_sessions():
    settings = get_settings()
    max_age_hours = settings.get('max_session_age_hours', 24)
    max_photos = settings.get('allowed_photo_count', 3)
    now = datetime.now()

    for entry in blobstore.list_entries('db/sessions/'):
        uploaded = entry['uploaded_at']
        if uploaded.tzinfo is not None:
            uploaded = uploaded.replace(tzinfo=None)
        age_hours = (now - uploaded).total_seconds() / 3600
        if age_hours <= max_age_hours:
            continue

        session_id = os.path.basename(entry['key'])[:-len('.json')]
        keys = [
            entry['key'],
            f"sessions/{session_id}/strip.png",
        ]
        keys.extend(
            f"sessions/{session_id}/photo_{i + 1}.png"
            for i in range(max_photos)
        )
        try:
            blobstore.delete_keys(keys)
        except Exception:
            continue
