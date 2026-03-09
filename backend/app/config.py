import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SaarthiAI"
    environment: str = os.getenv("ENV", "development")
    data_path: str = "backend/app/data/schemes.json"
    vector_store_path: str = "backend/app/vector_store/index.faiss"

    class Config:
        env_file = ".env"

settings = Settings()
