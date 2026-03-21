import logging
import base64
import requests
from app.config import settings

logger = logging.getLogger(__name__)

AZURE_VOICE_MAP = {
    "hi": "hi-IN-SwaraNeural",
    "en": "en-IN-NeerjaNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "bn": "bn-IN-TanishaaNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "pa": "pa-IN-GurleenNeural",
    "ur": "ur-IN-GulNeural",
}


class SpeechService:
    def __init__(self):
        self._azure_available = None

    @property
    def azure_available(self) -> bool:
        if self._azure_available is None:
            self._azure_available = bool(
                settings.azure_speech_key
                and not settings.offline_only
            )
        return self._azure_available

    def text_to_speech(self, text: str, language: str = "hi"):
        if self.azure_available:
            try:
                audio_bytes = self._azure_tts(text, language)
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                return {
                    "audio_base64": audio_b64,
                    "content_type": "audio/mpeg",
                    "use_browser_api": False,
                    "text": text,
                }
            except Exception as e:
                logger.warning(f"Azure TTS failed, falling back to browser API: {e}")

        return {"audio_base64": None, "use_browser_api": True, "text": text}

    def speech_to_text(self, audio_data: bytes, language: str = "hi") -> str:
        if self.azure_available:
            try:
                return self._azure_stt(audio_data, language)
            except Exception as e:
                logger.warning(f"Azure STT failed, falling back: {e}")

        return "Not implemented in MVP - using browser STT instead."

    def _azure_tts(self, text: str, language: str) -> bytes:
        token_url = (
            f"https://{settings.azure_speech_region}.api.cognitive.microsoft.com"
            f"/sts/v1.0/issueToken"
        )
        token_resp = requests.post(
            token_url,
            headers={"Ocp-Apim-Subscription-Key": settings.azure_speech_key},
            timeout=5,
        )
        token_resp.raise_for_status()
        access_token = token_resp.text

        voice = AZURE_VOICE_MAP.get(language, "hi-IN-SwaraNeural")
        lang_tag = f"{language}-IN" if len(language) == 2 else language

        ssml = (
            f"<speak version='1.0' xml:lang='{lang_tag}'>"
            f"<voice name='{voice}'>{text}</voice>"
            f"</speak>"
        )

        tts_url = (
            f"https://{settings.azure_speech_region}.tts.speech.microsoft.com"
            f"/cognitiveservices/v1"
        )
        resp = requests.post(
            tts_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            },
            data=ssml.encode("utf-8"),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.content

    def _azure_stt(self, audio_data: bytes, language: str) -> str:
        lang_locale = f"{language}-IN" if len(language) == 2 else language

        stt_url = (
            f"https://{settings.azure_speech_region}.stt.speech.microsoft.com"
            f"/speech/recognition/conversation/cognitiveservices/v1"
            f"?language={lang_locale}"
        )
        resp = requests.post(
            stt_url,
            headers={
                "Ocp-Apim-Subscription-Key": settings.azure_speech_key,
                "Content-Type": "audio/wav",
            },
            data=audio_data,
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("RecognitionStatus") == "Success":
            return result.get("DisplayText", "")
        return ""


speech_service = SpeechService()
