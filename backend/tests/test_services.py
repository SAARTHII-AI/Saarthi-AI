import pytest
from app.services.intent_detection import detect_intent
from app.services.scheme_loader import load_schemes
from app.services.recommendation_engine import recommend_schemes
from app.services.help_center_service import get_help_centers
from app.services.speech_service import SpeechService
from app.services.translator import TranslatorService


class TestIntentDetection:
    def test_eligibility_check(self):
        assert detect_intent("Am I eligible for this scheme?") == "eligibility_check"

    def test_eligibility_patrata(self):
        assert detect_intent("patrata kya hai") == "eligibility_check"

    def test_document_requirements(self):
        assert detect_intent("What documents are required?") == "document_requirements"

    def test_benefits_query(self):
        assert detect_intent("What are the benefits of this scheme?") == "benefits_query"

    def test_benefits_fayde(self):
        assert detect_intent("fayde kya milega") == "benefits_query"

    def test_scheme_search(self):
        assert detect_intent("Tell me about PM yojana") == "scheme_search"

    def test_general_information(self):
        assert detect_intent("hello how are you") == "general_information"

    def test_hindi_keyword_patrата(self):
        assert detect_intent("पात्रता बताइए") == "eligibility_check"

    def test_hindi_keyword_documents(self):
        assert detect_intent("दस्तावेज़ कौन से चाहिए") == "document_requirements"

    def test_hindi_keyword_benefits(self):
        assert detect_intent("लाभ क्या है") == "benefits_query"

    def test_hindi_keyword_scheme(self):
        assert detect_intent("योजना बताओ") == "scheme_search"

    def test_tamil_keyword_eligibility(self):
        assert detect_intent("yogya for scheme") == "eligibility_check"

    def test_tamil_keyword_documents(self):
        assert detect_intent("ஆவணங்கள் required") == "document_requirements"

    def test_tamil_keyword_benefits(self):
        assert detect_intent("நன்மைகள் scheme") == "benefits_query"

    def test_tamil_keyword_scheme(self):
        assert detect_intent("திட்டம் details") == "scheme_search"

    def test_mixed_case(self):
        assert detect_intent("ELIGIBILITY for Scheme") == "eligibility_check"

    def test_empty_string(self):
        assert detect_intent("") == "general_information"

    def test_random_text(self):
        assert detect_intent("asdfghjkl 12345") == "general_information"


class TestSchemeLoader:
    def test_load_all_schemes(self):
        schemes = load_schemes()
        assert isinstance(schemes, list)
        assert len(schemes) >= 50

    def test_filter_by_central(self):
        schemes = load_schemes(scheme_type="central")
        assert len(schemes) > 0
        for s in schemes:
            assert s["type"] == "central"

    def test_filter_by_state_type(self):
        schemes = load_schemes(scheme_type="state")
        assert len(schemes) > 0
        for s in schemes:
            assert s["type"] == "state"

    def test_filter_by_state_name(self):
        schemes = load_schemes(state="Tamil Nadu")
        assert len(schemes) > 0
        for s in schemes:
            assert s["type"] == "central" or s.get("state") == "Tamil Nadu"

    def test_combined_filters(self):
        schemes = load_schemes(scheme_type="state", state="Tamil Nadu")
        for s in schemes:
            assert s["type"] == "state"
            assert s.get("state") == "Tamil Nadu"

    def test_invalid_state_returns_central_only(self):
        schemes = load_schemes(state="Atlantis")
        for s in schemes:
            assert s["type"] == "central"

    def test_case_insensitive_type_filter(self):
        schemes = load_schemes(scheme_type="Central")
        assert len(schemes) > 0
        for s in schemes:
            assert s["type"] == "central"

    def test_all_schemes_have_required_fields(self):
        schemes = load_schemes()
        for s in schemes:
            assert "name" in s
            assert "type" in s
            assert s["type"] in ("central", "state")
            assert "documents_links" in s
            assert isinstance(s["documents_links"], list)
            if s["type"] == "state":
                assert s.get("state") is not None


class TestRecommendationEngine:
    def test_farmer_gets_farm_schemes(self):
        results = recommend_schemes({"occupation": "farmer"})
        assert isinstance(results, list)
        assert len(results) > 0
        names = [r["name"].lower() for r in results]
        assert any("kisan" in n or "farmer" in n or "fasal" in n for n in names), \
            f"Expected farmer-related scheme, got: {names}"

    def test_student_gets_education_schemes(self):
        results = recommend_schemes({"occupation": "student", "age": 20})
        assert isinstance(results, list)
        assert len(results) > 0
        found = any(
            "education" in r.get("description", "").lower()
            or "student" in r.get("description", "").lower()
            or "scholarship" in r.get("description", "").lower()
            or "skill" in r.get("description", "").lower()
            for r in results
        )
        assert found, f"Expected education-related scheme, got: {[r['name'] for r in results]}"

    def test_elderly_gets_pension_schemes(self):
        results = recommend_schemes({"age": 65})
        assert isinstance(results, list)
        assert len(results) > 0
        found = any(
            "pension" in r.get("description", "").lower()
            or "elderly" in r.get("description", "").lower()
            or "senior" in r.get("description", "").lower()
            for r in results
        )
        assert found, f"Expected pension-related scheme, got: {[r['name'] for r in results]}"

    def test_empty_profile_gets_fallback(self):
        results = recommend_schemes({})
        assert isinstance(results, list)
        assert len(results) > 0

    def test_max_five_recommendations(self):
        results = recommend_schemes({"occupation": "farmer", "income": 100000, "age": 30})
        assert len(results) <= 5

    def test_state_filter_in_recommendations(self):
        results = recommend_schemes({"occupation": "farmer", "state": "Maharashtra"})
        assert isinstance(results, list)
        for r in results:
            if r.get("state"):
                assert r["state"] == "Maharashtra"

    def test_recommendations_have_required_fields(self):
        results = recommend_schemes({"occupation": "farmer"})
        for r in results:
            assert "name" in r
            assert "description" in r
            assert "type" in r
            assert "documents_links" in r

    def test_low_income_gets_bpl_schemes(self):
        results = recommend_schemes({"income": 100000})
        assert isinstance(results, list)
        assert len(results) > 0

    def test_extremely_large_income(self):
        results = recommend_schemes({"income": 999999999999})
        assert isinstance(results, list)

    def test_vendor_occupation(self):
        results = recommend_schemes({"occupation": "vendor"})
        assert isinstance(results, list)


class TestHelpCenterService:
    def test_no_state_returns_national_only(self):
        centers = get_help_centers()
        assert len(centers) > 0
        for c in centers:
            assert c["type"] == "national_helpline"

    def test_national_helplines_always_included(self):
        for state in ["Tamil Nadu", "Maharashtra", "Uttar Pradesh", "Bihar"]:
            centers = get_help_centers(state=state)
            national = [c for c in centers if c["type"] == "national_helpline"]
            assert len(national) > 0, f"No national helplines for {state}"

    def test_state_centers_returned_for_known_state(self):
        centers = get_help_centers(state="Tamil Nadu")
        state_only = [c for c in centers if c["type"] != "national_helpline"]
        assert len(state_only) > 0

    def test_unknown_state_returns_national_only(self):
        centers = get_help_centers(state="Atlantis")
        for c in centers:
            assert c["type"] == "national_helpline"

    def test_all_states_have_centers(self):
        known_states = [
            "Uttar Pradesh", "Maharashtra", "Tamil Nadu", "Bihar",
            "Rajasthan", "Madhya Pradesh", "Karnataka", "West Bengal",
            "Telangana", "Odisha",
        ]
        for state in known_states:
            centers = get_help_centers(state=state)
            state_only = [c for c in centers if c["type"] != "national_helpline"]
            assert len(state_only) > 0, f"No centers found for {state}"

    def test_center_fields(self):
        centers = get_help_centers(state="Tamil Nadu")
        for c in centers:
            assert "name" in c
            assert "type" in c
            assert "phone" in c
            assert "address" in c
            assert "district" in c

    def test_whitespace_state_name(self):
        centers = get_help_centers(state="  Tamil Nadu  ")
        state_only = [c for c in centers if c["type"] != "national_helpline"]
        assert len(state_only) > 0


class TestSpeechService:
    def test_fallback_returns_browser_api_flag(self):
        service = SpeechService()
        service._azure_available = False
        result = service.text_to_speech("hello", language="en")
        assert result["use_browser_api"] is True
        assert result["audio_base64"] is None
        assert result["text"] == "hello"

    def test_stt_fallback(self):
        service = SpeechService()
        service._azure_available = False
        result = service.speech_to_text(b"fake_audio", language="hi")
        assert isinstance(result, str)
        assert "browser" in result.lower() or "not implemented" in result.lower()


class TestTranslatorService:
    def test_detect_language_returns_valid_code(self):
        service = TranslatorService()
        lang = service.detect_language("hello world")
        assert isinstance(lang, str)
        assert len(lang) >= 2

    def test_detect_language_hindi(self):
        service = TranslatorService()
        lang = service.detect_language("नमस्ते दुनिया यह हिंदी में है")
        assert lang in ("hi", "mr")

    def test_translate_same_language_preserves_text(self):
        service = TranslatorService()
        result = service.translate_text("hello", source="en", target="en")
        assert result == "hello"

    def test_translate_empty_text(self):
        service = TranslatorService()
        result = service.translate_text("", source="en", target="hi")
        assert result == ""

    def test_translate_none_text(self):
        service = TranslatorService()
        result = service.translate_text(None, source="en", target="hi")
        assert result is None
