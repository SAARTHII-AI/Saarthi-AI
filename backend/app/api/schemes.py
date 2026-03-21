from typing import Optional
from fastapi import APIRouter, Query
from app.services.scheme_loader import load_schemes

router = APIRouter()

@router.get("/")
async def get_schemes(
    scheme_type: Optional[str] = Query(None, alias="type"),
    state: Optional[str] = Query(None)
):
    schemes = load_schemes(scheme_type=scheme_type, state=state)
    return {"schemes": schemes, "total": len(schemes)}
