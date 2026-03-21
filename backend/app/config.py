import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SaarthiAI"
    environment: str = "development"
    data_path: str = "app/data/schemes.json"
    vector_store_path: str = "app/vector_store/index.faiss"

    offline_only: bool = False

    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_deployment: Optional[str] = None
    azure_openai_api_version: str = "2025-01-01-preview"

    azure_translator_key: Optional[str] = None
    azure_translator_endpoint: str = "https://api.cognitive.microsofttranslator.com"
    azure_translator_region: str = "eastus"

    azure_speech_key: Optional[str] = None
    azure_speech_region: str = "eastus"

    brightdata_api_token: Optional[str] = None
    brightdata_serp_zone: Optional[str] = None
    brightdata_dc_host: Optional[str] = None
    brightdata_dc_port: Optional[int] = None
    brightdata_dc_user: Optional[str] = None
    brightdata_dc_pass: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
