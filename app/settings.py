#from pydantic import BaseSettings
from pydantic_settings import BaseSettings   # <-- changed import
from pydantic import ConfigDict
import yaml
import os

class Settings(BaseSettings):
    llm_model: str
    embedding_model: str
    data_dir: str
    db_dir: str
    postgres_url: str
    default_pdf_name: str   # <-- NEW

    class ConfigDict:
        extra = "forbid"  # (default in pydantic v2, means no extra keys allowed)

def load_settings(path: str = None) -> Settings:
    path = path or os.getenv("CONFIG_PATH", "config.yaml")
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return Settings(**cfg)

settings = load_settings()
