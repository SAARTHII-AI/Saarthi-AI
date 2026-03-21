import logging
import uuid
import requests
from deep_translator import GoogleTranslator
from langdetect import detect
from app.config import settings

logger = logging.getLogger(__name__)


class TranslatorService:
    def __init__(self):
        self._azure_available = None

    @property
    def azure_available(self) -> bool:
        if self._azure_available is None:
            self._azure_available = bool(
                settings.azure_translator_key
                and not settings.offline_only
            )
        return self._azure_available

    def detect_language(self, text: str) -> str:
        if self.azure_available:
            try:
                return self._azure_detect(text)
            except Exception as e:
                logger.warning(f"Azure language detection failed, falling back: {e}")
        try:
            lang_code = detect(text)
            return lang_code
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en"

    def translate_text(self, text: str, source: str = "auto", target: str = "en") -> str:
        if not text or source == target:
            return text

        if self.azure_available:
            try:
                return self._azure_translate(text, source, target)
            except Exception as e:
                logger.warning(f"Azure translation failed, falling back: {e}")

        try:
            translator = GoogleTranslator(source=source, target=target)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            logger.error(f"Translation failed from {source} to {target}: {e}")
            return text

    def _azure_detect(self, text: str) -> str:
        url = f"{settings.azure_translator_endpoint}/detect?api-version=3.0"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.azure_translator_key,
            "Ocp-Apim-Subscription-Region": settings.azure_translator_region,
            "Content-Type": "application/json",
        }
        body = [{"Text": text}]
        resp = requests.post(url, headers=headers, json=body, timeout=5)
        resp.raise_for_status()
        result = resp.json()
        return result[0]["language"]

    def _azure_translate(self, text: str, source: str, target: str) -> str:
        params = {"api-version": "3.0", "to": target}
        if source and source != "auto":
            params["from"] = source

        url = f"{settings.azure_translator_endpoint}/translate"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.azure_translator_key,
            "Ocp-Apim-Subscription-Region": settings.azure_translator_region,
            "Content-Type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }
        body = [{"Text": text}]
        resp = requests.post(url, headers=headers, json=body, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        return result[0]["translations"][0]["text"]


translator_service = TranslatorService()
