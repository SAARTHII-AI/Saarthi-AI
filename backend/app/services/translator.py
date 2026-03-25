import logging
import uuid
import requests
from deep_translator import GoogleTranslator
from langdetect import detect
from app.config import settings

logger = logging.getLogger(__name__)

TRANSLITERATION_SCRIPTS = {
    "hi": ("Deva", "Latn"),
    "mr": ("Deva", "Latn"),
    "bn": ("Beng", "Latn"),
    "te": ("Telu", "Latn"),
    "ta": ("Taml", "Latn"),
    "gu": ("Gujr", "Latn"),
    "kn": ("Knda", "Latn"),
    "ml": ("Mlym", "Latn"),
    "pa": ("Guru", "Latn"),
    "or": ("Orya", "Latn"),
    "ur": ("Arab", "Latn"),
    "as": ("Beng", "Latn"),
}


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

    def transliterate_text(self, text: str, language: str) -> str | None:
        if not text or language == "en":
            return None

        if not self.azure_available:
            logger.warning("Azure Translator not available for transliteration")
            return None

        script_info = TRANSLITERATION_SCRIPTS.get(language)
        if not script_info:
            logger.warning(f"No transliteration script mapping for language: {language}")
            return None

        from_script, to_script = script_info

        try:
            result = self._azure_transliterate(text, language, from_script, to_script)
            if result and result != text:
                return result
            return None
        except Exception as e:
            logger.warning(f"Transliteration failed for {language}: {e}")
            return None

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

    def _azure_transliterate(self, text: str, language: str, from_script: str, to_script: str) -> str:
        url = f"{settings.azure_translator_endpoint}/transliterate"
        params = {
            "api-version": "3.0",
            "language": language,
            "fromScript": from_script,
            "toScript": to_script,
        }
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
        return result[0]["text"]


translator_service = TranslatorService()
