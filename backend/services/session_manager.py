import os
import uuid
import json
import secrets
import string
from datetime import datetime
from typing import Optional, List, Dict, Any


class SessionManager:
    def __init__(self, sessions_dir: str, id_length: int = 16):
        self.sessions_dir = sessions_dir
        self.id_length = id_length
        os.makedirs(sessions_dir, exist_ok=True)

    def generate_session_id(self) -> str:
        alphabet = string.ascii_lowercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(self.id_length))

    def get_session_dir(self, session_id: str) -> str:
        safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
        return os.path.join(self.sessions_dir, safe_id)

    def create_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        if session_id is None:
            session_id = self.generate_session_id()

        session_dir = self.get_session_dir(session_id)
        os.makedirs(session_dir, exist_ok=True)

        metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "photos": [],
            "strip_generated": False,
            "qr_generated": False,
        }

        metadata_path = os.path.join(session_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return {
            "session_id": session_id,
            "session_dir": session_dir,
            "metadata": metadata,
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session_dir = self.get_session_dir(session_id)
        metadata_path = os.path.join(session_dir, "metadata.json")

        if not os.path.exists(metadata_path):
            return None

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        return {
            "session_id": session_id,
            "session_dir": session_dir,
            "metadata": metadata,
        }

    def update_session_metadata(
        self, session_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None

        metadata = session["metadata"]
        metadata.update(updates)
        metadata["updated_at"] = datetime.now().isoformat()

        metadata_path = os.path.join(session["session_dir"], "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return {
            "session_id": session_id,
            "session_dir": session["session_dir"],
            "metadata": metadata,
        }

    def get_photo_path(self, session_id: str, photo_number: int) -> str:
        session_dir = self.get_session_dir(session_id)
        return os.path.join(session_dir, f"photo{photo_number}.png")

    def get_strip_path(self, session_id: str) -> str:
        session_dir = self.get_session_dir(session_id)
        return os.path.join(session_dir, "strip.png")

    def get_qr_path(self, session_id: str) -> str:
        session_dir = self.get_session_dir(session_id)
        return os.path.join(session_dir, "qr.png")

    def get_metadata_path(self, session_id: str) -> str:
        session_dir = self.get_session_dir(session_id)
        return os.path.join(session_dir, "metadata.json")

    def get_all_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        sessions = []
        if not os.path.exists(self.sessions_dir):
            return sessions

        entries = sorted(
            os.listdir(self.sessions_dir),
            key=lambda x: os.path.getmtime(os.path.join(self.sessions_dir, x)),
            reverse=True,
        )

        for entry in entries[:limit]:
            session_path = os.path.join(self.sessions_dir, entry)
            if os.path.isdir(session_path):
                session = self.get_session(entry)
                if session:
                    sessions.append(session)

        return sessions

    def delete_session(self, session_id: str) -> bool:
        session_dir = self.get_session_dir(session_id)
        if os.path.exists(session_dir):
            import shutil
            shutil.rmtree(session_dir)
            return True
        return False

    def list_sessions(self) -> List[str]:
        if not os.path.exists(self.sessions_dir):
            return []
        return [
            d
            for d in os.listdir(self.sessions_dir)
            if os.path.isdir(os.path.join(self.sessions_dir, d))
        ]
