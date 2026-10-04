import os
import json
import socket
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image, ImageDraw

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
QRCODES_DIR = os.path.join(BASE_DIR, 'qrcodes')


def get_settings() -> dict:
    config_path = os.path.join(BASE_DIR, 'config', 'settings.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_download_host() -> str:
    ip = get_local_ip()
    if ip and ip != "127.0.0.1":
        return ip
    return get_settings().get('host_display', 'localhost')


def generate_qr_code(session_id: str, download_url: str) -> str:
    os.makedirs(QRCODES_DIR, exist_ok=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(download_url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color='#1a3a6b',
        back_color='white'
    )

    qr_path = os.path.join(QRCODES_DIR, f"{session_id}.png")
    qr_img.save(qr_path, 'PNG')
    return qr_path


def create_display_qr(session_id: str, qr_path: str) -> str:
    download_url = get_download_url(session_id)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(download_url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color='#1a3a6b',
        back_color='white'
    )

    display_path = os.path.join(QRCODES_DIR, f"{session_id}_display.png")
    qr_img.save(display_path, 'PNG')
    return display_path


def get_download_url(session_id: str) -> str:
    settings = get_settings()
    host = get_download_host()
    port = settings.get('server_port', 8000)
    return f"http://{host}:{port}/download/{session_id}"


def get_qr_base64(qr_path: str) -> str:
    import base64
    with open(qr_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')
