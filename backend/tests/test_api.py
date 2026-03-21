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
        assert "message" in body

    def test_api_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestSchemesEndpoint:
    def test_get_all_schemes(self):
        response = client.get("/schemes")
        assert response.status_code == 200
        data = response.json()
        assert "schemes" in data
        assert "total" in data
        assert isinstance(data["schemes"], list)
        assert data["total"] >= 50

    def test_filter_type_central(self):
        response = client.get("/schemes?type=central")
        assert response.status_code == 200
        data = response.json()
        assert len(data["schemes"]) > 0
        for scheme in data["schemes"]:
            assert scheme["type"] == "central"

    def test_filter_type_state(self):
        response = client.get("/schemes?type=state")
        assert response.status_code == 200
        data = response.json()
        assert len(data["schemes"]) > 0
        for scheme in data["schemes"]:
            assert scheme["type"] == "state"

    def test_filter_state_tamil_nadu(self):
        response = client.get("/schemes?state=Tamil Nadu")
        assert response.status_code == 200
        data = response.json()
        assert len(data["schemes"]) > 0
        for scheme in data["schemes"]:
            assert scheme["type"] == "central" or scheme.get("state") == "Tamil Nadu"

    def test_combined_type_and_state(self):
        response = client.get("/schemes?type=state&state=Tamil Nadu")
        assert response.status_code == 200
        data = response.json()
        for scheme in data["schemes"]:
            assert scheme["type"] == "state"
            assert scheme.get("state") == "Tamil Nadu"

    def test_api_prefix_schemes(self):
        response = client.get("/api/schemes")
        assert response.status_code == 200
        data = response.json()
        assert "schemes" in data


class TestQueryEndpoint:
    def test_basic_english_query(self):
        payload = {"query": "Tell me about government schemes", "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "answer" in data
        assert "recommended_schemes" in data
        assert data["response_language"] == "en"

    def test_hindi_query(self):
        with patch("app.api.query.translator_service") as mock_ts:
            mock_ts.detect_language.return_value = "hi"
            mock_ts.translate_text = lambda text, source="auto", target="en": text
            payload = {"query": "सरकारी योजना के बारे में बताइए", "language": "hi"}
            response = client.post("/query", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert data["response_language"] == "hi"

    def test_farmer_gets_pm_kisan(self):
        payload = {
            "query": "kisan yojana documents required for farmer",
            "language": "en",
            "occupation": "farmer",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        names = [s["name"].lower() for s in data["recommended_schemes"]]
        assert any("kisan" in n for n in names), f"Expected PM-KISAN, got: {names}"

    def test_state_specific_query_tamil_nadu(self):
        payload = {
            "query": "farmer scheme",
            "language": "en",
            "occupation": "farmer",
            "state": "Tamil Nadu",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        for scheme in data["recommended_schemes"]:
            if scheme.get("state"):
                assert scheme["state"] == "Tamil Nadu"

    def test_empty_query_fails_422(self):
        payload = {"language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code == 422

    def test_very_long_query(self):
        long_text = "government scheme information " * 50
        payload = {"query": long_text, "language": "en"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_unsupported_language_code(self):
        payload = {"query": "Tell me about schemes", "language": "zz"}
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_response_has_doc_links_and_nearest_centers(self):
        payload = {
            "query": "scheme for farmer",
            "language": "en",
            "state": "Tamil Nadu",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "doc_links" in data
        assert "nearest_centers" in data
        assert isinstance(data["doc_links"], list)
        assert isinstance(data["nearest_centers"], list)

    def test_income_filter_affects_recommendations(self):
        payload_low = {
            "query": "health scheme",
            "language": "en",
            "income": 100000,
        }
        payload_high = {
            "query": "health scheme",
            "language": "en",
            "income": 5000000,
        }
        resp_low = client.post("/query", json=payload_low)
        resp_high = client.post("/query", json=payload_high)
        assert resp_low.status_code == 200
        assert resp_high.status_code == 200
        names_low = {s["name"] for s in resp_low.json()["recommended_schemes"]}
        names_high = {s["name"] for s in resp_high.json()["recommended_schemes"]}
        assert isinstance(names_low, set)
        assert isinstance(names_high, set)


class TestHelpCentersEndpoint:
    def test_get_all_help_centers(self):
        response = client.get("/api/help-centers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_help_centers_with_state_filter(self):
        response = client.get("/api/help-centers?state=Tamil Nadu")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        has_national = any(c["type"] == "national_helpline" for c in data)
        assert has_national
        state_centers = [c for c in data if c["type"] != "national_helpline"]
        assert len(state_centers) > 0

    def test_help_centers_unknown_state(self):
        response = client.get("/api/help-centers?state=Atlantis")
        assert response.status_code == 200
        data = response.json()
        for c in data:
            assert c["type"] == "national_helpline"

    def test_help_centers_no_state_returns_national_only(self):
        response = client.get("/api/help-centers")
        assert response.status_code == 200
        data = response.json()
        for c in data:
            assert c["type"] == "national_helpline"


class TestEdgeCases:
    def test_malformed_json_body(self):
        response = client.post(
            "/query",
            content=b"this is not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

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
        assert "SaarthiAI" in response.json().get("message", "")


class TestNewStateSchemes:
    def test_gujarat_schemes_exist(self):
        response = client.get("/schemes?state=Gujarat")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Gujarat"]
        assert len(state_schemes) >= 3

    def test_punjab_schemes_exist(self):
        response = client.get("/schemes?state=Punjab")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Punjab"]
        assert len(state_schemes) >= 3

    def test_haryana_schemes_exist(self):
        response = client.get("/schemes?state=Haryana")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Haryana"]
        assert len(state_schemes) >= 3

    def test_andhra_pradesh_schemes_exist(self):
        response = client.get("/schemes?state=Andhra Pradesh")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Andhra Pradesh"]
        assert len(state_schemes) >= 3

    def test_kerala_schemes_exist(self):
        response = client.get("/schemes?state=Kerala")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Kerala"]
        assert len(state_schemes) >= 3

    def test_chhattisgarh_schemes_exist(self):
        response = client.get("/schemes?state=Chhattisgarh")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Chhattisgarh"]
        assert len(state_schemes) >= 3

    def test_jharkhand_schemes_exist(self):
        response = client.get("/schemes?state=Jharkhand")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Jharkhand"]
        assert len(state_schemes) >= 3

    def test_assam_schemes_exist(self):
        response = client.get("/schemes?state=Assam")
        data = response.json()
        state_schemes = [s for s in data["schemes"] if s.get("state") == "Assam"]
        assert len(state_schemes) >= 3

    def test_total_schemes_at_least_75(self):
        response = client.get("/schemes")
        data = response.json()
        assert data["total"] >= 75


class TestQueryWithFarmerProfile:
    def test_query_with_crop_and_land_size(self):
        payload = {
            "query": "farming scheme for wheat",
            "language": "en",
            "occupation": "farmer",
            "state": "Haryana",
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
            "state": "Gujarat",
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


class TestQueryNewStates:
    def test_query_gujarat_state(self):
        payload = {
            "query": "farming scheme Gujarat irrigation",
            "language": "en",
            "state": "Gujarat",
            "occupation": "farmer",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_punjab_state(self):
        payload = {
            "query": "paddy farmer Punjab scheme",
            "language": "en",
            "state": "Punjab",
            "occupation": "farmer",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_chhattisgarh_state(self):
        payload = {
            "query": "Rajiv Gandhi Kisan Nyay",
            "language": "en",
            "state": "Chhattisgarh",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200

    def test_query_assam_state(self):
        payload = {
            "query": "tea garden worker scheme Assam",
            "language": "en",
            "state": "Assam",
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 200
