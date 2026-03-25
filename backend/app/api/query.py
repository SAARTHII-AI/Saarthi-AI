import asyncio
import logging
import time
from collections import defaultdict
from fastapi import APIRouter, HTTPException, Request
from app.schemas import QueryRequest, QueryResponse
from app.services.rag_engine import rag_engine
from app.services.intent_detection import detect_intent
from app.services.recommendation_engine import recommend_schemes
from app.services.translator import translator_service
from app.services.brightdata_service import search_schemes as brightdata_search
from app.services.brightdata_service import search_document_links
from app.services.help_center_service import get_help_centers
from app.services.gov_data_service import enrich_query_context, get_relevant_gov_links

logger = logging.getLogger(__name__)

router = APIRouter()

DEVANAGARI_RANGE = range(0x0900, 0x097F + 1)
SCRIPT_RANGES = {
    "hi": range(0x0900, 0x097F + 1),
    "mr": range(0x0900, 0x097F + 1),
    "bn": range(0x0980, 0x09FF + 1),
    "te": range(0x0C00, 0x0C7F + 1),
    "ta": range(0x0B80, 0x0BFF + 1),
    "gu": range(0x0A80, 0x0AFF + 1),
    "kn": range(0x0C80, 0x0CFF + 1),
    "ml": range(0x0D00, 0x0D7F + 1),
    "pa": range(0x0A00, 0x0A7F + 1),
    "or": range(0x0B00, 0x0B7F + 1),
    "ur": range(0x0600, 0x06FF + 1),
    "as": range(0x0980, 0x09FF + 1),
}

def _text_likely_in_language(text: str, lang: str) -> bool:
    if lang == "en":
        return True
    script_range = SCRIPT_RANGES.get(lang)
    if not script_range:
        return False
    native_chars = sum(1 for ch in text if ord(ch) in script_range)
    return native_chars > 20

def _is_safe_url(url: str) -> bool:
    if not url:
        return False
    url_stripped = url.strip().lower()
    return url_stripped.startswith("http://") or url_stripped.startswith("https://")

_rate_limit: dict = defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 20

def _check_rate_limit(client_ip: str):
    now = time.time()
    _rate_limit[client_ip] = [t for t in _rate_limit[client_ip] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit[client_ip]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
    _rate_limit[client_ip].append(now)


async def _run_brightdata_search(english_query):
    try:
        result = await asyncio.to_thread(brightdata_search, english_query)
        if result:
            logger.info(f"Bright Data returned {len(result)} snippet(s)")
        return result or []
    except Exception as e:
        logger.warning(f"Bright Data search failed (non-fatal): {e}")
        return []


async def _run_gov_enrichment(english_query, crop):
    try:
        return await asyncio.to_thread(enrich_query_context, english_query, crop=crop)
    except Exception as e:
        logger.warning(f"Gov data enrichment failed (non-fatal): {e}")
        return ""


async def _run_rag_search(english_query, user_state, occupation):
    return await asyncio.to_thread(
        rag_engine.search_similar,
        english_query,
        user_state=user_state,
        occupation=occupation
    )


async def _run_doc_link_search(english_query, primary_scheme_name):
    try:
        return await asyncio.to_thread(search_document_links, english_query, primary_scheme_name)
    except Exception as e:
        logger.warning(f"Bright Data doc link search failed (non-fatal): {e}")
        return []


async def _run_gov_links(english_query):
    try:
        return await asyncio.to_thread(get_relevant_gov_links, english_query)
    except Exception as e:
        logger.warning(f"Gov links failed (non-fatal): {e}")
        return []


async def _run_translate(text, source, target):
    try:
        return await asyncio.to_thread(translator_service.translate_text, text, source, target)
    except Exception as e:
        logger.warning(f"Translation failed (non-fatal): {e}")
        return text


async def _run_transliterate(text, language):
    try:
        return await asyncio.to_thread(translator_service.transliterate_text, text, language)
    except Exception as e:
        logger.warning(f"Transliteration failed (non-fatal): {e}")
        return None


@router.post("/", response_model=QueryResponse)
async def handle_query(request: QueryRequest, raw_request: Request):
    client_ip = raw_request.client.host if raw_request.client else "unknown"
    _check_rate_limit(client_ip)
    original_query = request.query

    detected_lang = request.language
    if request.language == "auto" or not request.language:
        detected_lang = await asyncio.to_thread(translator_service.detect_language, original_query)
        if not detected_lang:
            detected_lang = "en"

    english_query = original_query
    if detected_lang != "en":
        english_query = await _run_translate(original_query, detected_lang, "en")

    intent = detect_intent(english_query)

    farmer_profile = {
        "state": request.state or request.location,
        "occupation": request.occupation,
        "income": request.income,
        "crop": request.crop,
        "land_size": request.land_size,
    }
    farmer_profile = {k: v for k, v in farmer_profile.items() if v}

    top_schemes, web_snippets, gov_context = await asyncio.gather(
        _run_rag_search(
            english_query,
            user_state=request.state or request.location,
            occupation=request.occupation
        ),
        _run_brightdata_search(english_query),
        _run_gov_enrichment(english_query, crop=request.crop),
    )

    context = rag_engine._build_rich_context(
        schemes=top_schemes,
        web_snippets=web_snippets,
        farmer_profile=farmer_profile if farmer_profile else None
    )
    if gov_context:
        context = context + "\n\n" + gov_context if context else gov_context

    conv_history = None
    if request.conversation_history:
        conv_history = [{"role": m.role, "content": m.content} for m in request.conversation_history]

    answer = await asyncio.to_thread(
        rag_engine.generate_answer,
        context,
        english_query,
        farmer_profile=farmer_profile if farmer_profile else None,
        language=detected_lang,
        matched_schemes=top_schemes,
        conversation_history=conv_history,
    )

    final_answer = answer
    answer_romanized = None
    if detected_lang != "en" and answer:
        answer_has_target_lang = _text_likely_in_language(answer, detected_lang)
        if not answer_has_target_lang:
            translated = await _run_translate(answer, "en", detected_lang)
            if translated and len(translated) > 20:
                final_answer = translated

        answer_romanized = await _run_transliterate(final_answer, detected_lang)

    include_schemes = intent in ("scheme_search", "eligibility_check", "benefits_query",
                                    "document_requirements", "application_process", "general_information")
    include_centers = intent in ("helpline_query", "application_process", "general_information")
    include_doc_links = intent not in ("helpline_query",)

    final_recommendations = []
    doc_links_task = None
    gov_links_task = None

    if include_doc_links and top_schemes:
        primary_scheme = top_schemes[0]
        doc_links_task = _run_doc_link_search(english_query, primary_scheme["name"])
        gov_links_task = _run_gov_links(english_query)

    if include_schemes:
        raw_recommendations = recommend_schemes(request.model_dump())
        query_words = set(english_query.lower().split())
        scored_recs = []
        for rec in raw_recommendations:
            rec_name_lower = rec["name"].lower()
            rec_desc_lower = rec.get("description", "").lower()
            relevance = sum(1 for w in query_words if len(w) > 3 and (w in rec_name_lower or w in rec_desc_lower))
            scored_recs.append((relevance, rec))
        scored_recs.sort(key=lambda x: x[0], reverse=True)
        filtered_recs = [r for score, r in scored_recs if score > 0]
        if not filtered_recs:
            filtered_recs = [r for _, r in scored_recs[:3]]

        if detected_lang != "en" and filtered_recs:
            translate_tasks = []
            for rec in filtered_recs:
                translate_tasks.append(_run_translate(rec["name"], "en", detected_lang))
                translate_tasks.append(_run_translate(rec["description"], "en", detected_lang))
            translated_texts = await asyncio.gather(*translate_tasks)

            for i, rec in enumerate(filtered_recs):
                final_recommendations.append({
                    "name": translated_texts[i * 2],
                    "description": translated_texts[i * 2 + 1],
                    "type": rec.get("type"),
                    "state": rec.get("state"),
                    "documents_links": rec.get("documents_links")
                })
        else:
            for rec in filtered_recs:
                final_recommendations.append({
                    "name": rec["name"],
                    "description": rec["description"],
                    "type": rec.get("type"),
                    "state": rec.get("state"),
                    "documents_links": rec.get("documents_links")
                })

    doc_links = []
    if include_doc_links:
        seen_urls = set()
        for scheme in top_schemes:
            for link in scheme.get("documents_links", []) or []:
                if link not in seen_urls and _is_safe_url(link):
                    seen_urls.add(link)
                    doc_links.append({"title": scheme["name"], "url": link})

        if doc_links_task:
            enriched_links = await doc_links_task
            for el in enriched_links:
                if el["url"] not in seen_urls and _is_safe_url(el["url"]):
                    seen_urls.add(el["url"])
                    doc_links.append({"title": el["title"], "url": el["url"]})

        if gov_links_task:
            gov_links = await gov_links_task
            for gl in gov_links:
                if gl["url"] not in seen_urls and _is_safe_url(gl["url"]):
                    seen_urls.add(gl["url"])
                    doc_links.append({"title": gl["title"], "url": gl["url"]})

    nearest_centers = []
    if include_centers:
        user_state = request.state or request.location
        centers = get_help_centers(state=user_state)
        for c in centers:
            nearest_centers.append({
                "name": c["name"],
                "type": c["type"],
                "phone": c["phone"],
                "address": c["address"],
                "district": c["district"],
                "maps_url": c.get("maps_url"),
            })

    return QueryResponse(
        intent=intent,
        answer=final_answer,
        answer_romanized=answer_romanized,
        recommended_schemes=final_recommendations,
        response_language=detected_lang,
        doc_links=doc_links,
        nearest_centers=nearest_centers,
    )
