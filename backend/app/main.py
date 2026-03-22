import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from app.api import health, schemes, query, help_centers
from app.services.rag_engine import rag_engine
from mangum import Mangum

app = FastAPI(title="SaarthiAI", description="Voice-first AI assistant for government schemes.")

app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(help_centers.router, prefix="/help-centers", tags=["help-centers"])

app.include_router(api_router)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(help_centers.router, prefix="/help-centers", tags=["help-centers"])

@app.on_event("startup")
async def startup_event():
    try:
        rag_engine.load_documents()
        rag_engine.build_vector_index()
    except Exception as e:
        print(f"Error initializing RAG engine on startup: {e}")

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKSPACE_ROOT = os.path.dirname(_BACKEND_ROOT)

_CANDIDATE_DIRS = [
    os.environ.get("SAARTHI_FRONTEND_DIR", ""),
    os.path.join(_BACKEND_ROOT, "frontend_dist"),
    os.path.join(_WORKSPACE_ROOT, "frontend"),
]
FRONTEND_DIR = next((d for d in _CANDIDATE_DIRS if d and os.path.isdir(d)), None)

if FRONTEND_DIR:
    print(f"Frontend directory found: {FRONTEND_DIR}")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend_static")

    @app.get("/manifest.json")
    def serve_manifest():
        return FileResponse(os.path.join(FRONTEND_DIR, "manifest.json"))

    @app.get("/sw.js")
    def serve_sw():
        return FileResponse(os.path.join(FRONTEND_DIR, "sw.js"), media_type="application/javascript")

    @app.get("/script.js")
    def serve_script():
        return FileResponse(os.path.join(FRONTEND_DIR, "script.js"), media_type="application/javascript")

    @app.get("/voice.js")
    def serve_voice():
        return FileResponse(os.path.join(FRONTEND_DIR, "voice.js"), media_type="application/javascript")

    @app.get("/style.css")
    def serve_style():
        return FileResponse(os.path.join(FRONTEND_DIR, "style.css"), media_type="text/css")

    icons_dir = os.path.join(FRONTEND_DIR, "icons")
    if os.path.isdir(icons_dir):
        app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")
else:
    print(f"WARNING: No frontend directory found — static file serving disabled")
    print(f"  Checked: {_CANDIDATE_DIRS}")

    @app.get("/")
    def serve_fallback():
        return PlainTextResponse("SaarthiAI API is running. Frontend not available.")

handler = Mangum(app)
