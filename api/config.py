import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SaarthiAI"
    environment: str = os.getenv("ENV", "development")
    data_path: str = "api/data/schemes.json"
    vector_store_path: str = "api/vector_store/index.npy"
    huggingface_api_token: str = os.getenv("HUGGINGFACE_API_TOKEN", "")

    class Config:
        env_file = ".env"

settings = Settings()
