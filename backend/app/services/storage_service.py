from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


class LocalStorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_dir = Path(settings.storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload: UploadFile, category: str) -> str:
        destination_dir = self.base_dir / category
        destination_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(upload.filename or "").suffix or ".bin"
        filename = f"{uuid4()}{suffix}"
        destination = destination_dir / filename
        content = await upload.read()
        destination.write_bytes(content)
        await upload.seek(0)
        return str(destination)
