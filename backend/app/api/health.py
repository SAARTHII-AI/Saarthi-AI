from fastapi import APIRouter
from app.services.scheme_loader import load_schemes

router = APIRouter()

@router.get("/")
def check_health():
    schemes = load_schemes()
    return {
        "status": "ok",
        "message": "SaarthiAI backend is running properly.",
        "schemes_loaded": len(schemes),
    }
