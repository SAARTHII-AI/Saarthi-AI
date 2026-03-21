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

    def test_hindi_keyword_patrata(self):
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
        schemes = load_schemes(state="Telangana")
        assert len(schemes) > 0
        for s in schemes:
            assert s["type"] == "central" or s.get("state") == "Telangana"

    def test_combined_filters(self):
        schemes = load_schemes(scheme_type="state", state="Telangana")
        for s in schemes:
            assert s["type"] == "state"
            assert s.get("state") == "Telangana"

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

    def test_normalization_scope_to_type(self):
        schemes = load_schemes()
        for s in schemes:
            assert "type" in s
            assert s["type"] in ("central", "state")

    def test_normalization_states_to_state(self):
        schemes = load_schemes(scheme_type="state")
        for s in schemes:
            assert s.get("state") is not None, f"Scheme {s['name']} missing state"

    def test_normalization_application_url_in_links(self):
        schemes = load_schemes()
        for s in schemes:
            if s.get("application_url") and s["application_url"].startswith("http"):
                assert s["application_url"] in s["documents_links"], \
                    f"application_url not in documents_links for {s['name']}"

    def test_schemes_have_benefits_field(self):
        schemes = load_schemes()
        for s in schemes:
            assert "benefits" in s, f"Missing benefits in {s['name']}"
            assert len(s["benefits"]) > 10

    def test_schemes_have_eligibility_field(self):
        schemes = load_schemes()
        for s in schemes:
            assert "eligibility" in s, f"Missing eligibility in {s['name']}"
            assert len(s["eligibility"]) > 5

    def test_central_schemes_count(self):
        schemes = load_schemes(scheme_type="central")
        assert len(schemes) >= 30

    def test_state_schemes_count(self):
        schemes = load_schemes(scheme_type="state")
        assert len(schemes) >= 10


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


class TestGovDataService:
    def test_get_relevant_gov_links_pm_kisan(self):
        from app.services.gov_data_service import get_relevant_gov_links
        links = get_relevant_gov_links("pm-kisan scheme eligibility")
        assert isinstance(links, list)
        assert len(links) > 0
        assert any("PM-KISAN" in l["title"] for l in links)

    def test_get_relevant_gov_links_crop_insurance(self):
        from app.services.gov_data_service import get_relevant_gov_links
        links = get_relevant_gov_links("crop insurance pmfby")
        assert isinstance(links, list)
        assert len(links) > 0

    def test_get_relevant_gov_links_mandi_prices(self):
        from app.services.gov_data_service import get_relevant_gov_links
        links = get_relevant_gov_links("mandi market price wheat")
        assert isinstance(links, list)
        assert len(links) > 0

    def test_get_relevant_gov_links_soil_health(self):
        from app.services.gov_data_service import get_relevant_gov_links
        links = get_relevant_gov_links("soil health card")
        assert isinstance(links, list)
        assert len(links) > 0

    def test_get_relevant_gov_links_no_match(self):
        from app.services.gov_data_service import get_relevant_gov_links
        links = get_relevant_gov_links("random unrelated query xyz")
        assert isinstance(links, list)

    def test_enrich_query_context_returns_string(self):
        from app.services.gov_data_service import enrich_query_context
        result = enrich_query_context("farming scheme")
        assert isinstance(result, str)

    def test_enrich_query_context_with_crop(self):
        from app.services.gov_data_service import enrich_query_context
        result = enrich_query_context("msp price", crop="wheat")
        assert isinstance(result, str)


class TestRAGEngineCache:
    def test_cache_key_generation(self):
        from app.services.rag_engine import rag_engine
        key1 = rag_engine._cache_key("context1", "question1", {"state": "Bihar"})
        key2 = rag_engine._cache_key("context1", "question1", {"state": "Bihar"})
        key3 = rag_engine._cache_key("context2", "question1", {"state": "Bihar"})
        assert key1 == key2
        assert key1 != key3

    def test_cache_key_different_profiles(self):
        from app.services.rag_engine import rag_engine
        key1 = rag_engine._cache_key("ctx", "q", {"state": "Bihar"})
        key2 = rag_engine._cache_key("ctx", "q", {"state": "UP"})
        assert key1 != key2

    def test_cache_key_none_profile(self):
        from app.services.rag_engine import rag_engine
        key1 = rag_engine._cache_key("ctx", "q", None)
        key2 = rag_engine._cache_key("ctx", "q", {})
        assert isinstance(key1, str)
        assert isinstance(key2, str)


class TestOfflineAnswerEngine:
    def test_generate_answer_with_schemes_en(self):
        from app.services.offline_answer_engine import generate_offline_answer
        schemes = [
            {"name": "PM-KISAN", "description": "Income support", "benefits": "Rs 6000/year",
             "eligibility": "Farmers", "helpline": "155261", "application_url": "https://pmkisan.gov.in/"},
        ]
        answer = generate_offline_answer(schemes, "PM-KISAN details", language="en")
        assert "PM-KISAN" in answer
        assert "6000" in answer or "6,000" in answer
        assert "CSC" in answer

    def test_generate_answer_with_schemes_hi(self):
        from app.services.offline_answer_engine import generate_offline_answer
        schemes = [
            {"name": "PM-KISAN", "description": "Income support", "benefits": "Rs 6000/year",
             "eligibility": "Farmers", "helpline": "155261"},
        ]
        answer = generate_offline_answer(schemes, "PM-KISAN kya hai", language="hi")
        assert "PM-KISAN" in answer
        assert "योजना" in answer or "जानकारी" in answer

    def test_generate_answer_empty_schemes_en(self):
        from app.services.offline_answer_engine import generate_offline_answer
        answer = generate_offline_answer([], "random question", language="en")
        assert "PM-KISAN" in answer
        assert "CSC" in answer

    def test_generate_answer_empty_schemes_hi(self):
        from app.services.offline_answer_engine import generate_offline_answer
        answer = generate_offline_answer([], "random question", language="hi")
        assert "CSC" in answer or "केंद्र" in answer

    def test_generate_answer_with_farmer_profile(self):
        from app.services.offline_answer_engine import generate_offline_answer
        schemes = [
            {"name": "Test Scheme", "description": "Test", "benefits": "Test benefits",
             "eligibility": "Farmers in Bihar", "state": "Bihar", "type": "state"},
        ]
        profile = {"state": "Bihar", "crop": "wheat"}
        answer = generate_offline_answer(schemes, "scheme for me", profile, "en")
        assert "Bihar" in answer

    def test_generate_answer_multiple_schemes(self):
        from app.services.offline_answer_engine import generate_offline_answer
        schemes = [
            {"name": "Scheme A", "description": "Desc A", "benefits": "Ben A", "eligibility": "All"},
            {"name": "Scheme B", "description": "Desc B", "benefits": "Ben B", "eligibility": "All"},
            {"name": "Scheme C", "description": "Desc C", "benefits": "Ben C", "eligibility": "All"},
        ]
        answer = generate_offline_answer(schemes, "help me", language="en")
        assert "Scheme A" in answer
        assert "Scheme B" in answer
        assert "Scheme C" in answer

    def test_generate_answer_truncates_long_description(self):
        from app.services.offline_answer_engine import generate_offline_answer
        long_desc = "A" * 300
        schemes = [{"name": "Test", "description": long_desc, "benefits": "X", "eligibility": "Y"}]
        answer = generate_offline_answer(schemes, "test", language="en")
        assert "..." in answer


class TestStateSchemesByRegion:
    def test_telangana_schemes_exist(self):
        schemes = load_schemes(state="Telangana")
        state_schemes = [s for s in schemes if s.get("state") == "Telangana"]
        assert len(state_schemes) >= 3

    def test_maharashtra_schemes_exist(self):
        schemes = load_schemes(state="Maharashtra")
        state_schemes = [s for s in schemes if s.get("state") == "Maharashtra"]
        assert len(state_schemes) >= 2

    def test_andhra_pradesh_schemes_exist(self):
        schemes = load_schemes(state="Andhra Pradesh")
        state_schemes = [s for s in schemes if s.get("state") == "Andhra Pradesh"]
        assert len(state_schemes) >= 2

    def test_madhya_pradesh_scheme_exists(self):
        schemes = load_schemes(state="Madhya Pradesh")
        state_schemes = [s for s in schemes if s.get("state") == "Madhya Pradesh"]
        assert len(state_schemes) >= 1

    def test_odisha_scheme_exists(self):
        schemes = load_schemes(state="Odisha")
        state_schemes = [s for s in schemes if s.get("state") == "Odisha"]
        assert len(state_schemes) >= 1

    def test_bihar_scheme_exists(self):
        schemes = load_schemes(state="Bihar")
        state_schemes = [s for s in schemes if s.get("state") == "Bihar"]
        assert len(state_schemes) >= 1

    def test_chhattisgarh_scheme_exists(self):
        schemes = load_schemes(state="Chhattisgarh")
        state_schemes = [s for s in schemes if s.get("state") == "Chhattisgarh"]
        assert len(state_schemes) >= 1

    def test_up_scheme_exists(self):
        schemes = load_schemes(state="Uttar Pradesh")
        state_schemes = [s for s in schemes if s.get("state") == "Uttar Pradesh"]
        assert len(state_schemes) >= 1

    def test_jharkhand_scheme_exists(self):
        schemes = load_schemes(state="Jharkhand")
        state_schemes = [s for s in schemes if s.get("state") == "Jharkhand"]
        assert len(state_schemes) >= 1

    def test_total_schemes_minimum_55(self):
        schemes = load_schemes()
        assert len(schemes) >= 55

    def test_all_state_schemes_have_required_fields(self):
        schemes = load_schemes(scheme_type="state")
        for s in schemes:
            assert "name" in s, f"Missing name in state scheme"
            assert "description" in s, f"Missing description in {s.get('name', '?')}"
            assert "eligibility" in s, f"Missing eligibility in {s.get('name', '?')}"
            assert "benefits" in s, f"Missing benefits in {s.get('name', '?')}"
            assert "documents" in s, f"Missing documents in {s.get('name', '?')}"
            assert "documents_links" in s, f"Missing documents_links in {s.get('name', '?')}"
            assert s["type"] == "state"
            assert s["state"] is not None


class TestRAGSearchSchemes:
    def test_search_finds_telangana_scheme(self):
        from app.services.rag_engine import rag_engine
        if not rag_engine.schemes:
            rag_engine.load_documents()
        results = rag_engine.search_similar("Rythu Bandhu farmer Telangana", user_state="Telangana")
        assert len(results) > 0

    def test_search_finds_pm_kisan(self):
        from app.services.rag_engine import rag_engine
        if not rag_engine.schemes:
            rag_engine.load_documents()
        results = rag_engine.search_similar("PM-KISAN income support farmer")
        assert len(results) > 0
        assert any("KISAN" in r["name"] for r in results)

    def test_search_finds_odisha_scheme(self):
        from app.services.rag_engine import rag_engine
        if not rag_engine.schemes:
            rag_engine.load_documents()
        results = rag_engine.search_similar("KALIA farmer Odisha", user_state="Odisha")
        assert len(results) > 0

    def test_search_finds_mudra_loan(self):
        from app.services.rag_engine import rag_engine
        if not rag_engine.schemes:
            rag_engine.load_documents()
        results = rag_engine.search_similar("Mudra loan small business enterprise")
        assert len(results) > 0

    def test_state_boost_works(self):
        from app.services.rag_engine import rag_engine
        if not rag_engine.schemes:
            rag_engine.load_documents()
        results = rag_engine.search_similar("farmer scheme", user_state="Telangana")
        has_telangana = any(s.get("state") == "Telangana" for s in results)
        assert has_telangana, f"Telangana schemes not boosted: {[s['name'] for s in results]}"

    def test_search_includes_benefits_scoring(self):
        from app.services.rag_engine import rag_engine
        if not rag_engine.schemes:
            rag_engine.load_documents()
        results = rag_engine.search_similar("pension monthly Rs 3000")
        assert len(results) > 0
        found_pension = any("pension" in r.get("name", "").lower() or "pension" in r.get("benefits", "").lower() for r in results)
        assert found_pension


class TestRAGEngineOfflineFallback:
    def test_generate_answer_no_azure_uses_offline_engine(self):
        from app.services.rag_engine import rag_engine
        if not rag_engine.schemes:
            rag_engine.load_documents()
        from unittest.mock import patch
        with patch("app.services.rag_engine._build_azure_client", return_value=None):
            schemes = [
                {"name": "PM-KISAN", "description": "Income support for farmers",
                 "benefits": "Rs 6000/year", "eligibility": "All farmers",
                 "helpline": "155261", "application_url": "https://pmkisan.gov.in/"}
            ]
            context = rag_engine._build_rich_context(schemes=schemes)
            answer = rag_engine.generate_answer(
                context, "PM KISAN details",
                matched_schemes=schemes, language="en"
            )
            assert "PM-KISAN" in answer
            assert len(answer) > 50

    def test_generate_answer_empty_context_uses_offline(self):
        from app.services.rag_engine import rag_engine
        from unittest.mock import patch
        with patch("app.services.rag_engine._build_azure_client", return_value=None):
            answer = rag_engine.generate_answer("", "any question", language="en")
            assert len(answer) > 20
            assert "CSC" in answer or "scheme" in answer.lower()

    def test_build_rich_context_includes_benefits(self):
        from app.services.rag_engine import rag_engine
        schemes = [
            {"name": "Test", "description": "Desc", "benefits": "Rs 5000/year",
             "eligibility": "All", "documents": ["Aadhaar", "PAN"],
             "helpline": "1800", "application_url": "https://test.gov.in/"}
        ]
        context = rag_engine._build_rich_context(schemes=schemes)
        assert "Benefits: Rs 5000/year" in context
        assert "Documents Required:" in context
        assert "Helpline: 1800" in context
        assert "https://test.gov.in/" in context
