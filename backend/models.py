from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SessionCreate(BaseModel):
    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    session_id: str
    photo1_path: Optional[str] = None
    photo2_path: Optional[str] = None
    photo3_path: Optional[str] = None
    strip_path: Optional[str] = None
    qr_path: Optional[str] = None
    metadata: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CaptureRequest(BaseModel):
    photos: List[str]
    session_id: str


class GenerateStripRequest(BaseModel):
    session_id: str
    template_name: Optional[str] = "default"


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


class PhotoSlotConfig(BaseModel):
    slot_index: int
    x: int
    y: int
    width: int
    height: int
    border_radius: int = 0


class TemplateConfig(BaseModel):
    template_name: str
    template_file: str
    output_width: int
    output_height: int
    photo_slots: List[PhotoSlotConfig]
    background_color: str = "#FFFFFF"


class AppSettings(BaseModel):
    app: dict
    server: dict
    camera: dict
    capture: dict
    output: dict
    qr: dict
    session: dict
    template: dict
    paths: dict
