from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(_BACKEND_DIR / ".env"),
            str(_REPO_ROOT / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SaarthiAI"
    environment: str = Field(default="development", validation_alias="ENV")

    data_path: str = "app/data/schemes.json"
    vector_store_path: str = "app/vector_store/index.faiss"

    offline_only: bool = Field(default=False, validation_alias="OFFLINE_ONLY")

    azure_openai_endpoint: Optional[str] = Field(default=None, validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: Optional[str] = Field(default=None, validation_alias="AZURE_OPENAI_API_KEY")
    azure_openai_deployment: Optional[str] = Field(default=None, validation_alias="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field(
        default="2025-01-01-preview",
        validation_alias="AZURE_OPENAI_API_VERSION",
    )

    brightdata_api_token: Optional[str] = Field(default=None, validation_alias="BRIGHTDATA_API_TOKEN")
    brightdata_serp_zone: Optional[str] = Field(default=None, validation_alias="BRIGHTDATA_SERP_ZONE")
    brightdata_unlocker_zone: Optional[str] = Field(default=None, validation_alias="BRIGHTDATA_UNLOCKER_ZONE")
    brightdata_request_url: str = Field(
        default="https://api.brightdata.com/request",
        validation_alias="BRIGHTDATA_REQUEST_URL",
    )
    brightdata_serp_timeout_seconds: float = Field(
        default=25.0,
        validation_alias="BRIGHTDATA_SERP_TIMEOUT_SECONDS",
    )

    brightdata_dc_host: Optional[str] = Field(default=None, validation_alias="BRIGHTDATA_DC_HOST")
    brightdata_dc_port: Optional[int] = Field(default=None, validation_alias="BRIGHTDATA_DC_PORT")
    brightdata_dc_user: Optional[str] = Field(default=None, validation_alias="BRIGHTDATA_DC_USER")
    brightdata_dc_pass: Optional[str] = Field(default=None, validation_alias="BRIGHTDATA_DC_PASS")

    # Azure Speech/Cognitive Services settings
    azure_speech_key: Optional[str] = Field(default=None, validation_alias="AZURE_SPEECH_KEY")
    azure_speech_region: Optional[str] = Field(default=None, validation_alias="AZURE_SPEECH_REGION")
    azure_blob_connection_string: Optional[str] = Field(
        default=None, validation_alias="AZURE_BLOB_CONNECTION_STRING"
    )

    def azure_openai_configured(self) -> bool:
        return bool(
            self.azure_openai_endpoint
            and self.azure_openai_api_key
            and self.azure_openai_deployment
        )

    def brightdata_serp_configured(self) -> bool:
        return bool(self.brightdata_api_token and self.brightdata_serp_zone)

    def azure_speech_configured(self) -> bool:
        return bool(self.azure_speech_key and self.azure_speech_region)


settings = Settings()
