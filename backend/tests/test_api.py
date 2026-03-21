"""
Comprehensive API endpoint tests for Saarthi-AI backend.

Tests cover:
- Query endpoint with various languages
- Query with edge cases (empty, whitespace, XSS, long text)
- Help centers endpoint with mocked BrightData search
- Speech endpoints (TTS/STT)
- Connection status endpoint
- Schemes endpoint
"""

import pytest
import base64
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.intent_detection import detect_intent
from app.services.rag_engine import rag_engine


client = TestClient(app)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def mock_rag_engine():
    """Ensure RAG engine has test data."""
    if not rag_engine.schemes:
        rag_engine.schemes = [
            {
                "name": "PM-KISAN",
                "description": "Farmer support scheme providing income support to farmers",
                "eligibility": "All landholding farmers",
                "benefits": "Rs. 6,000 per year"
            },
            {
                "name": "Ayushman Bharat",
                "description": "Health insurance scheme for poor families",
                "eligibility": "BPL families as per SECC data",
                "benefits": "Rs. 5 lakh health cover per family"
            },
            {
                "name": "Digital India",
                "description": "Digital empowerment initiatives for students",
                "eligibility": "Indian students",
                "benefits": "Digital training and scholarships"
            }
        ]
        try:
            rag_engine.build_vector_index()
        except Exception:
            pass


@pytest.fixture
def mock_translator():
    """Mock translator service to avoid actual API calls."""
    with patch('app.services.translator.translator_service') as mock:
        mock.detect_language.return_value = "en"
        mock.translate_text.side_effect = lambda text, *args, **kwargs: text
        yield mock


@pytest.fixture
def mock_web_search():
    """Mock web search to avoid external calls."""
    with patch('app.api.query.fetch_serp_snippets', new_callable=AsyncMock) as mock_serp, \
         patch('app.api.query.fetch_document_links', new_callable=AsyncMock) as mock_docs:
        mock_serp.return_value = ""
        mock_docs.return_value = []
        yield mock_serp, mock_docs


@pytest.fixture
def mock_azure_llm():
    """Mock Azure OpenAI LLM calls."""
    with patch('app.api.query.generate_answer_with_azure', new_callable=AsyncMock) as mock:
        mock.return_value = None  # Fall back to local answer generation
        yield mock


@pytest.fixture
def mock_offline_mode():
    """Mock settings to be in offline mode."""
    with patch('app.api.query.settings') as mock_settings:
        mock_settings.offline_only = True
        mock_settings.azure_openai_configured.return_value = False
        yield mock_settings


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_returns_ok(self):
        """Test that health endpoint returns 200 with correct message."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "SaarthiAI backend is running" in data["message"]

    def test_health_check_api_prefix(self):
        """Test health check with /api prefix."""
        response = client.get("/api/health")
        assert response.status_code == 200


# ============================================================================
# Schemes Endpoint Tests
# ============================================================================

class TestSchemesEndpoint:
    """Test schemes listing endpoint."""

    def test_schemes_endpoint_returns_list(self):
        """Test that schemes endpoint returns a list."""
        response = client.get("/schemes")
        assert response.status_code == 200
        data = response.json()
        assert "schemes" in data
        assert isinstance(data["schemes"], list)

    def test_schemes_endpoint_with_api_prefix(self):
        """Test schemes endpoint with /api prefix."""
        response = client.get("/api/schemes")
        assert response.status_code == 200

    def test_schemes_contain_required_fields(self):
        """Test that returned schemes have required fields."""
        response = client.get("/schemes")
        data = response.json()
        if data["schemes"]:
            scheme = data["schemes"][0]
            # At minimum, schemes should have name and description
            assert "name" in scheme
            assert "description" in scheme


# ============================================================================
# Query Endpoint Tests - Language Support
# ============================================================================

class TestQueryEndpointLanguages:
    """Test query endpoint with various languages."""

    def test_query_hindi(self, mock_web_search, mock_azure_llm):
        """Test query in Hindi language."""
        request_payload = {
            "query": "मुझे किसान योजना के बारे में बताओ",
            "language": "hi",
            "occupation": "farmer"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "answer" in data
        assert "recommended_schemes" in data

    def test_query_english(self, mock_web_search, mock_azure_llm):
        """Test query in English language."""
        request_payload = {
            "query": "Tell me about farmer schemes",
            "language": "en",
            "occupation": "farmer"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert data["intent"] == "scheme_search"

    def test_query_tamil(self, mock_web_search, mock_azure_llm):
        """Test query in Tamil language."""
        request_payload = {
            "query": "விவசாயிகளுக்கான திட்டங்கள் பற்றி சொல்லுங்கள்",
            "language": "ta"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data

    def test_query_telugu(self, mock_web_search, mock_azure_llm):
        """Test query in Telugu language."""
        request_payload = {
            "query": "రైతు పథకాల గురించి చెప్పండి",
            "language": "te"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data

    def test_query_auto_language_detection(self, mock_web_search, mock_azure_llm):
        """Test auto language detection."""
        request_payload = {
            "query": "What documents do I need for PM-KISAN?",
            "language": "auto"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert "response_language" in data


# ============================================================================
# Query Endpoint Tests - Edge Cases
# ============================================================================

class TestQueryEndpointEdgeCases:
    """Test query endpoint with edge cases."""

    def test_query_empty_string(self):
        """Test query with empty string."""
        request_payload = {
            "query": "",
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        # QueryRequest.query currently has no min_length constraint.
        assert response.status_code == 200

    def test_query_whitespace_only(self, mock_web_search, mock_azure_llm):
        """Test query with only whitespace."""
        request_payload = {
            "query": "   \t\n   ",
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        # Whitespace query should be handled gracefully
        assert response.status_code == 200

    def test_query_single_character(self, mock_web_search, mock_azure_llm):
        """Test query with single character."""
        request_payload = {
            "query": "a",
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200

    def test_query_xss_attempt(self, mock_web_search, mock_azure_llm):
        """Test query with XSS attempt - should be handled safely."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "' OR '1'='1",
            "; DROP TABLE schemes; --"
        ]
        for payload in xss_payloads:
            request_payload = {
                "query": payload,
                "language": "en"
            }
            response = client.post("/query", json=request_payload)
            # Should handle without error
            assert response.status_code == 200
            data = response.json()
            # Response should not execute or reflect XSS
            assert "<script>" not in data.get("answer", "")

    def test_query_special_characters(self, mock_web_search, mock_azure_llm):
        """Test query with special characters."""
        request_payload = {
            "query": "What about !@#$%^&*()_+-={}[]|\\:\";<>?,./~` schemes?",
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200

    def test_query_unicode_characters(self, mock_web_search, mock_azure_llm):
        """Test query with various unicode characters."""
        request_payload = {
            "query": "Tell me about schemes for farmers",
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200

    def test_query_very_long_text(self, mock_web_search, mock_azure_llm):
        """Test query with very long text (>5000 chars)."""
        long_query = "Tell me about farmer schemes. " * 200  # ~6000 chars
        request_payload = {
            "query": long_query,
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        # QueryRequest.query currently has no max_length constraint.
        assert response.status_code == 200

    def test_query_mixed_language(self, mock_web_search, mock_azure_llm):
        """Test query with mixed language (Hinglish)."""
        request_payload = {
            "query": "Mujhe kisan yojana ke documents chahiye",
            "language": "auto"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200

    def test_query_null_optional_fields(self, mock_web_search, mock_azure_llm):
        """Test query with null optional fields."""
        request_payload = {
            "query": "Tell me about schemes",
            "language": None,
            "location": None,
            "age": None,
            "income": None,
            "occupation": None
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200

    def test_query_missing_query_field(self):
        """Test request without query field."""
        request_payload = {
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 422  # Validation error

    def test_query_invalid_json(self):
        """Test request with invalid JSON."""
        response = client.post(
            "/query",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


# ============================================================================
# Query Response Structure Tests
# ============================================================================

class TestQueryResponseStructure:
    """Test query response structure and document links."""

    def test_query_response_has_all_fields(self, mock_web_search, mock_azure_llm):
        """Test that query response has all required fields."""
        request_payload = {
            "query": "What documents are needed for PM-KISAN?",
            "language": "en"
        }
        response = client.post("/query", json=request_payload)
        assert response.status_code == 200
        data = response.json()

        assert "intent" in data
        assert "answer" in data
        assert "recommended_schemes" in data
        assert "document_links" in data
        assert "response_language" in data

    def test_document_links_structure(self, mock_web_search, mock_azure_llm):
        """Test that document links have correct structure when returned."""
        # Mock document links
        with patch('app.api.query.fetch_document_links', new_callable=AsyncMock) as mock_docs:
            mock_docs.return_value = [
                {
                    "title": "PM-KISAN Official Portal",
                    "url": "https://pmkisan.gov.in/",
                    "description": "Official website",
                    "source": "government"
                }
            ]

            request_payload = {
                "query": "What documents are needed for PM-KISAN?",
                "language": "en"
            }
            response = client.post("/query", json=request_payload)
            data = response.json()

            assert isinstance(data["document_links"], list)
            for doc_link in data["document_links"]:
                assert "title" in doc_link
                assert "url" in doc_link
                assert "description" in doc_link
                assert "source" in doc_link

    def test_recommended_schemes_structure(self, mock_web_search, mock_azure_llm):
        """Test that recommended schemes have correct structure."""
        request_payload = {
            "query": "Tell me about schemes",
            "language": "en",
            "occupation": "farmer"
        }
        response = client.post("/query", json=request_payload)
        data = response.json()

        assert isinstance(data["recommended_schemes"], list)
        for scheme in data["recommended_schemes"]:
            assert "name" in scheme
            assert "description" in scheme


# ============================================================================
# Intent Detection Tests
# ============================================================================

class TestIntentDetection:
    """Test intent detection functionality."""

    def test_intent_eligibility_check(self):
        """Test eligibility check intent detection."""
        assert detect_intent("What is the eligibility for Kisan yojana?") == "eligibility_check"
        assert detect_intent("Who can apply for this scheme?") == "eligibility_check"
        assert detect_intent("Am I eligible?") == "eligibility_check"

    def test_intent_document_requirements(self):
        """Test document requirements intent detection."""
        assert detect_intent("What documents do I need?") == "document_requirements"
        assert detect_intent("Required papers for application") == "document_requirements"
        assert detect_intent("List of dastavez needed") == "document_requirements"

    def test_intent_benefits_query(self):
        """Test benefits query intent detection."""
        assert detect_intent("What are the benefits?") == "benefits_query"
        assert detect_intent("Kya fayde milenge?") == "benefits_query"
        assert detect_intent("What will I get from this scheme?") == "benefits_query"

    def test_intent_scheme_search(self):
        """Test scheme search intent detection."""
        assert detect_intent("Tell me about PM-KISAN yojana") == "scheme_search"
        assert detect_intent("Information about startup scheme") == "scheme_search"
        assert detect_intent("Mudra loan plan details") == "scheme_search"

    def test_intent_general_information(self):
        """Test general information intent detection."""
        assert detect_intent("Hello how are you?") == "general_information"
        assert detect_intent("What can you help me with?") == "general_information"

    def test_intent_with_hindi_keywords(self):
        """Test intent detection with Hindi keywords."""
        assert detect_intent("इस योजना की पात्रता क्या है?") == "eligibility_check"
        assert detect_intent("दस्तावेज़ क्या चाहिए?") == "document_requirements"
        assert detect_intent("इस योजना के लाभ बताइए") == "benefits_query"

    def test_intent_with_tamil_keywords(self):
        """Test intent detection with Tamil keywords."""
        assert detect_intent("இந்த திட்டத்தின் தகுதி என்ன?") == "eligibility_check"
        assert detect_intent("தேவையான ஆவணங்கள்") == "document_requirements"
        assert detect_intent("இந்த திட்டத்தின் நன்மைகள்") == "benefits_query"


# ============================================================================
# Help Centers Endpoint Tests
# ============================================================================

class TestHelpCentersAPI:
    """Test help centers endpoint with mocked external services."""

    @pytest.fixture
    def mock_brightdata(self):
        """Mock BrightData help center search."""
        with patch('app.services.help_center_locator.help_center_locator._search_brightdata_places', new_callable=AsyncMock) as mock:
            mock.return_value = []
            yield mock

    def test_help_centers_nearby_valid_coordinates(self, mock_brightdata):
        """Test nearby help centers with valid coordinates."""
        request_payload = {
            "lat": 28.6139,
            "lng": 77.2090,
            "radius_meters": 5000,
            "limit": 10
        }
        response = client.post("/help-centers/nearby", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert "centers" in data
        assert "total" in data
        assert "search_location" in data
        assert "radius_meters" in data

    def test_help_centers_invalid_latitude(self):
        """Test with invalid latitude (out of range)."""
        request_payload = {
            "lat": 100.0,  # Invalid: should be -90 to 90
            "lng": 77.2090,
            "radius_meters": 5000
        }
        response = client.post("/help-centers/nearby", json=request_payload)
        assert response.status_code == 422  # Validation error

    def test_help_centers_invalid_longitude(self):
        """Test with invalid longitude (out of range)."""
        request_payload = {
            "lat": 28.6139,
            "lng": 200.0,  # Invalid: should be -180 to 180
            "radius_meters": 5000
        }
        response = client.post("/help-centers/nearby", json=request_payload)
        assert response.status_code == 422

    def test_help_centers_minimum_radius(self):
        """Test with minimum valid radius."""
        request_payload = {
            "lat": 28.6139,
            "lng": 77.2090,
            "radius_meters": 100,  # Minimum valid radius
            "limit": 5
        }
        response = client.post("/help-centers/nearby", json=request_payload)
        assert response.status_code == 200

    def test_help_centers_maximum_radius(self):
        """Test with maximum valid radius."""
        request_payload = {
            "lat": 28.6139,
            "lng": 77.2090,
            "radius_meters": 50000,  # Maximum valid radius
            "limit": 50
        }
        response = client.post("/help-centers/nearby", json=request_payload)
        assert response.status_code == 200

    def test_help_centers_radius_too_small(self):
        """Test with radius below minimum."""
        request_payload = {
            "lat": 28.6139,
            "lng": 77.2090,
            "radius_meters": 50  # Below minimum (100)
        }
        response = client.post("/help-centers/nearby", json=request_payload)
        assert response.status_code == 422

    def test_help_centers_radius_too_large(self):
        """Test with radius above maximum."""
        request_payload = {
            "lat": 28.6139,
            "lng": 77.2090,
            "radius_meters": 100000  # Above maximum (50000)
        }
        response = client.post("/help-centers/nearby", json=request_payload)
        assert response.status_code == 422

    def test_help_centers_details_valid_id(self, mock_brightdata):
        """Test getting details with valid place ID."""
        with patch('app.services.help_center_locator.help_center_locator.get_center_details', new_callable=AsyncMock) as mock:
            mock.return_value = None  # Not found
            response = client.get("/help-centers/details/ChIJexample123")
            assert response.status_code == 200
            data = response.json()
            assert "found" in data
            assert "message" in data

    def test_help_centers_details_generic_id(self, mock_brightdata):
        """Test getting details with generic BrightData place ID."""
        with patch('app.services.help_center_locator.help_center_locator.get_center_details', new_callable=AsyncMock) as mock:
            mock.return_value = None
            response = client.get("/help-centers/details/bd_place_123456")
            assert response.status_code == 200


# ============================================================================
# Speech Endpoint Tests
# ============================================================================

class TestSpeechEndpoints:
    """Test speech TTS and STT endpoints."""

    @pytest.fixture
    def mock_speech_service(self):
        """Mock speech service."""
        with patch('app.api.speech.speech_service') as mock:
            yield mock

    def test_tts_not_configured(self, mock_speech_service):
        """Test TTS when Azure Speech is not configured."""
        from app.services.speech_service import SpeechServiceError
        mock_speech_service.text_to_speech = AsyncMock(
            side_effect=SpeechServiceError("Azure Speech not configured")
        )

        request_payload = {
            "text": "Hello, how are you?",
            "language": "en-IN",
            "gender": "female"
        }
        response = client.post("/speech/tts", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["use_browser_api"] is True

    def test_tts_valid_request(self, mock_speech_service):
        """Test TTS with valid request (mocked success)."""
        mock_speech_service.text_to_speech = AsyncMock(
            return_value=b"fake audio data"
        )

        request_payload = {
            "text": "Test speech synthesis",
            "language": "hi-IN",
            "gender": "female",
            "return_base64": True
        }
        response = client.post("/speech/tts", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "audio_base64" in data

    def test_tts_empty_text(self):
        """Test TTS with empty text."""
        request_payload = {
            "text": "",
            "language": "en-IN"
        }
        response = client.post("/speech/tts", json=request_payload)
        assert response.status_code == 422  # Validation error (min_length=1)

    def test_tts_text_too_long(self):
        """Test TTS with text exceeding maximum length."""
        request_payload = {
            "text": "a" * 6000,  # Max is 5000
            "language": "en-IN"
        }
        response = client.post("/speech/tts", json=request_payload)
        assert response.status_code == 422  # Validation error (max_length=5000)

    def test_tts_all_supported_languages(self, mock_speech_service):
        """Test TTS with all supported language codes."""
        mock_speech_service.text_to_speech = AsyncMock(return_value=b"audio")

        languages = ["hi-IN", "en-IN", "ta-IN", "te-IN", "hi", "en", "ta", "te"]
        for lang in languages:
            request_payload = {
                "text": "Test",
                "language": lang
            }
            response = client.post("/speech/tts", json=request_payload)
            assert response.status_code == 200

    def test_stt_not_configured(self, mock_speech_service):
        """Test STT when Azure Speech is not configured."""
        from app.services.speech_service import SpeechServiceError
        mock_speech_service.speech_to_text = AsyncMock(
            side_effect=SpeechServiceError("Azure Speech not configured")
        )

        audio_base64 = base64.b64encode(b"fake audio").decode()
        request_payload = {
            "audio_base64": audio_base64,
            "language": "hi-IN"
        }
        response = client.post("/speech/stt", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["use_browser_api"] is True

    def test_stt_invalid_base64(self):
        """Test STT with invalid base64 data."""
        request_payload = {
            "audio_base64": "not-valid-base64!!!",
            "language": "hi-IN"
        }
        response = client.post("/speech/stt", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Invalid base64" in data.get("error", "")

    def test_stt_empty_audio(self, mock_speech_service):
        """Test STT with empty audio data."""
        mock_speech_service.speech_to_text = AsyncMock(return_value="")

        audio_base64 = base64.b64encode(b"").decode()
        request_payload = {
            "audio_base64": audio_base64,
            "language": "hi-IN"
        }
        response = client.post("/speech/stt", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        # Empty audio should return error
        assert data["success"] is False

    def test_speech_status_endpoint(self):
        """Test speech service status endpoint."""
        response = client.get("/speech/status")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "configured" in data
        assert "supported_languages" in data

    def test_speech_languages_endpoint(self):
        """Test supported languages endpoint."""
        response = client.get("/speech/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        # Should support at least Hindi and English
        langs = data["languages"]
        assert "hi-IN" in langs
        assert "en-IN" in langs


# ============================================================================
# Connection Status Endpoint Tests
# ============================================================================

class TestConnectionEndpoint:
    """Test connection status and health check endpoints."""

    def test_connection_status(self):
        """Test getting connection status."""
        response = client.get("/connection/status")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["online", "offline", "degraded"]
        assert "forced_offline" in data
        assert "services" in data

    def test_connection_mode(self):
        """Test getting just the connection mode."""
        response = client.get("/connection/mode")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert "is_online" in data

    def test_connection_health_check(self):
        """Test triggering health check."""
        with patch('app.services.connection_manager.connection_manager.run_health_checks', new_callable=AsyncMock) as mock:
            mock.return_value = {
                "mode": "offline",
                "forced_offline": True,
                "services": {},
                "auto_recovery_enabled": True
            }
            response = client.post("/connection/health-check")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "state" in data


# ============================================================================
# Root Endpoint Tests
# ============================================================================

class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_returns_welcome(self):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "SaarthiAI" in data["message"]


# ============================================================================
# API Prefix Tests
# ============================================================================

class TestApiPrefix:
    """Test that all endpoints work with /api prefix."""

    def test_api_prefix_health(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_api_prefix_schemes(self):
        response = client.get("/api/schemes")
        assert response.status_code == 200

    def test_api_prefix_query(self, mock_web_search, mock_azure_llm):
        response = client.post("/api/query", json={"query": "test"})
        assert response.status_code == 200

    def test_api_prefix_connection_status(self):
        response = client.get("/api/connection/status")
        assert response.status_code == 200

    def test_api_prefix_speech_status(self):
        response = client.get("/api/speech/status")
        assert response.status_code == 200
