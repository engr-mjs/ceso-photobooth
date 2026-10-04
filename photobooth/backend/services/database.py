import os

if os.environ.get('VERCEL'):
    from .jsonstore import (  # noqa: F401
        create_session, delete_session, get_all_sessions, get_session,
        get_session_photos, init_db, save_photo, session_exists, update_session,
    )
else:
    from .sqlite_store import (  # noqa: F401
        create_session, delete_session, get_all_sessions, get_session,
        get_session_photos, init_db, save_photo, session_exists, update_session,
    )
