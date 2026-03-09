from fastapi import APIRouter
from backend.app.schemas import QueryRequest, QueryResponse
from backend.app.services.rag_engine import rag_engine
from backend.app.services.intent_detection import detect_intent
from backend.app.services.recommendation_engine import recommend_schemes

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    # Detect the intent of the query
    intent = detect_intent(request.query)
    
    # Retrieve relevant schemes from the RAG pipeline
    top_schemes = rag_engine.search_similar(request.query)
    context = "\n".join([f"{s['name']}: {s['description']} (Eligibility: {s['eligibility']})" for s in top_schemes])
    
    # Generate an answer using the context and the user's question
    answer = rag_engine.generate_answer(context, request.query)
    
    # Provide recommendations if relevant criteria are available
    recommendations = recommend_schemes(request.dict())
    
    return QueryResponse(
        intent=intent,
        answer=answer,
        recommended_schemes=recommendations
    )
