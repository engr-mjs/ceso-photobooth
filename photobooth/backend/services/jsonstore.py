from datetime import datetime
from typing import Dict, List, Optional

from . import blobstore

__all__ = [
    'init_db', 'create_session', 'get_session', 'update_session', 'save_photo',
    'get_session_photos', 'get_all_sessions', 'delete_session', 'session_exists',
]

UPDATABLE_KEYS = ('status', 'strip_generated', 'strip_filename', 'qr_filename', 'photo_count', 'metadata')


def _key(session_id: str) -> str:
    return f"db/sessions/{session_id}.json"


def init_db() -> None:
    pass


def create_session(session_id: str) -> Dict:
    now = datetime.now().isoformat()
    row = {
        'id': session_id,
        'created_at': now,
        'status': 'active',
        'strip_generated': 0,
        'strip_filename': None,
        'qr_filename': None,
        'photo_count': 0,
        'metadata': None,
        'photos': [],
    }
    blobstore.put_json(_key(session_id), row)
    return {'session_id': session_id, 'created_at': now, 'status': 'active'}


def get_session(session_id: str) -> Optional[Dict]:
    data = blobstore.get_json(_key(session_id))
    if isinstance(data, dict) and 'id' in data:
        return data
    return None


def update_session(session_id: str, **kwargs) -> None:
    row = get_session(session_id)
    if row is None:
        return
    changed = False
    for key, value in kwargs.items():
        if key in UPDATABLE_KEYS:
            row[key] = value
            changed = True
    if changed:
        blobstore.put_json(_key(session_id), row)


def save_photo(session_id: str, photo_index: int, filename: str, filepath: str) -> Dict:
    row = get_session(session_id)
    if row is None:
        raise KeyError(f"Session not found: {session_id}")
    photo = {
        'id': photo_index + 1,
        'session_id': session_id,
        'photo_index': photo_index,
        'filename': filename,
        'filepath': filepath,
        'created_at': datetime.now().isoformat(),
    }
    photos = [p for p in row.get('photos', []) if p['photo_index'] != photo_index]
    photos.append(photo)
    photos.sort(key=lambda p: p['photo_index'])
    row['photos'] = photos
    row['photo_count'] = len(photos)
    blobstore.put_json(_key(session_id), row)
    return {'id': photo['id'], 'session_id': session_id, 'photo_index': photo_index, 'filename': filename}


def get_session_photos(session_id: str) -> List[Dict]:
    row = get_session(session_id)
    if row is None:
        return []
    return list(row.get('photos', []))


def get_all_sessions() -> List[Dict]:
    sessions = []
    for entry in blobstore.list_entries('db/sessions/'):
        row = blobstore.get_json(entry['key'])
        if isinstance(row, dict) and 'id' in row:
            row.pop('photos', None)
            sessions.append(row)
    sessions.sort(key=lambda r: r.get('created_at', ''), reverse=True)
    return sessions


def delete_session(session_id: str) -> None:
    blobstore.delete_keys([_key(session_id)])


def session_exists(session_id: str) -> bool:
    return get_session(session_id) is not None
