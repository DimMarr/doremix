from PIL import Image
import io
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException


# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
UPLOAD_DIR = "/app/uploads/covers"
WEBP_QUALITY = 80


def validate_image(file: UploadFile) -> None:
    extension = Path(file.filename).suffix.lstrip(".").lower()

    if not extension:
        raise HTTPException(status_code=400, detail="File has no extension")

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )


def convert_to_webp(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes))

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    output = io.BytesIO()
    image.save(output, format="WEBP", quality=WEBP_QUALITY, optimize=True)
    output.seek(0)

    return output.read()


def save_cover_image(file: UploadFile, playlist_id: int) -> str:
    validate_image(file)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    image_bytes = file.file.read()

    webp_bytes = convert_to_webp(image_bytes)

    filename = f"playlist_{playlist_id}.webp"

    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(webp_bytes)

    return f"{filename}"
