from fastapi import APIRouter
from app.schemas import QueryRequest, QueryResponse, DocumentLink
from app.services.rag_engine import rag_engine
from app.services.intent_detection import detect_intent
from app.services.recommendation_engine import recommend_schemes
from app.services.translator import translator_service
from app.services.web_search import fetch_serp_snippets, fetch_document_links
from app.services.llm_answer import generate_answer_with_azure
from app.config import settings
from typing import List
import re

router = APIRouter()


def _extract_document_type_from_query(query: str) -> str:
    """
    Extract the document type being asked about from the query.
    Returns a specific document type or 'documents required' as default.
    """
    query_lower = query.lower()

    # Common document types in government schemes
    document_patterns = [
        (r'\b(aadhaar|aadhar|uidai)\b', 'Aadhaar card'),
        (r'\b(pan\s*card|pancard)\b', 'PAN card'),
        (r'\b(ration\s*card)\b', 'ration card'),
        (r'\b(income\s*certificate)\b', 'income certificate'),
        (r'\b(caste\s*certificate|sc|st|obc)\b', 'caste certificate'),
        (r'\b(bank\s*(account|passbook)|passbook)\b', 'bank account'),
        (r'\b(voter\s*id|election\s*card)\b', 'voter ID'),
        (r'\b(bpl\s*card|below\s*poverty)\b', 'BPL card'),
        (r'\b(land\s*(record|document|patta))\b', 'land records'),
        (r'\b(application\s*form|apply|registration)\b', 'application form'),
        (r'\b(eligibility|who\s*can|criteria)\b', 'eligibility criteria'),
    ]

    for pattern, doc_type in document_patterns:
        if re.search(pattern, query_lower):
            return doc_type

    return 'documents required'


def _should_fetch_document_links(intent: str, english_query: str, top_schemes: List[dict]) -> bool:
    """
    Determine if document links should be fetched based on intent and scheme match.

    Returns True when the query is explicitly document-related and a scheme is identified.
    """
    if intent != "document_requirements":
        return False

    if not top_schemes:
        return False

    query_lower = english_query.lower()
    explicit_doc_terms = (
        "document",
        "documents",
        "paper",
        "papers",
        "certificate",
        "proof",
        "aadhaar",
        "aadhar",
        "pan",
        "form",
    )
    return any(term in query_lower for term in explicit_doc_terms)

@router.post("/", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    original_query = request.query

    # Language Detection & Setting
    detected_lang = request.language
    if request.language == "auto" or not request.language:
        detected_lang = translator_service.detect_language(original_query)
        # Fallback if detected_lang is None or unsupported
        if not detected_lang:
            detected_lang = "en"

    # Always translate non-English queries to English for backend processing
    english_query = original_query
    if detected_lang != "en":
        english_query = translator_service.translate_text(original_query, source=detected_lang, target="en")

    # Detect the intent using the translated English query
    intent = detect_intent(english_query)

    # Retrieve relevant schemes from the RAG pipeline using English query
    top_schemes = rag_engine.search_similar(english_query)
    local_context = "\n".join(
        [f"{s['name']}: {s['description']} (Eligibility: {s['eligibility']})" for s in top_schemes]
    )

    web_context = ""
    document_links: List[DocumentLink] = []

    if not settings.offline_only:
        # Fetch SERP snippets for context
        web_context = await fetch_serp_snippets(english_query)

        # Fetch document links when relevant
        if _should_fetch_document_links(intent, english_query, top_schemes):
            # Use the top scheme name if available, otherwise extract from query
            scheme_name = ""
            if top_schemes:
                scheme_name = top_schemes[0].get('name', '')

            if scheme_name:
                document_type = _extract_document_type_from_query(english_query)
                document_links = await fetch_document_links(scheme_name, document_type)

    combined_context = local_context
    if web_context:
        combined_context = (
            f"{local_context}\n\nWeb search snippets:\n{web_context}"
            if local_context
            else f"Web search snippets:\n{web_context}"
        )

    english_answer = None
    has_any_context = bool(local_context.strip() or web_context.strip())
    if has_any_context and settings.azure_openai_configured() and not settings.offline_only:
        english_answer = await generate_answer_with_azure(
            english_query=english_query,
            intent=intent,
            local_context=local_context,
            web_context=web_context,
        )

    if not english_answer:
        english_answer = rag_engine.generate_answer(combined_context, english_query)

    # Translate answer back to user's language if necessary
    final_answer = english_answer
    if detected_lang != "en":
        final_answer = translator_service.translate_text(english_answer, source="en", target=detected_lang)

    # Provide recommendations if relevant criteria are available
    raw_recommendations = recommend_schemes(request.model_dump())

    # Translate recommendations if necessary
    final_recommendations = []
    for rec in raw_recommendations:
        rec_name = rec["name"]
        rec_desc = rec["description"]
        if detected_lang != "en":
            rec_name = translator_service.translate_text(rec_name, source="en", target=detected_lang)
            rec_desc = translator_service.translate_text(rec_desc, source="en", target=detected_lang)
        final_recommendations.append({"name": rec_name, "description": rec_desc})

    return QueryResponse(
        intent=intent,
        answer=final_answer,
        recommended_schemes=final_recommendations,
        document_links=document_links,
        response_language=detected_lang
    )
