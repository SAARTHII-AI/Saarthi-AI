from deep_translator import GoogleTranslator
from langdetect import detect
import logging

logger = logging.getLogger(__name__)

class TranslatorService:
    def __init__(self):
        # We will keep instances around if needed, though GoogleTranslator can be dynamic
        pass
        
    def detect_language(self, text: str) -> str:
        """
        Detects the language of the given text.
        Returns 'hi', 'ta', 'en', etc.
        Falls back to 'en' if detection fails.
        """
        try:
            # Langdetect might return variants like 'hi' or 'en'
            lang_code = detect(text)
            return lang_code
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en"
            
    def translate_text(self, text: str, source: str = "auto", target: str = "en") -> str:
        """
        Translates text from source language to target language.
        """
        # If text is empty or source and target are explicitly the same
        if not text or source == target:
            return text
            
        try:
            translator = GoogleTranslator(source=source, target=target)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            logger.error(f"Translation failed from {source} to {target}: {e}")
            # Fallback to original text if translation fails
            return text

translator_service = TranslatorService()
