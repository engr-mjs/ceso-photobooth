import os
import sys
import json
import socket
from contextlib import asynccontextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from routers.api import router as api_router

CONFIG_DIR = os.path.join(ROOT_DIR, "config")
SESSIONS_DIR = os.path.join(ROOT_DIR, "sessions")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend", "public")


def load_settings() -> dict:
    settings_path = os.path.join(CONFIG_DIR, "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as f:
            return json.load(f)
    return {}


settings = load_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "qrcodes"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "photos"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)

    host = get_local_ip()
    port = settings.get("server", {}).get("port", 8000)
    print(f"\n{'='*60}")
    print(f"  CESO Photobooth Server")
    print(f"{'='*60}")
    print(f"  Local:   http://localhost:{port}")
    print(f"  Network: http://{host}:{port}")
    print(f"{'='*60}\n")

    yield


app = FastAPI(
    title="CESO Photobooth",
    description="Professional Offline Web-Based Photobooth System",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins = settings.get("server", {}).get("cors_origins", ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="")


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


DOWNLOAD_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CESO Photobooth - Download</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #1a365d;
        }
        .container {
            max-width: 400px;
            width: 100%;
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a365d 0%, #2d5a9e 100%);
            padding: 24px;
            text-align: center;
            color: white;
        }
        .header h1 { font-family: 'Poppins', sans-serif; font-size: 20px; font-weight: 700; margin-bottom: 4px; }
        .header p { font-size: 13px; opacity: 0.8; }
        .content { padding: 24px; text-align: center; }
        .strip-preview { width: 200px; margin: 0 auto 24px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
        .download-btn {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 14px 32px; background: #1a365d; color: white;
            font-size: 16px; font-weight: 600; border: none; border-radius: 16px;
            cursor: pointer; text-decoration: none; transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(26, 54, 93, 0.3);
        }
        .download-btn:hover { background: #152d50; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(26, 54, 93, 0.4); }
        .download-btn svg { width: 20px; height: 20px; }
        .footer { padding: 16px 24px; text-align: center; border-top: 1px solid #f1f3f5; }
        .footer p { font-size: 12px; color: #adb5bd; }
        .loading { padding: 40px; text-align: center; }
        .spinner { width: 40px; height: 40px; border: 3px solid #e9ecef; border-top-color: #1a365d; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .error { padding: 40px 24px; text-align: center; }
        .error-icon { width: 48px; height: 48px; background: #fee2e2; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
        .error h2 { font-size: 18px; margin-bottom: 8px; }
        .error p { font-size: 14px; color: #666; }
    </style>
</head>
<body>
    <div class="container" id="app">
        <div class="loading">
            <div class="spinner"></div>
            <p>Loading your photo strip...</p>
        </div>
    </div>
    <script>
        const sessionId = window.location.pathname.split('/').pop();
        const app = document.getElementById('app');
        async function loadStrip() {
            try {
                const response = await fetch('/api/session/' + sessionId + '/info');
                if (!response.ok) throw new Error('Session not found');
                app.innerHTML = '<div class="header"><h1>CESO Photobooth</h1><p>Your photo strip is ready!</p></div><div class="content"><img class="strip-preview" src="/api/preview/' + sessionId + '" alt="Photo Strip" onerror="this.style.display=\'none\'" /><a class="download-btn" href="/api/download/' + sessionId + '" download><svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>Download Photo Strip</a></div><div class="footer"><p>CESO Photobooth &mdash; Capture Memories</p></div>';
            } catch (error) {
                app.innerHTML = '<div class="error"><div class="error-icon"><svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#ef4444"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg></div><h2>Strip Not Found</h2><p>This photo strip may have expired or is not available.</p></div>';
            }
        }
        loadStrip();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CESO Photobooth</title>
        <style>
            body { font-family: sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            h1 { color: #1a365d; }
            p { color: #666; }
            .status { color: #38a169; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CESO Photobooth</h1>
            <p>Professional Offline Photobooth System</p>
            <p class="status">Server is running</p>
            <p>Open the frontend application to start capturing photos.</p>
        </div>
    </body>
    </html>
    """


@app.get("/download/{session_id}", response_class=HTMLResponse)
async def download_page(session_id: str):
    return DOWNLOAD_PAGE_HTML


if __name__ == "__main__":
    import uvicorn

    host = settings.get("server", {}).get("host", "0.0.0.0")
    port = settings.get("server", {}).get("port", 8000)
    uvicorn.run("main:app", host=host, port=port, reload=True)
