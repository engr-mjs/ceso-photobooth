import os
import json
import socket
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from services import database as db
from services import session_manager
from services import template_engine
from services import qr_service

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SESSIONS_DIR = os.path.join(BASE_DIR, 'sessions')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
QRCODES_DIR = os.path.join(BASE_DIR, 'qrcodes')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    os.makedirs(os.path.join(PHOTOS_DIR, 'originals'), exist_ok=True)
    os.makedirs(os.path.join(PHOTOS_DIR, 'strips'), exist_ok=True)
    os.makedirs(QRCODES_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)
    db.init_db()
    template_engine.get_active_template()
    session_manager.cleanup_old_sessions()
    yield


app = FastAPI(
    title="Photobooth",
    description="Professional Offline Photobooth System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


FRONTEND_PUBLIC_DIR = os.path.join(BASE_DIR, 'frontend', 'public')
if os.path.isdir(FRONTEND_PUBLIC_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_PUBLIC_DIR), name="frontend_public")


def secure_path(base: str, *parts: str) -> str:
    target = os.path.normpath(os.path.join(base, *parts))
    base_resolved = os.path.normpath(base)
    if not target.startswith(base_resolved):
        raise HTTPException(status_code=400, detail="Invalid path")
    return target


@app.get("/health", response_model=None)
def health_check():
    settings = session_manager.get_settings()
    local_ip = get_local_ip()
    return {
        "status": "healthy",
        "server_time": datetime.now().isoformat(),
        "version": "1.0.0",
        "local_ip": local_ip,
        "port": settings.get('server_port', 8000),
    }


@app.get("/api/info")
def server_info():
    settings = session_manager.get_settings()
    local_ip = get_local_ip()
    return {
        "app_name": settings.get('app_name', 'Photobooth'),
        "server_address": f"http://{local_ip}:{settings.get('server_port', 8000)}",
        "local_ip": local_ip,
        "port": settings.get('server_port', 8000),
        "active_template": template_engine.get_active_template_id(),
    }


@app.post("/api/sessions")
def create_session():
    session_id = session_manager.generate_session_id()
    session = db.create_session(session_id)
    session_manager.create_session_dirs(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "created_at": session['created_at'],
        "message": "Session created successfully"
    }


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_manager.get_session_metadata(session_id)


@app.get("/api/sessions")
def list_sessions():
    sessions = db.get_all_sessions()
    return {"sessions": sessions, "count": len(sessions)}


@app.post("/api/sessions/{session_id}/photos/{photo_index}")
def upload_photo(session_id: str, photo_index: int, file: UploadFile = File(...)):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    settings = session_manager.get_settings()
    max_photos = settings.get('allowed_photo_count', 3)
    if photo_index < 0 or photo_index >= max_photos:
        raise HTTPException(
            status_code=400,
            detail=f"Photo index must be between 0 and {max_photos - 1}"
        )

    existing = [p for p in db.get_session_photos(session_id) if p['photo_index'] == photo_index]
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Photo {photo_index + 1} already exists for this session"
        )

    session_dir = session_manager.create_session_dirs(session_id)
    filename = f"photo_{photo_index + 1}.png"
    filepath = secure_path(session_dir, filename)

    contents = file.file.read()
    with open(filepath, 'wb') as f:
        f.write(contents)

    originals_dir = secure_path(PHOTOS_DIR, 'originals', session_id)
    os.makedirs(originals_dir, exist_ok=True)
    original_filepath = secure_path(originals_dir, filename)
    with open(original_filepath, 'wb') as f:
        f.write(contents)

    db.save_photo(session_id, photo_index, filename, filepath)
    photo_count = len(db.get_session_photos(session_id))
    db.update_session(session_id, photo_count=photo_count)

    return {
        "success": True,
        "photo_index": photo_index,
        "filename": filename,
        "message": f"Photo {photo_index + 1} uploaded successfully"
    }


@app.post("/api/sessions/{session_id}/photos/base64/{photo_index}")
def upload_photo_base64(session_id: str, photo_index: int, body: dict):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    settings = session_manager.get_settings()
    max_photos = settings.get('allowed_photo_count', 3)
    if photo_index < 0 or photo_index >= max_photos:
        raise HTTPException(
            status_code=400,
            detail=f"Photo index must be between 0 and {max_photos - 1}"
        )

    image_data = body.get('image_data', '')
    if not image_data:
        raise HTTPException(status_code=400, detail="No image data provided")

    result = session_manager.save_captured_photo(session_id, photo_index, image_data)
    return result


@app.get("/api/sessions/{session_id}/photos")
def get_session_photos(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    photos = db.get_session_photos(session_id)
    photos_with_urls = []
    for photo in photos:
        photos_with_urls.append({
            **photo,
            "url": f"/api/sessions/{session_id}/photos/{photo['photo_index']}/file"
        })
    return {"photos": photos_with_urls, "count": len(photos_with_urls)}


@app.get("/api/sessions/{session_id}/photos/{photo_index}/file")
def serve_photo(session_id: str, photo_index: int):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_dir = session_manager.get_session_dir(session_id)
    if not session_dir:
        raise HTTPException(status_code=404, detail="Session directory not found")

    filename = f"photo_{photo_index + 1}.png"
    filepath = secure_path(session_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Photo not found")

    return FileResponse(filepath, media_type="image/png")


@app.post("/api/sessions/{session_id}/generate-strip")
def generate_strip(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_dir = session_manager.get_session_dir(session_id)
    if not session_dir:
        raise HTTPException(status_code=404, detail="Session directory not found")

    photos = db.get_session_photos(session_id)
    if len(photos) < 3:
        raise HTTPException(
            status_code=400,
            detail=f"Need 3 photos but only {len(photos)} uploaded"
        )

    photo_paths = []
    for i in range(3):
        filepath = os.path.join(session_dir, f"photo_{i + 1}.png")
        if not os.path.exists(filepath):
            raise HTTPException(status_code=400, detail=f"Photo {i + 1} file missing")
        photo_paths.append(filepath)

    try:
        strip_path = template_engine.generate_strip(photo_paths, session_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strip generation failed: {str(e)}")

    try:
        download_url = qr_service.get_download_url(session_id)
        qr_path = qr_service.generate_qr_code(session_id, download_url)
        display_qr_path = qr_service.create_display_qr(session_id, qr_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {str(e)}")

    db.update_session(
        session_id,
        strip_generated=True,
        strip_filename='strip.png',
        qr_filename=f"{session_id}.png",
        status='completed'
    )

    metadata = {
        "generated_at": datetime.now().isoformat(),
        "template_used": template_engine.get_active_template_id(),
        "download_url": download_url,
    }
    metadata_path = os.path.join(session_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    db.update_session(session_id, metadata=json.dumps(metadata))

    return {
        "success": True,
        "session_id": session_id,
        "strip_filename": "strip.png",
        "qr_code_url": f"/api/sessions/{session_id}/qr",
        "download_url": download_url,
        "preview_url": f"/api/sessions/{session_id}/preview",
        "strip_url": f"/api/sessions/{session_id}/strip",
        "message": "Strip generated successfully"
    }


@app.get("/api/sessions/{session_id}/strip")
def serve_strip(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_dir = session_manager.get_session_dir(session_id)
    strip_path = os.path.join(session_dir, 'strip.png') if session_dir else None

    if not strip_path or not os.path.exists(strip_path):
        raise HTTPException(status_code=404, detail="Strip not generated yet")

    return FileResponse(strip_path, media_type="image/png")


@app.get("/api/sessions/{session_id}/preview")
def serve_preview(session_id: str):
    return serve_strip(session_id)


@app.get("/api/sessions/{session_id}/qr")
def serve_qr(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    qr_path = os.path.join(QRCODES_DIR, f"{session_id}_display.png")
    if not os.path.exists(qr_path):
        qr_path = os.path.join(QRCODES_DIR, f"{session_id}.png")

    if not os.path.exists(qr_path):
        raise HTTPException(status_code=404, detail="QR code not generated yet")

    return FileResponse(qr_path, media_type="image/png")


def _download_page_css() -> str:
    return """<style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { -webkit-text-size-adjust: 100%; }
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: #FFFFFF;
            color: #171717;
            min-height: 100vh;
            display: flex;
            padding: 28px 20px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        :focus-visible { outline: 2px solid #171717; outline-offset: 2px; }
        .page {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 40px;
            width: 100%;
            max-width: 440px;
            margin: 0 auto;
            text-align: center;
        }
        .brand { display: flex; flex-direction: column; align-items: center; gap: 8px; animation: fadeUp 0.4s ease-out both; }
        .badge {
            width: 32px; height: 32px; border-radius: 9999px;
            background: #171717; color: #FFFFFF;
            display: flex; align-items: center; justify-content: center;
        }
        .badge svg { width: 16px; height: 16px; }
        .wordmark {
            font-family: 'Geist Pixel', monospace;
            font-size: 20px;
            letter-spacing: 0.1em;
            color: #171717;
            text-transform: uppercase;
        }
        .tagline { font-size: 12px; color: #A3A3A3; }
        .strip { position: relative; display: flex; flex-direction: column; align-items: center; animation: fadeUp 0.4s ease-out 0.08s both; }
        .strip-frame {
            border: 1px solid #E5E5E5;
            border-radius: 12px;
            overflow: hidden;
            background: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .strip-frame img {
            display: block;
            width: auto;
            height: auto;
            max-width: min(74vw, 300px);
            max-height: 52vh;
        }
        .pill {
            position: absolute;
            bottom: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: #FFFFFF;
            border: 1px solid #E5E5E5;
            border-radius: 9999px;
            padding: 4px 12px;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 0.6rem;
            color: #A3A3A3;
            white-space: nowrap;
        }
        .actions {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            width: 100%;
            max-width: 320px;
            animation: fadeUp 0.4s ease-out 0.16s both;
        }
        h2 { font-size: 18px; font-weight: 600; letter-spacing: -0.01em; color: #171717; }
        .hint { font-size: 13px; color: #A3A3A3; margin-top: 4px; }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: -0.01em;
            text-decoration: none;
            cursor: pointer;
            border: none;
            transition: background 150ms ease, border-color 150ms ease, transform 150ms ease;
        }
        .btn:active { transform: scale(0.98); }
        .btn svg { width: 16px; height: 16px; flex-shrink: 0; }
        .btn-primary { background: #171717; color: #FFFFFF; }
        .btn-primary:hover { background: #262626; }
        .btn-secondary {
            background: transparent;
            color: #525252;
            font-weight: 500;
            border: 1px solid #E5E5E5;
        }
        .btn-secondary:hover { border-color: #D4D4D4; background: #FAFAFA; }
        .net { font-size: 0.6rem; letter-spacing: 0.15em; text-transform: uppercase; color: #D4D4D4; margin-top: 6px; }
        .footer { display: flex; flex-direction: column; align-items: center; gap: 6px; animation: fadeUp 0.4s ease-out 0.24s both; }
        .powered { font-size: 0.6rem; letter-spacing: 0.15em; text-transform: uppercase; color: #D4D4D4; }
        .footer .logo { height: 20px; width: auto; object-fit: contain; opacity: 0.5; }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (prefers-reduced-motion: reduce) {
            * { animation: none !important; transition: none !important; }
        }
    </style>"""


@app.get("/download/{session_id}")
def download_page(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return HTMLResponse(
            content=_error_page("Session Not Found", "This session does not exist or has expired."),
            status_code=404
        )

    session_dir = session_manager.get_session_dir(session_id)
    strip_path = os.path.join(session_dir, 'strip.png') if session_dir else None

    if not strip_path or not os.path.exists(strip_path):
        return HTMLResponse(
            content=_error_page("Strip Not Ready", "The photobooth strip has not been generated yet."),
            status_code=404
        )

    settings = session_manager.get_settings()
    app_name = settings.get('app_name', 'Photobooth')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{app_name} - Your Photo</title>
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist+Pixel&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    {_download_page_css()}
</head>
<body>
    <div class="page">
        <header class="brand">
            <div class="badge">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
                </svg>
            </div>
            <div class="wordmark">PHOTOBOOTH</div>
            <p class="tagline">Your strip is ready</p>
        </header>

        <div class="strip">
            <div class="strip-frame">
                <img src="/api/sessions/{session_id}/strip" alt="Photobooth strip">
            </div>
            <div class="pill">{session_id[:8]}</div>
        </div>

        <section class="actions">
            <div>
                <h2>Download your strip</h2>
                <p class="hint">Save it to your phone or share it anywhere</p>
            </div>
            <a href="/api/sessions/{session_id}/strip/download" class="btn btn-primary">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/>
                </svg>
                Download Photo
            </a>
            <a href="/api/sessions/{session_id}/strip" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                View Full Size
            </a>
            <span class="net">Local network &middot; No internet required</span>
        </section>

        <footer class="footer">
            <span class="powered">Powered by</span>
            <img src="/static/assets/ceso.png" alt="CESO" class="logo">
        </footer>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/api/sessions/{session_id}/strip/download")
def download_strip_file(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_dir = session_manager.get_session_dir(session_id)
    strip_path = os.path.join(session_dir, 'strip.png') if session_dir else None

    if not strip_path or not os.path.exists(strip_path):
        raise HTTPException(status_code=404, detail="Strip not found")

    return FileResponse(
        strip_path,
        media_type="image/png",
        filename=f"photobooth_{session_id}.png",
        headers={"Content-Disposition": f'attachment; filename="photobooth_{session_id}.png"'}
    )


def _error_page(title: str, message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title} - Photobooth</title>
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist+Pixel&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    {_download_page_css()}
</head>
<body>
    <div class="page">
        <header class="brand">
            <div class="badge">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
            </div>
            <div class="wordmark">PHOTOBOOTH</div>
            <p class="tagline">Something went wrong</p>
        </header>

        <section class="actions">
            <div>
                <h2>{title}</h2>
                <p class="hint">{message}</p>
            </div>
            <button type="button" class="btn btn-secondary" onclick="history.back()">Go Back</button>
            <span class="net">Local network &middot; No internet required</span>
        </section>

        <footer class="footer">
            <span class="powered">Powered by</span>
            <img src="/static/assets/ceso.png" alt="CESO" class="logo">
        </footer>
    </div>
</body>
</html>"""


@app.get("/api/templates")
def list_templates():
    templates = template_engine.get_all_templates()
    active_id = template_engine.get_active_template_id()
    result = []
    for tid, tdata in templates.items():
        result.append({
            "id": tid,
            "name": tdata['name'],
            "description": tdata['description'],
            "filename": tdata['filename'],
            "output_width": tdata['output_width'],
            "output_height": tdata['output_height'],
            "photo_slots_count": len(tdata['photo_slots']),
            "active": tid == active_id
        })
    return {"templates": result, "active_template": active_id}


@app.get("/api/templates/{template_id}")
def get_template(template_id: str):
    templates = template_engine.get_all_templates()
    if template_id not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    tdata = templates[template_id]
    return {"id": template_id, **tdata}


@app.post("/api/templates/active")
def set_active_template(body: dict):
    template_id = body.get('template_id', '')
    templates = template_engine.get_all_templates()
    if template_id not in templates:
        raise HTTPException(status_code=404, detail="Template not found")

    config_path = os.path.join(BASE_DIR, 'config', 'templates.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    config['active_template'] = template_id
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    return {"success": True, "active_template": template_id, "message": f"Template set to {template_id}"}


@app.get("/api/config")
def get_config():
    settings = session_manager.get_settings()
    return settings


@app.put("/api/config")
def update_config(body: dict):
    settings = session_manager.get_settings()
    for key, value in body.items():
        if key in settings:
            settings[key] = value

    config_path = os.path.join(BASE_DIR, 'config', 'settings.json')
    with open(config_path, 'w') as f:
        json.dump(settings, f, indent=2)

    return {"success": True, "message": "Configuration updated"}


if __name__ == "__main__":
    import uvicorn
    settings = session_manager.get_settings()
    host = settings.get('server_address', '0.0.0.0')
    port = settings.get('server_port', 8000)
    local_ip = get_local_ip()

    print("=" * 50)
    print("  PHOTOBOOTH SERVER")
    print("=" * 50)
    print(f"  Local:    http://localhost:{port}")
    print(f"  Network:  http://{local_ip}:{port}")
    print(f"  Health:   http://{local_ip}:{port}/health")
    print("=" * 50)
    print("  Press Ctrl+C to stop")
    print("=" * 50)

    uvicorn.run(app, host=host, port=port, log_level="info")
