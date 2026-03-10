from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def check_health():
    return {"status": "ok", "message": "SaarthiAI backend is running properly."}
