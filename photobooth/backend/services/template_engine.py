import os
import json
from typing import Dict, List
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
TEMPLATES_CONFIG_PATH = os.path.join(CONFIG_DIR, 'templates.json')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


def load_templates_config() -> dict:
    with open(TEMPLATES_CONFIG_PATH, 'r') as f:
        return json.load(f)


def get_active_template() -> dict:
    config = load_templates_config()
    active_id = config.get('active_template', 'default_strip')
    return config['templates'].get(active_id, {})


def get_active_template_id() -> str:
    config = load_templates_config()
    return config.get('active_template', 'default_strip')


def get_all_templates() -> Dict[str, dict]:
    config = load_templates_config()
    return config.get('templates', {})


def get_template_image(template_id: str = None) -> Image.Image:
    config = load_templates_config()
    if template_id is None:
        template_id = config.get('active_template', 'default_strip')

    template_config = config['templates'].get(template_id)
    if not template_config:
        raise ValueError(f"Template '{template_id}' not found in configuration")

    template_path = os.path.join(TEMPLATES_DIR, template_config['filename'])

    if not os.path.exists(template_path):
        return create_placeholder_template(template_config)

    img = Image.open(template_path).convert('RGBA')
    return img


def create_placeholder_template(template_config: dict) -> Image.Image:
    width = template_config.get('output_width', 1800)
    height = template_config.get('output_height', 3200)
    bg_color = template_config.get('background_color', [255, 255, 255, 255])

    img = Image.new('RGBA', (width, height), tuple(bg_color))

    draw_area_color = (240, 240, 240, 255)
    for slot in template_config.get('photo_slots', []):
        x, y, w, h = slot['x'], slot['y'], slot['width'], slot['height']
        draw_area = Image.new('RGBA', (w, h), draw_area_color)
        img.paste(draw_area, (x, y))

    template_path = os.path.join(TEMPLATES_DIR, template_config['filename'])
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    img.save(template_path, 'PNG')

    return img


def fit_image_to_slot(
    image: Image.Image,
    slot_width: int,
    slot_height: int,
    fit_mode: str = 'cover'
) -> Image.Image:
    img_w, img_h = image.size
    slot_ratio = slot_width / slot_height
    img_ratio = img_w / img_h

    if fit_mode == 'cover':
        if img_ratio > slot_ratio:
            new_h = slot_height
            new_w = int(img_ratio * slot_height)
        else:
            new_w = slot_width
            new_h = int(slot_width / img_ratio)
    elif fit_mode == 'contain':
        if img_ratio > slot_ratio:
            new_w = slot_width
            new_h = int(slot_width / img_ratio)
        else:
            new_h = slot_height
            new_w = int(img_ratio * slot_height)
    else:
        new_w = slot_width
        new_h = slot_height

    resized = image.resize((new_w, new_h), Image.LANCZOS)

    if fit_mode == 'cover':
        left = (new_w - slot_width) // 2
        top = (new_h - slot_height) // 2
        resized = resized.crop((left, top, left + slot_width, top + slot_height))

    return resized


def generate_strip(photo_paths: List[str], session_dir: str, template_id: str = None) -> str:
    template_img = get_template_image(template_id)
    config = load_templates_config()
    active_id = template_id or config.get('active_template', 'default_strip')
    template_config = config['templates'][active_id]
    photo_slots = template_config['photo_slots']
    fit_mode = template_config.get('photo_fit_mode', 'cover')

    if len(photo_paths) != len(photo_slots):
        raise ValueError(f"Expected {len(photo_slots)} photos but got {len(photo_paths)}")

    strip = template_img.copy()

    for i, (photo_path, slot) in enumerate(zip(photo_paths, photo_slots)):
        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"Photo not found: {photo_path}")

        photo = Image.open(photo_path).convert('RGBA')
        fitted_photo = fit_image_to_slot(photo, slot['width'], slot['height'], fit_mode)

        mask = Image.new('L', fitted_photo.size, 255)
        strip.paste(fitted_photo, (slot['x'], slot['y']), mask)

    output_path = os.path.join(session_dir, 'strip.png')
    strip.save(output_path, 'PNG', quality=95)

    strips_archive = os.path.join(BASE_DIR, 'photos', 'strips')
    os.makedirs(strips_archive, exist_ok=True)
    session_id = os.path.basename(session_dir)
    archive_path = os.path.join(strips_archive, f"{session_id}_strip.png")
    strip.save(archive_path, 'PNG', quality=95)

    return output_path
