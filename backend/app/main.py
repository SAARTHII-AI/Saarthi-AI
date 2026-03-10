from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, schemes, query
from app.services.rag_engine import rag_engine
from mangum import Mangum

app = FastAPI(title="SaarthiAI", description="Voice-first AI assistant for government schemes.")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router with /api prefix (for Vercel)
api_router = APIRouter(prefix="/api")
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
api_router.include_router(query.router, prefix="/query", tags=["query"])

app.include_router(api_router)

# Also keep routes without prefix for local dev and backward compatibility
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
app.include_router(query.router, prefix="/query", tags=["query"])

@app.on_event("startup")
async def startup_event():
    # Attempt to load documents and build vector index if it hasn't been built
    try:
        rag_engine.load_documents()
        rag_engine.build_vector_index()
    except Exception as e:
        print(f"Error initializing RAG engine on startup: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to SaarthiAI Backend. Use /docs to view API documentation."}

# AWS Lambda handler
handler = Mangum(app)
