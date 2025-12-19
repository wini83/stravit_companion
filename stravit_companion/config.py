# stravit_companion/config.py
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    db_path: Path = BASE_DIR / "stravit.db"
    stravit_base_url: str
    stravit_email: str
    stravit_password: str
    stravit_csv_link: str
    my_name: str
    pushover_user: str
    pushover_token: str
    pushover_title: str = "Stravit Companion"
    pushover_priority: int = 0

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="",  # ważne: brak prefiksu
    )


settings = Settings()  # type: ignore[call-arg]
