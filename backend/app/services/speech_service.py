"""
Speech Service for Saarthi-AI using Azure Cognitive Services.

Provides Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities with
fallback to browser APIs when Azure is not configured.

Supported languages:
- Hindi (hi-IN)
- English (en-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
"""

import base64
import logging
from typing import Optional, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Azure Speech voice mappings for Indian languages
VOICE_MAPPINGS: Dict[str, str] = {
    "hi-IN": "hi-IN-SwaraNeural",      # Hindi female voice
    "hi-IN-male": "hi-IN-MadhurNeural", # Hindi male voice
    "en-IN": "en-IN-NeerjaNeural",      # English (India) female voice
    "en-IN-male": "en-IN-PrabhatNeural", # English (India) male voice
    "ta-IN": "ta-IN-PallaviNeural",     # Tamil female voice
    "ta-IN-male": "ta-IN-ValluvarNeural", # Tamil male voice
    "te-IN": "te-IN-ShrutiNeural",      # Telugu female voice
    "te-IN-male": "te-IN-MohanNeural",  # Telugu male voice
}

# Fallback voice mappings (using standard locale codes)
DEFAULT_VOICE = "hi-IN-SwaraNeural"

# Language code normalization (simple codes to full locale codes)
LANGUAGE_NORMALIZATION: Dict[str, str] = {
    "hi": "hi-IN",
    "en": "en-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "hindi": "hi-IN",
    "english": "en-IN",
    "tamil": "ta-IN",
    "telugu": "te-IN",
}


class SpeechServiceError(Exception):
    """Custom exception for speech service errors."""
    pass


class SpeechService:
    """
    Speech service providing TTS and STT capabilities using Azure Cognitive Services.
    Falls back to browser APIs when Azure is not configured.
    """

    def __init__(self):
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def provider(self) -> str:
        """Returns the current speech provider based on configuration."""
        return "azure" if settings.azure_speech_configured() else "browser"

    @property
    def is_configured(self) -> bool:
        """Check if Azure Speech is properly configured."""
        return settings.azure_speech_configured()

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an async HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self):
        """Close the HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def _normalize_language(self, language: str) -> str:
        """Normalize language code to full locale format (e.g., 'hi' -> 'hi-IN')."""
        lang_lower = language.lower().strip()
        return LANGUAGE_NORMALIZATION.get(lang_lower, language)

    def _get_voice_name(self, language: str, gender: str = "female") -> str:
        """Get the appropriate Azure voice name for a language."""
        normalized_lang = self._normalize_language(language)

        if gender.lower() == "male":
            voice_key = f"{normalized_lang}-male"
            return VOICE_MAPPINGS.get(voice_key, VOICE_MAPPINGS.get(normalized_lang, DEFAULT_VOICE))

        return VOICE_MAPPINGS.get(normalized_lang, DEFAULT_VOICE)

    async def text_to_speech(
        self,
        text: str,
        language: str = "hi-IN",
        gender: str = "female",
        output_format: str = "audio-16khz-128kbitrate-mono-mp3"
    ) -> bytes:
        """
        Convert text to speech audio using Azure TTS.

        Args:
            text: The text to convert to speech
            language: Language code (hi-IN, en-IN, ta-IN, te-IN, or short codes)
            gender: Voice gender ('female' or 'male')
            output_format: Audio output format (default: MP3)

        Returns:
            Audio data as bytes

        Raises:
            SpeechServiceError: If Azure is not configured or API call fails
        """
        if not self.is_configured:
            raise SpeechServiceError(
                "Azure Speech not configured. Use browser TTS as fallback.",
                {"use_browser_api": True, "text": text, "language": language}
            )

        normalized_lang = self._normalize_language(language)
        voice_name = self._get_voice_name(language, gender)

        # Construct SSML for better speech control
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{normalized_lang}'>
            <voice name='{voice_name}'>
                {self._escape_ssml(text)}
            </voice>
        </speak>
        """.strip()

        # Azure Speech TTS REST API endpoint
        tts_url = f"https://{settings.azure_speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"

        headers = {
            "Ocp-Apim-Subscription-Key": settings.azure_speech_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": output_format,
            "User-Agent": "SaarthiAI-SpeechService",
        }

        try:
            client = await self._get_client()
            response = await client.post(tts_url, content=ssml, headers=headers)

            if response.status_code == 200:
                logger.info(f"TTS successful for {len(text)} chars in {normalized_lang}")
                return response.content
            elif response.status_code == 401:
                raise SpeechServiceError("Azure Speech authentication failed. Check API key.")
            elif response.status_code == 429:
                raise SpeechServiceError("Azure Speech rate limit exceeded. Try again later.")
            else:
                error_detail = response.text[:200] if response.text else "No details"
                raise SpeechServiceError(
                    f"Azure TTS failed with status {response.status_code}: {error_detail}"
                )

        except httpx.TimeoutException:
            raise SpeechServiceError("Azure TTS request timed out")
        except httpx.RequestError as e:
            raise SpeechServiceError(f"Azure TTS network error: {str(e)}")

    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "hi-IN",
        audio_format: str = "audio/wav"
    ) -> str:
        """
        Convert speech audio to text using Azure STT.

        Args:
            audio_data: Audio data as bytes (WAV, MP3, or other supported formats)
            language: Language code for recognition
            audio_format: MIME type of the audio (e.g., 'audio/wav', 'audio/mp3')

        Returns:
            Transcribed text

        Raises:
            SpeechServiceError: If Azure is not configured or API call fails
        """
        if not self.is_configured:
            raise SpeechServiceError(
                "Azure Speech not configured. Use browser STT as fallback.",
                {"use_browser_api": True, "language": language}
            )

        normalized_lang = self._normalize_language(language)

        # Azure Speech STT REST API endpoint
        stt_url = (
            f"https://{settings.azure_speech_region}.stt.speech.microsoft.com/"
            f"speech/recognition/conversation/cognitiveservices/v1"
            f"?language={normalized_lang}"
        )

        # Map common MIME types to Azure content types
        content_type_mapping = {
            "audio/wav": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "audio/wave": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "audio/x-wav": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "audio/mp3": "audio/mpeg",
            "audio/mpeg": "audio/mpeg",
            "audio/ogg": "audio/ogg; codecs=opus",
            "audio/webm": "audio/webm; codecs=opus",
        }

        content_type = content_type_mapping.get(audio_format.lower(), audio_format)

        headers = {
            "Ocp-Apim-Subscription-Key": settings.azure_speech_key,
            "Content-Type": content_type,
            "Accept": "application/json",
        }

        try:
            client = await self._get_client()
            response = await client.post(stt_url, content=audio_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                recognition_status = result.get("RecognitionStatus", "Unknown")

                if recognition_status == "Success":
                    text = result.get("DisplayText", "")
                    logger.info(f"STT successful: {len(text)} chars recognized in {normalized_lang}")
                    return text
                elif recognition_status == "NoMatch":
                    logger.warning("STT: No speech could be recognized")
                    return ""
                elif recognition_status == "InitialSilenceTimeout":
                    logger.warning("STT: Initial silence timeout")
                    return ""
                else:
                    raise SpeechServiceError(f"STT recognition failed: {recognition_status}")

            elif response.status_code == 401:
                raise SpeechServiceError("Azure Speech authentication failed. Check API key.")
            elif response.status_code == 429:
                raise SpeechServiceError("Azure Speech rate limit exceeded. Try again later.")
            else:
                error_detail = response.text[:200] if response.text else "No details"
                raise SpeechServiceError(
                    f"Azure STT failed with status {response.status_code}: {error_detail}"
                )

        except httpx.TimeoutException:
            raise SpeechServiceError("Azure STT request timed out")
        except httpx.RequestError as e:
            raise SpeechServiceError(f"Azure STT network error: {str(e)}")

    def _escape_ssml(self, text: str) -> str:
        """Escape special characters for SSML."""
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&apos;",
        }
        for char, escaped in replacements.items():
            text = text.replace(char, escaped)
        return text

    def get_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Return information about supported languages and voices."""
        return {
            "hi-IN": {
                "name": "Hindi",
                "voices": {
                    "female": "hi-IN-SwaraNeural",
                    "male": "hi-IN-MadhurNeural",
                }
            },
            "en-IN": {
                "name": "English (India)",
                "voices": {
                    "female": "en-IN-NeerjaNeural",
                    "male": "en-IN-PrabhatNeural",
                }
            },
            "ta-IN": {
                "name": "Tamil",
                "voices": {
                    "female": "ta-IN-PallaviNeural",
                    "male": "ta-IN-ValluvarNeural",
                }
            },
            "te-IN": {
                "name": "Telugu",
                "voices": {
                    "female": "te-IN-ShrutiNeural",
                    "male": "te-IN-MohanNeural",
                }
            },
        }

    def get_status(self) -> Dict[str, Any]:
        """Return the current status of the speech service."""
        return {
            "provider": self.provider,
            "configured": self.is_configured,
            "supported_languages": list(self.get_supported_languages().keys()),
            "azure_region": settings.azure_speech_region if self.is_configured else None,
        }


# Singleton instance
speech_service = SpeechService()
