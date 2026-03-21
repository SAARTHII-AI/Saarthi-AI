"""
Comprehensive service unit tests for Saarthi-AI backend.

Tests cover:
- RAG engine edge cases
- Intent detection with mixed language queries
- Recommendation engine with all occupation types
- Translation service error handling
- Scheme loader with missing/malformed data
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path


# ============================================================================
# RAG Engine Tests
# ============================================================================

class TestRAGEngine:
    """Test RAG engine functionality with edge cases."""

    @pytest.fixture
    def rag_engine(self):
        """Fresh RAG engine instance for each test."""
        from app.services.rag_engine import RAGEngine
        engine = RAGEngine()
        engine.schemes = [
            {
                "name": "PM-KISAN",
                "description": "Farmer support scheme providing income support",
                "eligibility": "All landholding farmers",
                "benefits": "Rs. 6,000 per year"
            },
            {
                "name": "Ayushman Bharat",
                "description": "Health insurance scheme for poor families",
                "eligibility": "BPL families",
                "benefits": "Rs. 5 lakh health cover"
            },
            {
                "name": "Digital India",
                "description": "Digital empowerment for students and youth",
                "eligibility": "Indian students",
                "benefits": "Digital training"
            }
        ]
        return engine

    def test_search_empty_query(self, rag_engine):
        """Test search with empty query."""
        results = rag_engine.search_similar("")
        assert isinstance(results, list)
        # Empty query should return empty results
        assert len(results) == 0

    def test_search_whitespace_query(self, rag_engine):
        """Test search with whitespace-only query."""
        results = rag_engine.search_similar("   \t\n   ")
        assert isinstance(results, list)

    def test_search_single_character(self, rag_engine):
        """Test search with single character query."""
        results = rag_engine.search_similar("a")
        assert isinstance(results, list)

    def test_search_unicode_query(self, rag_engine):
        """Test search with unicode characters."""
        results = rag_engine.search_similar("किसान योजना")
        assert isinstance(results, list)

    def test_search_special_characters(self, rag_engine):
        """Test search with special characters."""
        results = rag_engine.search_similar("!@#$%^&*()")
        assert isinstance(results, list)
        # Special characters only should return empty
        assert len(results) == 0

    def test_search_relevant_keywords(self, rag_engine):
        """Test search with relevant keywords."""
        results = rag_engine.search_similar("farmer support")
        assert len(results) > 0
        # Should find PM-KISAN
        names = [r["name"] for r in results]
        assert "PM-KISAN" in names

    def test_search_health_keywords(self, rag_engine):
        """Test search with health-related keywords."""
        results = rag_engine.search_similar("health insurance")
        assert len(results) > 0
        names = [r["name"] for r in results]
        assert "Ayushman Bharat" in names

    def test_search_top_k_limit(self, rag_engine):
        """Test that search respects top_k limit."""
        results = rag_engine.search_similar("scheme", top_k=1)
        assert len(results) <= 1

        results = rag_engine.search_similar("scheme", top_k=10)
        # Should not exceed available schemes
        assert len(results) <= len(rag_engine.schemes)

    def test_search_empty_schemes(self):
        """Test search when no schemes are loaded."""
        from app.services.rag_engine import RAGEngine
        engine = RAGEngine()
        engine.schemes = []
        results = engine.search_similar("farmer")
        assert results == []

    def test_search_case_insensitivity(self, rag_engine):
        """Test that search is case insensitive."""
        results_lower = rag_engine.search_similar("farmer")
        results_upper = rag_engine.search_similar("FARMER")
        results_mixed = rag_engine.search_similar("FaRmEr")

        assert len(results_lower) == len(results_upper) == len(results_mixed)

    def test_generate_answer_with_context(self, rag_engine):
        """Test answer generation with context."""
        context = "PM-KISAN provides Rs. 6,000 per year to farmers."
        question = "What is PM-KISAN?"
        answer = rag_engine.generate_answer(context, question)

        assert isinstance(answer, str)
        assert len(answer) > 0
        assert context in answer or "जानकारी" in answer

    def test_generate_answer_empty_context(self, rag_engine):
        """Test answer generation with empty context."""
        answer = rag_engine.generate_answer("", "What is PM-KISAN?")
        assert isinstance(answer, str)
        # Should indicate no information found
        assert "नहीं" in answer or "couldn't" in answer.lower() or "not" in answer.lower()

    def test_generate_answer_none_context(self, rag_engine):
        """Test answer generation with None context."""
        answer = rag_engine.generate_answer(None, "What is PM-KISAN?")
        # Should handle None gracefully
        assert isinstance(answer, str)

    def test_load_documents(self, rag_engine):
        """Test document loading."""
        with patch('app.services.scheme_loader.load_schemes') as mock_load:
            mock_load.return_value = [{"name": "Test", "description": "Test scheme"}]
            schemes = rag_engine.load_documents()
            assert isinstance(schemes, list)

    def test_build_vector_index(self, rag_engine):
        """Test vector index building (should not raise)."""
        rag_engine.build_vector_index()
        # Should complete without error in compatibility mode

    def test_create_embeddings(self, rag_engine):
        """Test embedding creation (mock mode)."""
        embeddings = rag_engine.create_embeddings(["test text"])
        assert isinstance(embeddings, list)


# ============================================================================
# Intent Detection Tests
# ============================================================================

class TestIntentDetection:
    """Test intent detection with various inputs."""

    def test_eligibility_english_keywords(self):
        """Test eligibility detection with English keywords."""
        from app.services.intent_detection import detect_intent

        queries = [
            "Who is eligible?",
            "What is the eligibility criteria?",
            "Can I apply for this scheme?",
            "Who can get this benefit?",
        ]
        for query in queries:
            assert detect_intent(query) == "eligibility_check"

    def test_eligibility_hindi_keywords(self):
        """Test eligibility detection with Hindi keywords."""
        from app.services.intent_detection import detect_intent

        queries = [
            "इस योजना की पात्रता क्या है?",
            "कौन आवेदन कर सकता है?",
        ]
        for query in queries:
            result = detect_intent(query)
            assert result == "eligibility_check"

    def test_eligibility_mixed_language(self):
        """Test eligibility detection with Hinglish."""
        from app.services.intent_detection import detect_intent

        result = detect_intent("Meri patrata kya hai?")
        assert result == "eligibility_check"

    def test_document_english_keywords(self):
        """Test document requirements detection."""
        from app.services.intent_detection import detect_intent

        queries = [
            "What documents are needed?",
            "Required papers for application",
            "What documents do I need?",
        ]
        for query in queries:
            assert detect_intent(query) == "document_requirements"

    def test_document_hindi_keywords(self):
        """Test document detection with Hindi keywords."""
        from app.services.intent_detection import detect_intent

        assert detect_intent("दस्तावेज़ क्या चाहिए?") == "document_requirements"
        assert detect_intent("कागज़ात की सूची") == "document_requirements"

    def test_benefits_english_keywords(self):
        """Test benefits query detection."""
        from app.services.intent_detection import detect_intent

        queries = [
            "What are the benefits?",
            "What will I get from this scheme?",
            "benefits of PM-KISAN",
        ]
        for query in queries:
            assert detect_intent(query) == "benefits_query"

    def test_benefits_hindi_keywords(self):
        """Test benefits detection with Hindi keywords."""
        from app.services.intent_detection import detect_intent

        queries = [
            "इस योजना के लाभ क्या हैं?",
            "क्या फायदे मिलेंगे?",
        ]
        for query in queries:
            assert detect_intent(query) == "benefits_query"

    def test_scheme_search_keywords(self):
        """Test scheme search detection."""
        from app.services.intent_detection import detect_intent

        queries = [
            "Tell me about PM-KISAN yojana",
            "Information about startup scheme",
            "What is Mudra loan plan?",
        ]
        for query in queries:
            assert detect_intent(query) == "scheme_search"

    def test_scheme_search_tamil_keywords(self):
        """Test scheme search with Tamil keywords."""
        from app.services.intent_detection import detect_intent

        result = detect_intent("விவசாயிகளுக்கான திட்டம்")
        assert result == "scheme_search"

    def test_general_information_fallback(self):
        """Test general information as fallback."""
        from app.services.intent_detection import detect_intent

        queries = [
            "Hello",
            "Good morning",
            "How are you?",
            "What can you do?",
        ]
        for query in queries:
            assert detect_intent(query) == "general_information"

    def test_empty_query(self):
        """Test intent detection with empty query."""
        from app.services.intent_detection import detect_intent

        result = detect_intent("")
        assert result == "general_information"

    def test_special_characters_only(self):
        """Test intent detection with special characters only."""
        from app.services.intent_detection import detect_intent

        result = detect_intent("!@#$%^&*()")
        assert result == "general_information"

    def test_case_insensitivity(self):
        """Test that intent detection is case insensitive."""
        from app.services.intent_detection import detect_intent

        assert detect_intent("ELIGIBILITY") == "eligibility_check"
        assert detect_intent("ELIGibility") == "eligibility_check"
        assert detect_intent("Documents NEEDED") == "document_requirements"

    def test_multiple_keywords_priority(self):
        """Test priority when multiple keywords are present."""
        from app.services.intent_detection import detect_intent

        # Document should take priority
        result = detect_intent("What documents needed for eligibility?")
        assert result == "document_requirements"


# ============================================================================
# Recommendation Engine Tests
# ============================================================================

class TestRecommendationEngine:
    """Test recommendation engine with all occupation types."""

    def test_farmer_occupation(self):
        """Test recommendations for farmer occupation."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"occupation": "farmer", "age": 35}
        results = recommend_schemes(user_data)

        assert isinstance(results, list)
        assert len(results) > 0
        names = [r["name"] for r in results]
        assert "PM-KISAN" in names

    def test_kisan_occupation_alias(self):
        """Test recommendations for 'kisan' (farmer in Hindi)."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"occupation": "kisan", "age": 30}
        results = recommend_schemes(user_data)

        names = [r["name"] for r in results]
        assert "PM-KISAN" in names

    def test_student_occupation(self):
        """Test recommendations for student occupation."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"occupation": "student", "age": 20}
        results = recommend_schemes(user_data)

        assert len(results) > 0
        names = [r["name"] for r in results]
        assert "Digital India" in names

    def test_startup_occupation(self):
        """Test recommendations for startup occupation."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"occupation": "startup", "age": 28}
        results = recommend_schemes(user_data)

        names = [r["name"] for r in results]
        assert "Startup India" in names or "Mudra Loan" in names

    def test_business_occupation(self):
        """Test recommendations for business occupation."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"occupation": "business", "age": 40}
        results = recommend_schemes(user_data)

        names = [r["name"] for r in results]
        assert "Startup India" in names or "Mudra Loan" in names

    def test_entrepreneur_occupation(self):
        """Test recommendations for entrepreneur occupation."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"occupation": "entrepreneur", "age": 32}
        results = recommend_schemes(user_data)

        names = [r["name"] for r in results]
        assert any(n in names for n in ["Startup India", "Mudra Loan"])

    def test_low_income_recommendations(self):
        """Test recommendations for low income families."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"income": 100000, "age": 40}
        results = recommend_schemes(user_data)

        names = [r["name"] for r in results]
        assert "Ayushman Bharat" in names
        assert "PM Awas Yojana" in names

    def test_young_age_recommendations(self):
        """Test recommendations for young people."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"age": 25, "occupation": "unemployed"}
        results = recommend_schemes(user_data)

        names = [r["name"] for r in results]
        assert "PM Kaushal Vikas Yojana" in names

    def test_age_above_35(self):
        """Test recommendations for age above 35."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"age": 45, "occupation": "teacher"}
        results = recommend_schemes(user_data)

        # Should not include skill development for youth
        names = [r["name"] for r in results]
        # Default recommendation when no specific match
        assert len(results) > 0

    def test_empty_user_data(self):
        """Test recommendations with empty user data."""
        from app.services.recommendation_engine import recommend_schemes

        results = recommend_schemes({})

        assert isinstance(results, list)
        assert len(results) > 0
        # Should return default recommendation
        names = [r["name"] for r in results]
        assert "Ayushman Bharat" in names

    def test_none_values(self):
        """Test recommendations with None values."""
        from app.services.recommendation_engine import recommend_schemes

        user_data = {"occupation": None, "age": None, "income": None}
        results = recommend_schemes(user_data)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_max_three_recommendations(self):
        """Test that maximum 3 recommendations are returned."""
        from app.services.recommendation_engine import recommend_schemes

        # User data that matches many criteria
        user_data = {
            "occupation": "farmer",
            "age": 25,
            "income": 100000
        }
        results = recommend_schemes(user_data)

        assert len(results) <= 3

    def test_recommendation_structure(self):
        """Test that recommendations have correct structure."""
        from app.services.recommendation_engine import recommend_schemes

        results = recommend_schemes({"occupation": "farmer"})

        for rec in results:
            assert "name" in rec
            assert "description" in rec
            assert isinstance(rec["name"], str)
            assert isinstance(rec["description"], str)

    def test_case_insensitive_occupation(self):
        """Test that occupation matching is case insensitive."""
        from app.services.recommendation_engine import recommend_schemes

        results_lower = recommend_schemes({"occupation": "farmer"})
        results_upper = recommend_schemes({"occupation": "FARMER"})
        results_mixed = recommend_schemes({"occupation": "FaRmEr"})

        # All should find PM-KISAN
        for results in [results_lower, results_upper, results_mixed]:
            names = [r["name"] for r in results]
            assert "PM-KISAN" in names


# ============================================================================
# Translation Service Tests
# ============================================================================

class TestTranslatorService:
    """Test translator service error handling."""

    def test_detect_language_hindi(self):
        """Test language detection for Hindi text."""
        from app.services.translator import translator_service

        lang = translator_service.detect_language("नमस्ते, आप कैसे हैं?")
        assert lang == "hi"

    def test_detect_language_english(self):
        """Test language detection for English text."""
        from app.services.translator import translator_service

        lang = translator_service.detect_language("Hello, how are you?")
        assert lang == "en"

    def test_detect_language_empty_string(self):
        """Test language detection for empty string."""
        from app.services.translator import translator_service

        lang = translator_service.detect_language("")
        # Should return fallback
        assert lang == "en"

    def test_detect_language_single_word(self):
        """Test language detection for single word."""
        from app.services.translator import translator_service

        # Single word might be ambiguous
        lang = translator_service.detect_language("hello")
        assert lang in ["en", "hi"]  # Could detect either

    def test_translate_same_language(self):
        """Test that translation with same source and target returns original."""
        from app.services.translator import translator_service

        text = "Hello world"
        result = translator_service.translate_text(text, source="en", target="en")
        assert result == text

    def test_translate_empty_text(self):
        """Test translation of empty text."""
        from app.services.translator import translator_service

        result = translator_service.translate_text("", source="en", target="hi")
        assert result == ""

    def test_translate_error_handling(self):
        """Test translation error handling."""
        from app.services.translator import translator_service

        with patch('app.services.translator.GoogleTranslator') as mock:
            mock.return_value.translate.side_effect = Exception("API error")

            # Should return original text on error
            result = translator_service.translate_text("Hello", source="en", target="hi")
            assert result == "Hello"

    def test_translate_api_success(self):
        """Test successful translation."""
        from app.services.translator import translator_service

        with patch('app.services.translator.GoogleTranslator') as mock:
            mock.return_value.translate.return_value = "नमस्ते"

            result = translator_service.translate_text("Hello", source="en", target="hi")
            assert result == "नमस्ते"


# ============================================================================
# Scheme Loader Tests
# ============================================================================

class TestSchemeLoader:
    """Test scheme loader with various data scenarios."""

    def test_load_schemes_file_not_exists(self, tmp_path):
        """Test loading when file doesn't exist."""
        with patch('app.services.scheme_loader.settings') as mock_settings:
            mock_settings.data_path = str(tmp_path / "nonexistent.json")

            from app.services.scheme_loader import load_schemes
            result = load_schemes()
            assert result == []

    def test_load_schemes_empty_file(self, tmp_path):
        """Test loading empty JSON file."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("{}")

        with patch('app.services.scheme_loader.settings') as mock_settings:
            mock_settings.data_path = str(empty_file)

            from app.services.scheme_loader import load_schemes
            result = load_schemes()
            assert result == []

    def test_load_schemes_valid_data(self, tmp_path):
        """Test loading valid schemes data."""
        schemes_data = {
            "schemes": [
                {"name": "Test Scheme", "description": "A test scheme"}
            ]
        }
        valid_file = tmp_path / "schemes.json"
        valid_file.write_text(json.dumps(schemes_data))

        with patch('app.services.scheme_loader.settings') as mock_settings:
            mock_settings.data_path = str(valid_file)

            from app.services.scheme_loader import load_schemes
            result = load_schemes()
            assert len(result) == 1
            assert result[0]["name"] == "Test Scheme"

    def test_load_schemes_malformed_json(self, tmp_path):
        """Test loading malformed JSON file."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{ invalid json }")

        with patch('app.services.scheme_loader.settings') as mock_settings:
            mock_settings.data_path = str(malformed_file)

            from app.services.scheme_loader import load_schemes
            # Should raise or handle gracefully
            with pytest.raises(json.JSONDecodeError):
                load_schemes()

    def test_load_schemes_missing_schemes_key(self, tmp_path):
        """Test loading JSON without 'schemes' key."""
        data = {"data": [{"name": "Test"}]}
        file_path = tmp_path / "no_schemes.json"
        file_path.write_text(json.dumps(data))

        with patch('app.services.scheme_loader.settings') as mock_settings:
            mock_settings.data_path = str(file_path)

            from app.services.scheme_loader import load_schemes
            result = load_schemes()
            # Should return empty list or None for missing key
            assert result == [] or result is None

    def test_load_schemes_unicode_content(self, tmp_path):
        """Test loading schemes with unicode content."""
        schemes_data = {
            "schemes": [
                {
                    "name": "प्रधानमंत्री किसान",
                    "description": "किसानों के लिए योजना"
                }
            ]
        }
        unicode_file = tmp_path / "unicode.json"
        unicode_file.write_text(json.dumps(schemes_data, ensure_ascii=False), encoding="utf-8")

        with patch('app.services.scheme_loader.settings') as mock_settings:
            mock_settings.data_path = str(unicode_file)

            from app.services.scheme_loader import load_schemes
            result = load_schemes()
            assert len(result) == 1
            assert "किसान" in result[0]["name"]

    def test_load_schemes_large_file(self, tmp_path):
        """Test loading large schemes file."""
        schemes_data = {
            "schemes": [
                {"name": f"Scheme {i}", "description": f"Description {i}"}
                for i in range(1000)
            ]
        }
        large_file = tmp_path / "large.json"
        large_file.write_text(json.dumps(schemes_data))

        with patch('app.services.scheme_loader.settings') as mock_settings:
            mock_settings.data_path = str(large_file)

            from app.services.scheme_loader import load_schemes
            result = load_schemes()
            assert len(result) == 1000


# ============================================================================
# Speech Service Tests
# ============================================================================

class TestSpeechService:
    """Test speech service functionality."""

    @pytest.fixture
    def speech_service(self):
        """Get fresh speech service instance."""
        from app.services.speech_service import SpeechService
        return SpeechService()

    def test_normalize_language_short_codes(self, speech_service):
        """Test language normalization for short codes."""
        assert speech_service._normalize_language("hi") == "hi-IN"
        assert speech_service._normalize_language("en") == "en-IN"
        assert speech_service._normalize_language("ta") == "ta-IN"
        assert speech_service._normalize_language("te") == "te-IN"

    def test_normalize_language_full_names(self, speech_service):
        """Test language normalization for full names."""
        assert speech_service._normalize_language("hindi") == "hi-IN"
        assert speech_service._normalize_language("english") == "en-IN"
        assert speech_service._normalize_language("tamil") == "ta-IN"
        assert speech_service._normalize_language("telugu") == "te-IN"

    def test_normalize_language_full_codes(self, speech_service):
        """Test language normalization for full locale codes."""
        assert speech_service._normalize_language("hi-IN") == "hi-IN"
        assert speech_service._normalize_language("en-IN") == "en-IN"

    def test_normalize_language_case_insensitive(self, speech_service):
        """Test that normalization is case insensitive."""
        assert speech_service._normalize_language("HI") == "hi-IN"
        assert speech_service._normalize_language("HINDI") == "hi-IN"

    def test_get_voice_name_female(self, speech_service):
        """Test getting female voice names."""
        assert "Swara" in speech_service._get_voice_name("hi-IN", "female")
        assert "Neerja" in speech_service._get_voice_name("en-IN", "female")

    def test_get_voice_name_male(self, speech_service):
        """Test getting male voice names."""
        assert "Madhur" in speech_service._get_voice_name("hi-IN", "male")
        assert "Prabhat" in speech_service._get_voice_name("en-IN", "male")

    def test_escape_ssml(self, speech_service):
        """Test SSML escaping."""
        text = "Hello & goodbye <test> \"quotes\" 'apostrophe'"
        escaped = speech_service._escape_ssml(text)

        assert "&amp;" in escaped
        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&quot;" in escaped
        assert "&apos;" in escaped

    def test_get_supported_languages(self, speech_service):
        """Test getting supported languages."""
        languages = speech_service.get_supported_languages()

        assert "hi-IN" in languages
        assert "en-IN" in languages
        assert "ta-IN" in languages
        assert "te-IN" in languages

        # Each language should have voice info
        for lang_code, info in languages.items():
            assert "name" in info
            assert "voices" in info
            assert "female" in info["voices"]
            assert "male" in info["voices"]

    def test_get_status_unconfigured(self, speech_service):
        """Test status when Azure is not configured."""
        with patch('app.services.speech_service.settings') as mock_settings:
            mock_settings.azure_speech_configured.return_value = False
            mock_settings.azure_speech_region = None

            status = speech_service.get_status()
            assert status["provider"] == "browser"
            assert status["configured"] is False

    def test_provider_property(self, speech_service):
        """Test provider property."""
        with patch('app.services.speech_service.settings') as mock_settings:
            mock_settings.azure_speech_configured.return_value = True
            assert speech_service.provider == "azure"

            mock_settings.azure_speech_configured.return_value = False
            assert speech_service.provider == "browser"


# ============================================================================
# Web Search Service Tests (if available)
# ============================================================================

class TestWebSearchService:
    """Test web search service functionality."""

    @pytest.mark.asyncio
    async def test_fetch_serp_snippets_offline_mode(self):
        """Test SERP fetch in offline mode."""
        with patch('app.services.web_search.settings') as mock_settings:
            mock_settings.offline_only = True

            from app.services.web_search import fetch_serp_snippets
            result = await fetch_serp_snippets("test query")
            assert result == ""

    @pytest.mark.asyncio
    async def test_fetch_document_links_offline_mode(self):
        """Test document links fetch in offline mode."""
        with patch('app.services.web_search.settings') as mock_settings:
            mock_settings.offline_only = True

            from app.services.web_search import fetch_document_links
            result = await fetch_document_links("PM-KISAN", "Aadhaar")
            assert result == []


# ============================================================================
# LLM Answer Service Tests (if available)
# ============================================================================

class TestLLMAnswerService:
    """Test LLM answer service functionality."""

    @pytest.mark.asyncio
    async def test_generate_answer_not_configured(self):
        """Test answer generation when Azure is not configured."""
        with patch('app.services.llm_answer.settings') as mock_settings:
            mock_settings.azure_openai_configured.return_value = False

            from app.services.llm_answer import generate_answer_with_azure
            result = await generate_answer_with_azure(
                english_query="test",
                intent="scheme_search",
                local_context="",
                web_context=""
            )
            assert result is None
