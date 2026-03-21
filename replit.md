# SaarthiAI

A voice-first AI assistant that helps citizens discover and understand government schemes in Hindi and Tamil.

## Architecture

- **Frontend**: Static HTML/CSS/JS served from `frontend/` directory on port 5000
  - Uses Web Speech API for voice recognition and text-to-speech
  - Tailwind CSS via CDN for styling
  - Communicates with backend via relative URLs (proxied through the main server)

- **Backend**: FastAPI Python application in `backend/` directory on port 8000
  - RAG engine with keyword-based scheme search + Azure OpenAI answer generation
  - Bright Data SERP enrichment (optional; falls back silently)
  - Translation via `deep-translator` (Google Translate)
  - Language detection via `langdetect`
  - Scheme data loaded from `backend/app/data/schemes.json`

- **Entry Point**: `server.py` - Starts both the backend uvicorn server and a proxying HTTP server
  - Port 5000: Frontend + API proxy (serves static files, forwards `/query`, `/health`, `/schemes` to backend)
  - Port 8000: FastAPI backend (internal only)

## Key Files

- `server.py` - Main entry point, starts both servers
- `backend/app/main.py` - FastAPI app
- `backend/app/config.py` - Settings (reads from env vars / Replit Secrets)
- `backend/app/api/query.py` - Main query endpoint (keyword search + Bright Data + Azure OpenAI)
- `backend/app/services/rag_engine.py` - Keyword search + Azure OpenAI answer generation
- `backend/app/services/brightdata_service.py` - Bright Data SERP enrichment (optional)
- `backend/app/services/translator.py` - Translation service
- `backend/app/data/schemes.json` - Government schemes data
- `frontend/index.html` - Main UI
- `frontend/script.js` - API calls and chat logic
- `frontend/voice.js` - Voice recognition/synthesis

## Environment Variables & Secrets

Set via Replit Secrets / env vars (see `.env.example` for all keys):

| Key | Type | Purpose |
|-----|------|---------|
| `AZURE_OPENAI_API_KEY` | Secret | Azure OpenAI authentication |
| `AZURE_OPENAI_ENDPOINT` | Env var | Azure OpenAI resource URL |
| `AZURE_OPENAI_DEPLOYMENT` | Env var | Model deployment name |
| `AZURE_OPENAI_API_VERSION` | Env var | API version |
| `BRIGHTDATA_API_TOKEN` | Secret | Bright Data SERP authentication |
| `BRIGHTDATA_SERP_ZONE` | Env var | SERP zone name |
| `BRIGHTDATA_DC_PASS` | Secret | Datacenter proxy password |
| `BRIGHTDATA_DC_HOST/PORT/USER` | Env vars | Datacenter proxy config |
| `OFFLINE_ONLY` | Env var | Set `true` to disable all external APIs |

## Setup Notes

- `sentence-transformers` and `faiss-cpu` are in root `requirements.txt` for historical reasons but not installed (disk quota). The RAG engine uses keyword search as the retrieval layer.
- `backend/requirements.txt` mirrors root via `-r ../requirements.txt` — always edit root first.
- The frontend API_URL is `""` (empty string) so all API requests go to same origin and are proxied to backend.

## Running

The "Start application" workflow runs `python server.py`.

## Testing

```bash
cd backend && pytest
```
