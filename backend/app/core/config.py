from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI Answer Evaluation API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'storage' / 'evaluation.db').as_posix()}"
    storage_dir: str = str(BACKEND_DIR / "storage" / "uploads")
    enable_demo_fallback: bool = True
    plagiarism_text_threshold: float = 0.92
    plagiarism_structural_threshold: float = 0.85
    evaluation_similarity_threshold: float = 0.62
    ocr_enable_handwriting_model: bool = True
    ocr_handwriting_model_dir: str = str(
        BACKEND_DIR / "training" / "handwriting" / "models" / "trocr-finetuned"
    )
    ocr_device: str = "cpu"
    ocr_max_new_tokens: int = 256
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.ocr_handwriting_model_dir).mkdir(parents=True, exist_ok=True)
    return settings
