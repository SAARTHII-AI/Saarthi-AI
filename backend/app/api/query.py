from fastapi import APIRouter
from app.schemas import QueryRequest, QueryResponse
from app.services.rag_engine import rag_engine
from app.services.intent_detection import detect_intent
from app.services.recommendation_engine import recommend_schemes
from app.services.translator import translator_service

router = APIRouter()

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
    context = "\n".join([f"{s['name']}: {s['description']} (Eligibility: {s['eligibility']})" for s in top_schemes])
    
    # Generate an answer in English
    english_answer = rag_engine.generate_answer(context, english_query)
    
    # Translate answer back to user's language if necessary
    final_answer = english_answer
    if detected_lang != "en":
        final_answer = translator_service.translate_text(english_answer, source="en", target=detected_lang)
    
    # Provide recommendations if relevant criteria are available
    raw_recommendations = recommend_schemes(request.dict())
    
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
        response_language=detected_lang
    )
