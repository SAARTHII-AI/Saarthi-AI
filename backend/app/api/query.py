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

logger = logging.getLogger(__name__)

router = APIRouter()

_rate_limit: dict = defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 20

def _check_rate_limit(client_ip: str):
    now = time.time()
    _rate_limit[client_ip] = [t for t in _rate_limit[client_ip] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit[client_ip]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
    _rate_limit[client_ip].append(now)

@router.post("/", response_model=QueryResponse)
async def handle_query(request: QueryRequest, raw_request: Request):
    client_ip = raw_request.client.host if raw_request.client else "unknown"
    _check_rate_limit(client_ip)
    original_query = request.query

    detected_lang = request.language
    if request.language == "auto" or not request.language:
        detected_lang = translator_service.detect_language(original_query)
        if not detected_lang:
            detected_lang = "en"

    english_query = original_query
    if detected_lang != "en":
        english_query = translator_service.translate_text(original_query, source=detected_lang, target="en")

    intent = detect_intent(english_query)

    top_schemes = rag_engine.search_similar(english_query)
    local_context_parts = [
        f"{s['name']}: {s['description']} (Eligibility: {s['eligibility']})"
        for s in top_schemes
    ]

    web_snippets = brightdata_search(english_query)
    if web_snippets:
        logger.info(f"Bright Data returned {len(web_snippets)} snippet(s)")

    context_parts = web_snippets + local_context_parts
    context = "\n".join(context_parts)

    english_answer = rag_engine.generate_answer(context, english_query)

    final_answer = english_answer
    if detected_lang != "en":
        final_answer = translator_service.translate_text(english_answer, source="en", target=detected_lang)

    raw_recommendations = recommend_schemes(request.model_dump())

    final_recommendations = []
    for rec in raw_recommendations:
        rec_name = rec["name"]
        rec_desc = rec["description"]
        if detected_lang != "en":
            rec_name = translator_service.translate_text(rec_name, source="en", target=detected_lang)
            rec_desc = translator_service.translate_text(rec_desc, source="en", target=detected_lang)
        final_recommendations.append({
            "name": rec_name,
            "description": rec_desc,
            "type": rec.get("type"),
            "state": rec.get("state"),
            "documents_links": rec.get("documents_links")
        })

    doc_links = []
    seen_urls = set()
    for scheme in top_schemes:
        for link in scheme.get("documents_links", []) or []:
            if link not in seen_urls:
                seen_urls.add(link)
                doc_links.append({"title": scheme["name"], "url": link})

    if top_schemes:
        primary_scheme = top_schemes[0]
        enriched_links = search_document_links(english_query, primary_scheme["name"])
        for el in enriched_links:
            if el["url"] not in seen_urls:
                seen_urls.add(el["url"])
                doc_links.append({"title": el["title"], "url": el["url"]})

    nearest_centers = []
    user_state = request.state or request.location
    if user_state:
        centers = get_help_centers(state=user_state)
        for c in centers:
            nearest_centers.append({
                "name": c["name"],
                "type": c["type"],
                "phone": c["phone"],
                "address": c["address"],
                "district": c["district"],
            })
    else:
        centers = get_help_centers()
        for c in centers:
            nearest_centers.append({
                "name": c["name"],
                "type": c["type"],
                "phone": c["phone"],
                "address": c["address"],
                "district": c["district"],
            })

    return QueryResponse(
        intent=intent,
        answer=final_answer,
        recommended_schemes=final_recommendations,
        response_language=detected_lang,
        doc_links=doc_links,
        nearest_centers=nearest_centers,
    )
