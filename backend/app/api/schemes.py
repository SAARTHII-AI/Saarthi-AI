from fastapi import APIRouter
from backend.app.services.rag_engine import rag_engine
router = APIRouter()

@router.get("/")
async def get_schemes():
    schemes = rag_engine()
    return {"schemes": schemes}
