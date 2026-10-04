import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
from typing import Optional


class QRGenerator:
    def __init__(self, qr_dir: str):
        self.qr_dir = qr_dir
        os.makedirs(qr_dir, exist_ok=True)

    def generate(
        self,
        data: str,
        output_path: str,
        box_size: int = 10,
        border: int = 2,
        fill_color: str = "#1a365d",
        back_color: str = "#FFFFFF",
        error_correction: str = "M",
    ) -> str:
        ec_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }
        ec_level = ec_map.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M)

        qr = qrcode.QRCode(
            version=None,
            error_correction=ec_level,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        try:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(
                    back_color=Image.new("RGB", (1, 1), back_color),
                    front_color=Image.new("RGB", (1, 1), fill_color),
                ),
            )
        except Exception:
            img = qr.make_image(fill_color=fill_color, back_color=back_color)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        return output_path

    def generate_with_logo(
        self,
        data: str,
        output_path: str,
        logo_path: Optional[str] = None,
        logo_size_ratio: float = 0.25,
        **kwargs,
    ) -> str:
        qr_path = self.generate(data, output_path, **kwargs)

        if logo_path and os.path.exists(logo_path):
            qr_img = Image.open(qr_path).convert("RGBA")
            logo = Image.open(logo_path).convert("RGBA")

            logo_max_size = int(min(qr_img.width, qr_img.height) * logo_size_ratio)
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

            logo_pos = (
                (qr_img.width - logo.width) // 2,
                (qr_img.height - logo.height) // 2,
            )

            qr_img.paste(logo, logo_pos, logo)
            qr_img.save(qr_path)

        return qr_path

    def create_download_url(self, host: str, port: int, session_id: str) -> str:
        if port in (80, 443):
            return f"http://{host}/download/{session_id}"
        return f"http://{host}:{port}/download/{session_id}"

    def delete_qr(self, qr_path: str) -> bool:
        if os.path.exists(qr_path):
            os.remove(qr_path)
            return True
        return False
