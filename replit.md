# SaarthiAI

A voice-first AI assistant that helps citizens discover and understand government schemes in Hindi and Tamil.

## Architecture

- **Frontend**: Static HTML/CSS/JS served from `frontend/` directory on port 5000
  - Uses Web Speech API for voice recognition and text-to-speech
  - Tailwind CSS via CDN for styling
  - Communicates with backend via relative URLs (proxied through the main server)

- **Backend**: FastAPI Python application in `backend/` directory on port 8000
  - RAG engine with keyword-based scheme search
  - Translation via `deep-translator` (Google Translate)
  - Language detection via `langdetect`
  - Scheme data loaded from `backend/app/data/schemes.json`

- **Entry Point**: `server.py` - Starts both the backend uvicorn server and a proxying HTTP server
  - Port 5000: Frontend + API proxy (serves static files and forwards `/query`, `/health`, `/schemes` to backend)
  - Port 8000: FastAPI backend (internal only)

## Key Files

- `server.py` - Main entry point, starts both servers
- `backend/app/main.py` - FastAPI app
- `backend/app/api/query.py` - Main query endpoint
- `backend/app/services/rag_engine.py` - Keyword-based scheme search
- `backend/app/services/translator.py` - Translation service
- `backend/app/data/schemes.json` - Government schemes data
- `frontend/index.html` - Main UI
- `frontend/script.js` - API calls and chat logic
- `frontend/voice.js` - Voice recognition/synthesis

## Setup Notes

- `sentence-transformers` and `faiss-cpu` are listed in requirements.txt but not installed due to disk quota constraints. The RAG engine uses keyword-based search as a fallback, which works without these packages.
- The frontend API_URL is set to `""` (empty string) so all API requests go to the same origin and are proxied to the backend.

## Running

The "Start application" workflow runs `python server.py`, which starts both the backend and the proxying frontend server.
