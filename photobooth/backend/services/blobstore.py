import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
IS_VERCEL = bool(os.environ.get('VERCEL'))


def _local_path(key: str) -> str:
    path = os.path.normpath(os.path.join(BASE_DIR, *key.split('/')))
    if not path.startswith(BASE_DIR + os.sep):
        raise ValueError(f"Invalid storage key: {key}")
    return path


def _blob():
    import vercel.blob as blob
    return blob


def put_bytes(key: str, data: bytes, content_type: str = 'application/octet-stream') -> None:
    if IS_VERCEL:
        _blob().put(key, data, access='public', content_type=content_type, overwrite=True)
        return
    path = _local_path(key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def get_bytes(key: str) -> Optional[bytes]:
    if IS_VERCEL:
        try:
            return _blob().get(key, access='public').content
        except Exception as e:
            if type(e).__name__ == 'BlobNotFoundError':
                return None
            raise
    path = _local_path(key)
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return f.read()


def exists(key: str) -> bool:
    return get_bytes(key) is not None


def delete_keys(keys: List[str]) -> None:
    if not keys:
        return
    if IS_VERCEL:
        try:
            _blob().delete(keys)
        except Exception:
            for key in keys:
                try:
                    _blob().delete(key)
                except Exception:
                    continue
        return
    for key in keys:
        try:
            os.remove(_local_path(key))
        except OSError:
            continue


def list_entries(prefix: str) -> List[Dict[str, Any]]:
    if IS_VERCEL:
        entries = []
        cursor = None
        while True:
            res = _blob().list_objects(prefix=prefix, limit=1000, cursor=cursor)
            for item in res['blobs']:
                entries.append({
                    'key': item['pathname'],
                    'size': item['size'],
                    'uploaded_at': item['uploaded_at'],
                })
            if not res.get('has_more') or not res.get('cursor'):
                break
            cursor = res['cursor']
        return entries

    base = _local_path(prefix)
    entries = []
    if os.path.isdir(base):
        for root, _dirs, files in os.walk(base):
            for name in files:
                full = os.path.join(root, name)
                rel = os.path.relpath(full, BASE_DIR).replace(os.sep, '/')
                entries.append({
                    'key': rel,
                    'size': os.path.getsize(full),
                    'uploaded_at': datetime.fromtimestamp(os.path.getmtime(full)),
                })
    return entries


def put_json(key: str, obj: Any, content_type: str = 'application/json') -> None:
    put_bytes(key, json.dumps(obj, indent=2).encode('utf-8'), content_type=content_type)


def get_json(key: str, default: Any = None) -> Any:
    data = get_bytes(key)
    if data is None:
        return default
    try:
        return json.loads(data.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return default
