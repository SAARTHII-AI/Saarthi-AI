from fastapi import APIRouter
from app.services.scheme_loader import load_schemes

router = APIRouter()

@router.get("/")
async def get_schemes():
    schemes = load_schemes()
    return {"schemes": schemes}
