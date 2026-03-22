import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.rag_engine import rag_engine

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def _ensure_rag_loaded():
    if not rag_engine.schemes:
        rag_engine.load_documents()
        try:
            rag_engine.build_vector_index()
        except Exception:
            pass


def _mock_translator_translate(text, source="auto", target="en"):
    if not text or source == target:
        return text
    return text


def _mock_translator_detect(text):
    return "en"


@pytest.fixture(autouse=True)
def _mock_external_services():
    from app.api.query import _rate_limit
    _rate_limit.clear()
    with patch("app.api.query.brightdata_search", return_value=[]), \
         patch("app.api.query.search_document_links", return_value=[]), \
         patch("app.api.query.enrich_query_context", return_value=""), \
         patch("app.api.query.get_relevant_gov_links", return_value=[]), \
         patch("app.api.query.translator_service") as mock_ts, \
         patch("app.services.rag_engine._build_azure_client", return_value=None):
        mock_ts.detect_language = _mock_translator_detect
        mock_ts.translate_text = _mock_translator_translate
        yield


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    def test_health_has_schemes_count(self):
        response = client.get("/health")
        body = response.json()
        assert "schemes_loaded" in body
        assert body["schemes_loaded"] >= 50


class TestSchemesEndpoint:
    def test_get_all_schemes(self):
        response = client.get("/schemes")
        assert response.status_code == 200
        data = response.json()
        assert "schemes" in data
        assert "total" in data
        assert data["total"] >= 50

    def test_filter_central_schemes(self):
        response = client.get("/schemes?type=central")
        data = response.json()
        for s in data["schemes"]:
            assert s["type"] == "central"

    def test_filter_state_schemes(self):
        response = client.get("/schemes?type=state")
        data = response.json()
        for s in data["schemes"]:
            assert s["type"] == "state"

    def test_filter_by_specific_state(self):
        response = client.get("/schemes?state=Telangana")
        data = response.json()
        assert data["total"] > 0
        for s in data["schemes"]:
            assert s["type"] == "central" or s.get("state") == "Telangana"

    def test_all_schemes_have_benefits(self):
        response = client.get("/schemes")
        data = response.json()
        for s in data["schemes"]:
            assert "benefits" in s, f"Missing benefits for {s['name']}"
            assert len(s["benefits"]) > 0

    def test_all_schemes_have_eligibility(self):
        response = client.get("/schemes")
        data = response.json()
        for s in data["schemes"]:
            assert "eligibility" in s, f"Missing eligibility for {s['name']}"

    def test_all_schemes_have_documents(self):
        response = client.get("/schemes")
        data = response.json()
        for s in data["schemes"]:
            assert "documents" in s, f"Missing documents for {s['name']}"
            assert isinstance(s["documents"], list)
            assert len(s["documents"]) > 0

    def test_schemes_normalized_type_field(self):
        response = client.get("/schemes")
        data = response.json()
        for s in data["schemes"]:
            assert "type" in s
            assert s["type"] in ("central", "state")


class TestQueryEndpoint:
    def test_basic_query(self):
        payload = {"query": "PM-KISAN eligibility", "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "recommended_schemes" in data
        assert "response_language" in data
        assert "intent" in data

    def test_answer_uses_offline_engine(self):
        payload = {"query": "PM-KISAN income support", "language": "en"}
        response = client.post("/query", json=payload)
        data = response.json()
        assert len(data["answer"]) > 20

    def test_query_with_state(self):
        payload = {"query": "scheme for farmers", "language": "en", "state": "Telangana"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_query_auto_language(self):
        payload = {"query": "farming scheme for me", "language": "auto"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_hindi_language(self):
        payload = {"query": "PM-KISAN ke bare mein batao", "language": "hi"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["response_language"] == "hi"

    def test_query_returns_doc_links(self):
        payload = {"query": "PM-KISAN details", "language": "en"}
        response = client.post("/query", json=payload)
        data = response.json()
        assert "doc_links" in data
        assert isinstance(data["doc_links"], list)

    def test_query_returns_nearest_centers(self):
        payload = {"query": "scheme details", "language": "en", "state": "Tamil Nadu"}
        response = client.post("/query", json=payload)
        data = response.json()
        assert "nearest_centers" in data
        assert isinstance(data["nearest_centers"], list)

    def test_query_with_farmer_profile(self):
        payload = {
            "query": "best scheme for me",
            "language": "en",
            "occupation": "farmer",
            "state": "Maharashtra",
            "income": 100000,
            "crop": "cotton",
            "land_size": "3",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "recommended_schemes" in data


class TestQueryEdgeCases:
    def test_empty_query(self):
        payload = {"query": "", "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code in (200, 422)

    def test_very_long_query(self):
        payload = {"query": "scheme " * 500, "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code in (200, 422)

    def test_query_missing_body(self):
        response = client.post("/query", json={})
        assert response.status_code == 422

    def test_query_invalid_language(self):
        payload = {"query": "test", "language": "xyz"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_unicode_text(self):
        payload = {"query": "किसान योजना बताओ", "language": "hi"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_query_bengali_text(self):
        payload = {"query": "কৃষক প্রকল্প", "language": "bn"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_telugu_text(self):
        payload = {"query": "రైతు పథకం", "language": "te"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_tamil_text(self):
        payload = {"query": "விவசாயி திட்டம்", "language": "ta"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_gujarati_text(self):
        payload = {"query": "ખેડૂત યોજના", "language": "gu"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_with_only_whitespace(self):
        payload = {"query": "   ", "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code in (200, 422)
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data

    def test_query_with_special_characters(self):
        payload = {"query": "<script>alert('xss')</script>", "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_query_with_html_injection(self):
        payload = {
            "query": '<img src=x onerror="alert(1)"> scheme details',
            "language": "en",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_extremely_large_income(self):
        payload = {
            "query": "scheme for me",
            "language": "en",
            "income": 999999999999,
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommended_schemes" in data

    def test_missing_content_type_form_post(self):
        response = client.post("/query", content=b'{"query": "test"}')
        assert response.status_code in (200, 422)

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200


class TestStateSchemes:
    def test_telangana_schemes_exist(self):
        response = client.get("/schemes?state=Telangana")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Telangana"]
        assert len(state_schemes) >= 3

    def test_maharashtra_schemes_exist(self):
        response = client.get("/schemes?state=Maharashtra")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Maharashtra"]
        assert len(state_schemes) >= 2

    def test_andhra_pradesh_schemes_exist(self):
        response = client.get("/schemes?state=Andhra Pradesh")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Andhra Pradesh"]
        assert len(state_schemes) >= 2

    def test_madhya_pradesh_scheme_exists(self):
        response = client.get("/schemes?state=Madhya Pradesh")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Madhya Pradesh"]
        assert len(state_schemes) >= 1

    def test_odisha_scheme_exists(self):
        response = client.get("/schemes?state=Odisha")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Odisha"]
        assert len(state_schemes) >= 1

    def test_chhattisgarh_scheme_exists(self):
        response = client.get("/schemes?state=Chhattisgarh")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Chhattisgarh"]
        assert len(state_schemes) >= 1

    def test_bihar_scheme_exists(self):
        response = client.get("/schemes?state=Bihar")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Bihar"]
        assert len(state_schemes) >= 1

    def test_total_schemes_at_least_55(self):
        response = client.get("/schemes")
        data = response.json()
        assert data["total"] >= 55


class TestQueryWithFarmerProfile:
    def test_query_with_crop_and_land_size(self):
        payload = {
            "query": "farming scheme for wheat",
            "language": "en",
            "occupation": "farmer",
            "state": "Telangana",
            "crop": "wheat",
            "land_size": "3",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 10

    def test_query_with_all_profile_fields(self):
        payload = {
            "query": "best scheme for me",
            "language": "en",
            "occupation": "farmer",
            "state": "Maharashtra",
            "income": 60000,
            "crop": "cotton",
            "land_size": "2",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "recommended_schemes" in data

    def test_query_with_no_profile(self):
        payload = {"query": "general farming tips", "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_msp_related(self):
        payload = {"query": "wheat msp price", "language": "en", "crop": "wheat"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data


class TestQueryStates:
    def test_query_telangana_state(self):
        payload = {
            "query": "Rythu Bandhu farmer Telangana",
            "language": "en",
            "state": "Telangana",
            "occupation": "farmer",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_maharashtra_state(self):
        payload = {
            "query": "Ladki Bahin scheme Maharashtra women",
            "language": "en",
            "state": "Maharashtra",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_odisha_state(self):
        payload = {
            "query": "KALIA Yojana farmer Odisha",
            "language": "en",
            "state": "Odisha",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_andhra_pradesh_state(self):
        payload = {
            "query": "YSR scheme Andhra Pradesh",
            "language": "en",
            "state": "Andhra Pradesh",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200


class TestMultiLanguageQueries:
    def test_all_supported_languages_accepted(self):
        languages = ["hi", "en", "bn", "te", "mr", "ta", "gu", "kn", "ml", "pa", "or"]
        for lang in languages:
            payload = {"query": "farming scheme", "language": lang}
            response = client.post("/query", json=payload)
            assert response.status_code == 200, f"Failed for language: {lang}"
            data = response.json()
            assert data["response_language"] == lang, f"Wrong response_language for {lang}"

    def test_response_language_matches_request(self):
        payload = {"query": "scheme details", "language": "ta"}
        response = client.post("/query", json=payload)
        data = response.json()
        assert data["response_language"] == "ta"
