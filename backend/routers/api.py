import os
import sys
import json
import socket
from datetime import datetime
from typing import Optional, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import (
    SessionCreate,
    SessionResponse,
    CaptureRequest,
    GenerateStripRequest,
    HealthResponse,
)
from database import (
    init_database,
    create_session,
    update_session,
    get_session,
)
from services.image_processor import ImageProcessor
from services.qr_generator import QRGenerator
from services.session_manager import SessionManager

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
QR_DIR = os.path.join(BASE_DIR, "qrcodes")
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")

image_processor = ImageProcessor(CONFIG_DIR)
qr_generator = QRGenerator(QR_DIR)
session_manager = SessionManager(SESSIONS_DIR)


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def load_app_settings() -> dict:
    settings_path = os.path.join(CONFIG_DIR, "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            return json.load(f)
    return {}


@router.on_event("startup")
async def startup():
    await init_database()
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.makedirs(QR_DIR, exist_ok=True)
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    os.makedirs(os.path.join(PHOTOS_DIR, "originals"), exist_ok=True)
    os.makedirs(os.path.join(PHOTOS_DIR, "strips"), exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    settings = load_app_settings()
    return HealthResponse(
        status="healthy",
        version=settings.get("app", {}).get("version", "1.0.0"),
        timestamp=datetime.now().isoformat(),
    )


@router.get("/api/settings")
async def get_settings():
    settings = load_app_settings()
    return settings


@router.get("/api/config/template")
async def get_template_config():
    config_path = os.path.join(CONFIG_DIR, "template.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Template configuration not found")


@router.post("/api/session/create")
async def create_new_session(request: Optional[SessionCreate] = None):
    metadata = request.metadata if request else None
    session = session_manager.create_session()
    await create_session(session["session_id"], metadata)

    return {
        "session_id": session["session_id"],
        "status": "created",
        "message": "Session created successfully",
    }


@router.post("/api/session/{session_id}/save-photo")
async def save_photo(session_id: str, photo_data: dict, photo_number: Optional[int] = None):
    number = photo_data.get("photo_number", photo_number)
    if number not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Photo number must be 1, 2, or 3")

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    base64_image = photo_data.get("image")
    if not base64_image:
        raise HTTPException(status_code=400, detail="Image data is required")

    photo_path = session_manager.get_photo_path(session_id, number)
    image_processor.save_photo_from_base64(base64_image, photo_path)

    session_manager.update_session_metadata(
        session_id,
        {
            f"photo{number}_saved": True,
            f"photo{number}_path": photo_path,
        },
    )

    await update_session(
        session_id,
        **{f"photo{number}_path": photo_path},
    )

    return {
        "status": "success",
        "photo_number": number,
        "path": photo_path,
        "message": f"Photo {number} saved successfully",
    }


@router.post("/api/session/{session_id}/generate-strip")
async def generate_strip(session_id: str, request: Optional[GenerateStripRequest] = None):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    photo_paths = []
    for i in range(1, 4):
        path = session_manager.get_photo_path(session_id, i)
        if not os.path.exists(path):
            raise HTTPException(
                status_code=400, detail=f"Photo {i} not found. All 3 photos are required."
            )
        photo_paths.append(path)

    strip_path = session_manager.get_strip_path(session_id)
    template_name = request.template_name if request else "default"

    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.png")
    if not os.path.exists(template_path):
        template_path = None

    try:
        image_processor.reload_config()
        generated_path = image_processor.generate_strip(
            photo_paths, strip_path, template_path
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate strip: {str(e)}"
        )

    settings = load_app_settings()
    host = get_local_ip()
    port = settings.get("server", {}).get("port", 8000)
    download_url = qr_generator.create_download_url(host, port, session_id)

    qr_path = session_manager.get_qr_path(session_id)
    qr_settings = settings.get("qr", {})
    try:
        qr_generator.generate(
            data=download_url,
            output_path=qr_path,
            box_size=qr_settings.get("box_size", 10),
            border=qr_settings.get("border", 2),
            error_correction=qr_settings.get("error_correction_level", "M"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate QR code: {str(e)}"
        )

    session_manager.update_session_metadata(
        session_id,
        {"strip_generated": True, "qr_generated": True, "strip_path": generated_path, "qr_path": qr_path},
    )

    await update_session(
        session_id,
        strip_path=generated_path,
        qr_path=qr_path,
    )

    return {
        "status": "success",
        "session_id": session_id,
        "strip_path": generated_path,
        "qr_path": qr_path,
        "download_url": download_url,
        "preview_url": f"/api/preview/{session_id}",
        "qr_url": f"/api/qr/{session_id}",
        "message": "Strip and QR code generated successfully",
    }


@router.get("/api/download/{session_id}")
async def download_strip(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    strip_path = session_manager.get_strip_path(session_id)
    if not os.path.exists(strip_path):
        raise HTTPException(status_code=404, detail="Strip not found")

    return FileResponse(
        path=strip_path,
        filename=f"photobooth_{session_id}.png",
        media_type="image/png",
    )


@router.get("/api/preview/{session_id}")
async def preview_strip(session_id: str):
    strip_path = session_manager.get_strip_path(session_id)
    if not os.path.exists(strip_path):
        raise HTTPException(status_code=404, detail="Strip not found")

    return FileResponse(path=strip_path, media_type="image/png")


@router.get("/api/qr/{session_id}")
async def get_qr_code(session_id: str):
    qr_path = session_manager.get_qr_path(session_id)
    if not os.path.exists(qr_path):
        raise HTTPException(status_code=404, detail="QR code not found")

    return FileResponse(path=qr_path, media_type="image/png")


@router.get("/api/photo/{session_id}/{photo_number}")
async def get_photo(session_id: str, photo_number: int):
    if photo_number not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Photo number must be 1, 2, or 3")

    photo_path = session_manager.get_photo_path(session_id, photo_number)
    if not os.path.exists(photo_path):
        raise HTTPException(status_code=404, detail=f"Photo {photo_number} not found")

    return FileResponse(path=photo_path, media_type="image/png")


@router.get("/api/session/{session_id}/info")
async def get_session_info(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    metadata = session["metadata"]
    photos_exist = []
    for i in range(1, 4):
        path = session_manager.get_photo_path(session_id, i)
        photos_exist.append(os.path.exists(path))

    strip_exists = os.path.exists(session_manager.get_strip_path(session_id))
    qr_exists = os.path.exists(session_manager.get_qr_path(session_id))

    return {
        "session_id": session_id,
        "metadata": metadata,
        "photos_exist": photos_exist,
        "strip_exists": strip_exists,
        "qr_exists": qr_exists,
    }


@router.get("/api/sessions")
async def list_sessions(limit: int = 50):
    sessions = session_manager.get_all_sessions(limit=limit)
    return {"sessions": sessions, "count": len(sessions)}


@router.delete("/api/session/{session_id}")
async def delete_session_endpoint(session_id: str):
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}


@router.get("/api/templates")
async def list_templates():
    templates = []
    if os.path.exists(TEMPLATES_DIR):
        for f in os.listdir(TEMPLATES_DIR):
            if f.lower().endswith(".png"):
                templates.append({
                    "name": os.path.splitext(f)[0],
                    "file": f,
                    "path": os.path.join(TEMPLATES_DIR, f),
                })
    return {"templates": templates}
