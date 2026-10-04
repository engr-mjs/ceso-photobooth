import io
import os
import socket

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from . import config_store


def get_settings() -> dict:
    return config_store.get_settings()


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


def get_public_base_url() -> str:
    for env_var in ('PUBLIC_BASE_URL', 'VERCEL_PROJECT_PRODUCTION_URL', 'VERCEL_URL'):
        value = os.environ.get(env_var)
        if value:
            value = value.strip()
            if not value.startswith('http://') and not value.startswith('https://'):
                value = f"https://{value}"
            return value.rstrip('/')
    settings = get_settings()
    host = get_download_host()
    port = settings.get('server_port', 8000)
    return f"http://{host}:{port}"


def get_public_host() -> str:
    return get_public_base_url().split('://', 1)[-1]


def get_download_url(session_id: str) -> str:
    return f"{get_public_base_url()}/download/{session_id}"


def render_qr(download_url: str, box_size: int = 8, border: int = 3) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(download_url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color='#1a3a6b',
        back_color='white'
    )

    buffer = io.BytesIO()
    qr_img.save(buffer, 'PNG')
    return buffer.getvalue()
