"""
Pytest configuration and shared fixtures for Saarthi-AI backend tests.

This file contains fixtures that are shared across all test modules.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock


# ============================================================================
# Async Event Loop Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Settings Fixtures
# ============================================================================

@pytest.fixture
def mock_settings():
    """Mock settings for offline testing."""
    with patch('app.config.settings') as mock:
        mock.offline_only = True
        mock.data_path = "app/data/schemes.json"
        mock.azure_openai_configured.return_value = False
        mock.brightdata_serp_configured.return_value = False
        mock.azure_speech_configured.return_value = False
        yield mock


@pytest.fixture
def mock_online_settings():
    """Mock settings for online testing with mocked services."""
    with patch('app.config.settings') as mock:
        mock.offline_only = False
        mock.data_path = "app/data/schemes.json"
        mock.azure_openai_configured.return_value = True
        mock.brightdata_serp_configured.return_value = True
        mock.azure_speech_configured.return_value = True
        mock.azure_openai_endpoint = "https://test.openai.azure.com"
        mock.azure_openai_api_key = "test-key"
        mock.azure_openai_deployment = "test-deployment"
        mock.azure_openai_api_version = "2024-02-15-preview"
        mock.brightdata_api_token = "test-token"
        mock.brightdata_serp_zone = "test-zone"
        mock.azure_speech_key = "test-key"
        mock.azure_speech_region = "eastus"
        yield mock


# ============================================================================
# RAG Engine Fixtures
# ============================================================================

@pytest.fixture
def mock_rag_engine_with_data():
    """RAG engine fixture with test data."""
    from app.services.rag_engine import RAGEngine
    engine = RAGEngine()
    engine.schemes = [
        {
            "name": "PM-KISAN",
            "description": "Farmer support scheme providing income support to landholding farmers",
            "eligibility": "All landholding farmers' families",
            "benefits": "Rs. 6,000 per year in three installments"
        },
        {
            "name": "Ayushman Bharat - PMJAY",
            "description": "Health insurance scheme for poor families providing health coverage",
            "eligibility": "BPL families as per SECC 2011 data",
            "benefits": "Rs. 5 lakh health insurance cover per family"
        },
        {
            "name": "Digital India",
            "description": "Digital empowerment initiatives for students and youth",
            "eligibility": "Indian students and youth",
            "benefits": "Digital training and scholarships"
        },
        {
            "name": "Startup India",
            "description": "Support for entrepreneurs and startups with tax benefits",
            "eligibility": "Registered startups less than 10 years old",
            "benefits": "Tax exemptions and funding access"
        },
        {
            "name": "Mudra Loan",
            "description": "Loans for small businesses and micro enterprises",
            "eligibility": "Non-corporate small businesses",
            "benefits": "Collateral-free loans up to Rs. 10 lakh"
        }
    ]
    return engine


# ============================================================================
# HTTP Client Fixtures
# ============================================================================

@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient for testing HTTP calls."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        yield mock_client


# ============================================================================
# Translation Service Fixtures
# ============================================================================

@pytest.fixture
def mock_translator():
    """Mock translator service to avoid actual API calls."""
    with patch('app.services.translator.translator_service') as mock:
        mock.detect_language.return_value = "en"
        mock.translate_text.side_effect = lambda text, source, target: text
        yield mock


# ============================================================================
# Web Search Fixtures
# ============================================================================

@pytest.fixture
def mock_web_search():
    """Mock web search services to avoid external calls."""
    with patch('app.api.query.fetch_serp_snippets', new_callable=AsyncMock) as mock_serp, \
         patch('app.api.query.fetch_document_links', new_callable=AsyncMock) as mock_docs:
        mock_serp.return_value = ""
        mock_docs.return_value = []
        yield mock_serp, mock_docs


# ============================================================================
# LLM Answer Fixtures
# ============================================================================

@pytest.fixture
def mock_azure_llm():
    """Mock Azure OpenAI LLM calls."""
    with patch('app.api.query.generate_answer_with_azure', new_callable=AsyncMock) as mock:
        mock.return_value = None  # Fall back to local answer generation
        yield mock


# ============================================================================
# Speech Service Fixtures
# ============================================================================

@pytest.fixture
def mock_speech_service_not_configured():
    """Mock speech service when Azure is not configured."""
    from app.services.speech_service import SpeechServiceError

    with patch('app.api.speech.speech_service') as mock:
        mock.text_to_speech = AsyncMock(
            side_effect=SpeechServiceError("Azure Speech not configured")
        )
        mock.speech_to_text = AsyncMock(
            side_effect=SpeechServiceError("Azure Speech not configured")
        )
        mock.get_status.return_value = {
            "provider": "browser",
            "configured": False,
            "supported_languages": ["hi-IN", "en-IN", "ta-IN", "te-IN"],
            "azure_region": None
        }
        mock.get_supported_languages.return_value = {
            "hi-IN": {"name": "Hindi", "voices": {"female": "hi-IN-SwaraNeural", "male": "hi-IN-MadhurNeural"}},
            "en-IN": {"name": "English", "voices": {"female": "en-IN-NeerjaNeural", "male": "en-IN-PrabhatNeural"}}
        }
        yield mock


@pytest.fixture
def mock_speech_service_configured():
    """Mock speech service when Azure is configured."""
    with patch('app.api.speech.speech_service') as mock:
        mock.text_to_speech = AsyncMock(return_value=b"fake audio data")
        mock.speech_to_text = AsyncMock(return_value="Transcribed text")
        mock.get_status.return_value = {
            "provider": "azure",
            "configured": True,
            "supported_languages": ["hi-IN", "en-IN", "ta-IN", "te-IN"],
            "azure_region": "eastus"
        }
        mock.get_supported_languages.return_value = {
            "hi-IN": {"name": "Hindi", "voices": {"female": "hi-IN-SwaraNeural", "male": "hi-IN-MadhurNeural"}},
            "en-IN": {"name": "English", "voices": {"female": "en-IN-NeerjaNeural", "male": "en-IN-PrabhatNeural"}},
            "ta-IN": {"name": "Tamil", "voices": {"female": "ta-IN-PallaviNeural", "male": "ta-IN-ValluvarNeural"}},
            "te-IN": {"name": "Telugu", "voices": {"female": "te-IN-ShrutiNeural", "male": "te-IN-MohanNeural"}}
        }
        yield mock


# ============================================================================
# Help Center Locator Fixtures
# ============================================================================

@pytest.fixture
def mock_help_center_locator():
    """Mock help center locator for testing."""
    from app.services.help_center_locator import HelpCenter

    with patch('app.services.help_center_locator.help_center_locator') as mock:
        mock.find_nearby_centers = AsyncMock(return_value=[
            HelpCenter(
                name="Test CSC Center",
                address="Test Address, Delhi",
                lat=28.6315,
                lng=77.2167,
                distance_km=1.5,
                phone="+91-11-12345678",
                source="brightdata"
            )
        ])
        mock.get_center_details = AsyncMock(return_value=None)
        yield mock


# ============================================================================
# Connection Manager Fixtures
# ============================================================================

@pytest.fixture
def mock_connection_manager_online():
    """Mock connection manager in online mode."""
    with patch('app.services.connection_manager.connection_manager') as mock:
        mock.mode = MagicMock()
        mock.mode.value = "online"
        mock.is_online = True
        mock.get_state.return_value = {
            "mode": "online",
            "forced_offline": False,
            "services": {},
            "auto_recovery_enabled": True
        }
        mock.run_health_checks = AsyncMock(return_value={
            "mode": "online",
            "forced_offline": False,
            "services": {},
            "auto_recovery_enabled": True
        })
        yield mock


@pytest.fixture
def mock_connection_manager_offline():
    """Mock connection manager in offline mode."""
    with patch('app.services.connection_manager.connection_manager') as mock:
        mock.mode = MagicMock()
        mock.mode.value = "offline"
        mock.is_online = False
        mock.get_state.return_value = {
            "mode": "offline",
            "forced_offline": True,
            "services": {},
            "auto_recovery_enabled": False
        }
        yield mock


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_query_request():
    """Sample query request payload."""
    return {
        "query": "Tell me about farmer schemes",
        "language": "en",
        "location": "Delhi",
        "occupation": "farmer",
        "age": 35,
        "income": 100000
    }


@pytest.fixture
def sample_help_centers_request():
    """Sample help centers nearby request."""
    return {
        "lat": 28.6139,
        "lng": 77.2090,
        "radius_meters": 5000,
        "limit": 10
    }


@pytest.fixture
def sample_tts_request():
    """Sample TTS request payload."""
    return {
        "text": "Hello, how can I help you today?",
        "language": "en-IN",
        "gender": "female",
        "return_base64": True
    }


@pytest.fixture
def sample_stt_request():
    """Sample STT request payload."""
    import base64
    return {
        "audio_base64": base64.b64encode(b"fake audio data").decode(),
        "language": "hi-IN",
        "audio_format": "audio/wav"
    }


# ============================================================================
# Test Client Fixture
# ============================================================================

@pytest.fixture
def test_client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Cleanup code can be added here if needed
