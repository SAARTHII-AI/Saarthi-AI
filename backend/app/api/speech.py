"""
Speech API endpoints for Text-to-Speech (TTS) and Speech-to-Text (STT).

Provides REST endpoints for converting text to speech audio and
speech audio to text using Azure Cognitive Services.
"""

import base64
import logging
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.speech_service import speech_service, SpeechServiceError

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Request/Response Models ---

class TTSRequest(BaseModel):
    """Request model for text-to-speech conversion."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    language: str = Field(default="hi-IN", description="Language code (hi-IN, en-IN, ta-IN, te-IN)")
    gender: Literal["female", "male"] = Field(default="female", description="Voice gender")
    output_format: str = Field(
        default="audio-16khz-128kbitrate-mono-mp3",
        description="Audio output format"
    )
    return_base64: bool = Field(
        default=True,
        description="Return audio as base64 string (True) or raw audio stream (False)"
    )


class TTSResponse(BaseModel):
    """Response model for text-to-speech conversion."""
    success: bool
    audio_base64: Optional[str] = Field(default=None, description="Base64-encoded audio data")
    content_type: str = Field(default="audio/mpeg", description="MIME type of the audio")
    use_browser_api: bool = Field(default=False, description="Fallback to browser TTS")
    text: Optional[str] = Field(default=None, description="Original text (for browser fallback)")
    language: str = Field(default="hi-IN", description="Language used")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class STTRequest(BaseModel):
    """Request model for speech-to-text conversion."""
    audio_base64: str = Field(..., description="Base64-encoded audio data")
    language: str = Field(default="hi-IN", description="Language code for recognition")
    audio_format: str = Field(
        default="audio/wav",
        description="MIME type of the audio (audio/wav, audio/mp3, audio/webm)"
    )


class STTResponse(BaseModel):
    """Response model for speech-to-text conversion."""
    success: bool
    text: Optional[str] = Field(default=None, description="Transcribed text")
    use_browser_api: bool = Field(default=False, description="Fallback to browser STT")
    language: str = Field(default="hi-IN", description="Language used")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class SpeechStatusResponse(BaseModel):
    """Response model for speech service status."""
    provider: str = Field(description="Current speech provider (azure or browser)")
    configured: bool = Field(description="Whether Azure Speech is configured")
    supported_languages: list = Field(description="List of supported language codes")
    azure_region: Optional[str] = Field(None, description="Azure region if configured")


class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages."""
    languages: dict = Field(description="Dictionary of supported languages and voices")


# --- API Endpoints ---

@router.post("/tts", response_model=TTSResponse, summary="Text to Speech")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech audio using Azure TTS.

    Returns base64-encoded audio in JSON format.
    Falls back to browser API indication when Azure is not configured.
    For raw audio, use /speech/tts/stream.
    """
    try:
        audio_bytes = await speech_service.text_to_speech(
            text=request.text,
            language=request.language,
            gender=request.gender,
            output_format=request.output_format,
        )

        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return TTSResponse(
            success=True,
            audio_base64=audio_base64,
            content_type="audio/mpeg",
            language=request.language,
        )

    except SpeechServiceError as e:
        error_msg = str(e)
        logger.warning(f"TTS error: {error_msg}")

        # Check if this is a "not configured" error - signal browser fallback
        if "not configured" in error_msg.lower():
            return TTSResponse(
                success=False,
                use_browser_api=True,
                text=request.text,
                language=request.language,
                error="Azure Speech not configured. Use browser TTS.",
            )

        # For other errors, still return a response (not HTTP error) for graceful handling
        return TTSResponse(
            success=False,
            use_browser_api=True,
            text=request.text,
            language=request.language,
            error=error_msg,
        )

    except Exception as e:
        logger.error(f"Unexpected TTS error: {str(e)}")
        return TTSResponse(
            success=False,
            use_browser_api=True,
            text=request.text,
            language=request.language,
            error=f"Unexpected error: {str(e)}",
        )


@router.post("/tts/stream", summary="Text to Speech (Audio Stream)")
async def text_to_speech_stream(request: TTSRequest):
    """
    Convert text to speech and return raw audio stream.

    Returns audio file directly without base64 encoding.
    Falls back to HTTP 503 when Azure is not configured.
    """
    try:
        audio_bytes = await speech_service.text_to_speech(
            text=request.text,
            language=request.language,
            gender=request.gender,
            output_format=request.output_format,
        )

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "no-cache",
            }
        )

    except SpeechServiceError as e:
        error_msg = str(e)
        if "not configured" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Azure Speech not configured",
                    "use_browser_api": True,
                    "text": request.text,
                    "language": request.language,
                }
            )
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/stt", response_model=STTResponse, summary="Speech to Text")
async def speech_to_text(request: STTRequest):
    """
    Convert speech audio to text using Azure STT.

    Accepts base64-encoded audio data and returns transcribed text.
    Falls back to browser API indication when Azure is not configured.
    """
    try:
        # Decode base64 audio
        try:
            audio_bytes = base64.b64decode(request.audio_base64)
        except Exception as decode_error:
            return STTResponse(
                success=False,
                language=request.language,
                error=f"Invalid base64 audio data: {str(decode_error)}",
            )

        if len(audio_bytes) == 0:
            return STTResponse(
                success=False,
                language=request.language,
                error="Empty audio data provided",
            )

        text = await speech_service.speech_to_text(
            audio_data=audio_bytes,
            language=request.language,
            audio_format=request.audio_format,
        )

        return STTResponse(
            success=True,
            text=text,
            language=request.language,
        )

    except SpeechServiceError as e:
        error_msg = str(e)
        logger.warning(f"STT error: {error_msg}")

        # Check if this is a "not configured" error - signal browser fallback
        if "not configured" in error_msg.lower():
            return STTResponse(
                success=False,
                use_browser_api=True,
                language=request.language,
                error="Azure Speech not configured. Use browser STT.",
            )

        return STTResponse(
            success=False,
            use_browser_api=True,
            language=request.language,
            error=error_msg,
        )

    except Exception as e:
        logger.error(f"Unexpected STT error: {str(e)}")
        return STTResponse(
            success=False,
            use_browser_api=True,
            language=request.language,
            error=f"Unexpected error: {str(e)}",
        )


@router.get("/status", response_model=SpeechStatusResponse, summary="Speech Service Status")
async def get_speech_status():
    """
    Get the current status of the speech service.

    Returns information about the provider, configuration status,
    and supported languages.
    """
    status = speech_service.get_status()
    return SpeechStatusResponse(**status)


@router.get("/languages", response_model=SupportedLanguagesResponse, summary="Supported Languages")
async def get_supported_languages():
    """
    Get the list of supported languages and their available voices.
    """
    languages = speech_service.get_supported_languages()
    return SupportedLanguagesResponse(languages=languages)
