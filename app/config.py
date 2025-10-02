from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


def default_database_url() -> str:
    return f"sqlite:///{(BASE_DIR / 'jarvault.db').as_posix()}"


def default_storage_dir() -> str:
    return (BASE_DIR / "mods").as_posix()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8")

    database_url: str = Field(default_factory=default_database_url)
    storage_dir: str = Field(default_factory=default_storage_dir, alias="STORAGE_DIR")
    delete_password: Optional[str] = Field(default=None, alias="PASSWORD")


settings = Settings()
