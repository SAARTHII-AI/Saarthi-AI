from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from app.services.help_center_service import get_help_centers

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_help_centers(state: Optional[str] = Query(None, description="State name to filter help centers")):
    return get_help_centers(state=state)
