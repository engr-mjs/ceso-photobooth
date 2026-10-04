import copy
import json
import os
import time
from typing import Any

from . import blobstore

BASE_DIR = blobstore.BASE_DIR
SETTINGS_PATH = os.path.join(BASE_DIR, 'config', 'settings.json')
TEMPLATES_PATH = os.path.join(BASE_DIR, 'config', 'templates.json')
SETTINGS_KEY = 'config/settings.json'
TEMPLATES_KEY = 'config/templates.json'
CACHE_TTL_SECONDS = 60

_cache = {}


def _read_bundled(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def _invalidate(name: str = None) -> None:
    if name is None:
        _cache.clear()
    else:
        _cache.pop(name, None)


def _load(name: str, path: str, override_key: str) -> dict:
    now = time.time()
    hit = _cache.get(name)
    if hit and now - hit[0] < CACHE_TTL_SECONDS:
        return copy.deepcopy(hit[1])
    data = _read_bundled(path)
    override = blobstore.get_json(override_key)
    if isinstance(override, dict):
        data.update(override)
    _cache[name] = (now, data)
    return copy.deepcopy(data)


def get_settings() -> dict:
    if not blobstore.IS_VERCEL:
        return _read_bundled(SETTINGS_PATH)
    return _load('settings', SETTINGS_PATH, SETTINGS_KEY)


def get_templates_config() -> dict:
    if not blobstore.IS_VERCEL:
        return _read_bundled(TEMPLATES_PATH)
    return _load('templates', TEMPLATES_PATH, TEMPLATES_KEY)


def save_settings(settings: dict) -> None:
    if blobstore.IS_VERCEL:
        blobstore.put_json(SETTINGS_KEY, settings)
        _invalidate('settings')
        return
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent=2)


def save_templates_config(config: dict) -> None:
    if blobstore.IS_VERCEL:
        blobstore.put_json(TEMPLATES_KEY, config)
        _invalidate('templates')
        return
    with open(TEMPLATES_PATH, 'w') as f:
        json.dump(config, f, indent=2)
