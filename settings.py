from pydantic import BaseSettings
import yaml

class Settings(BaseSettings):
    llm_model: str
    embedding_model: str
    data_dir: str
    db_dir: str
    postgres_url: str

def load_settings(path="config.yaml"):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return Settings(**cfg)

settings = load_settings()
