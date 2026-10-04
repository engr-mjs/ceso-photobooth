import os
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw
from typing import List, Optional, Tuple


class ImageProcessor:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.template_config = self._load_template_config()

    def _load_template_config(self) -> dict:
        config_path = os.path.join(self.config_dir, "template.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return self._get_default_config()

    def _get_default_config(self) -> dict:
        return {
            "template_name": "default",
            "template_file": "templates/default.png",
            "output_width": 600,
            "output_height": 1800,
            "photo_slots": [
                {"slot_index": 1, "x": 30, "y": 100, "width": 540, "height": 400, "border_radius": 12},
                {"slot_index": 2, "x": 30, "y": 550, "width": 540, "height": 400, "border_radius": 12},
                {"slot_index": 3, "x": 30, "y": 1000, "width": 540, "height": 400, "border_radius": 12},
            ],
            "background_color": "#FFFFFF"
        }

    def reload_config(self):
        self.template_config = self._load_template_config()

    def decode_base64_image(self, base64_data: str) -> Image.Image:
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]
        image_data = base64.b64decode(base64_data)
        return Image.open(BytesIO(image_data)).convert("RGBA")

    def resize_image_to_slot(
        self, image: Image.Image, slot_width: int, slot_height: int
    ) -> Image.Image:
        img_ratio = image.width / image.height
        slot_ratio = slot_width / slot_height

        if img_ratio > slot_ratio:
            new_width = slot_width
            new_height = int(slot_width / img_ratio)
        else:
            new_height = slot_height
            new_width = int(slot_height * img_ratio)

        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        result = Image.new("RGBA", (slot_width, slot_height), (0, 0, 0, 0))
        offset_x = (slot_width - new_width) // 2
        offset_y = (slot_height - new_height) // 2
        result.paste(resized, (offset_x, offset_y), resized)

        return result

    def create_rounded_mask(self, width: int, height: int, radius: int) -> Image.Image:
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (width - 1, height - 1)], radius=radius, fill=255)
        return mask

    def generate_strip(
        self,
        photo_paths: List[str],
        output_path: str,
        template_path: Optional[str] = None,
    ) -> str:
        config = self.template_config
        output_width = config.get("output_width", 600)
        output_height = config.get("output_height", 1800)
        bg_color = config.get("background_color", "#FFFFFF")
        slots = config.get("photo_slots", [])

        bg_rgb = tuple(int(bg_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        strip = Image.new("RGBA", (output_width, output_height), bg_rgb + (255,))

        template_path = template_path or config.get("template_file")
        if template_path and os.path.exists(template_path):
            template = Image.open(template_path).convert("RGBA")
            template = template.resize((output_width, output_height), Image.Resampling.LANCZOS)
            
            for i, photo_path in enumerate(photo_paths):
                if i >= len(slots):
                    break
                slot = slots[i]
                photo = Image.open(photo_path).convert("RGBA")
                resized_photo = self.resize_image_to_slot(
                    photo, slot["width"], slot["height"]
                )
                
                border_radius = slot.get("border_radius", 0)
                if border_radius > 0:
                    mask = self.create_rounded_mask(
                        slot["width"], slot["height"], border_radius
                    )
                    resized_photo.putalpha(mask)
                
                strip.paste(resized_photo, (slot["x"], slot["y"]), resized_photo)
            
            strip = Image.alpha_composite(strip, template)
        else:
            for i, photo_path in enumerate(photo_paths):
                if i >= len(slots):
                    break
                slot = slots[i]
                photo = Image.open(photo_path).convert("RGBA")
                resized_photo = self.resize_image_to_slot(
                    photo, slot["width"], slot["height"]
                )
                
                border_radius = slot.get("border_radius", 0)
                if border_radius > 0:
                    mask = self.create_rounded_mask(
                        slot["width"], slot["height"], border_radius
                    )
                    resized_photo.putalpha(mask)
                
                strip.paste(resized_photo, (slot["x"], slot["y"]), resized_photo)

        strip_rgb = strip.convert("RGB")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        strip_rgb.save(output_path, "PNG", quality=95)
        return output_path

    def save_photo_from_base64(
        self, base64_data: str, output_path: str
    ) -> str:
        image = self.decode_base64_image(base64_data)
        rgb_image = image.convert("RGB")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        rgb_image.save(output_path, "PNG", quality=95)
        return output_path

    def get_image_info(self, image_path: str) -> dict:
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": os.path.getsize(image_path),
            }
