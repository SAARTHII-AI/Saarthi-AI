# SaarthiAI

A voice-first AI assistant that helps Indian citizens discover and understand government schemes in Hindi, Tamil, and English. Features state-wise and central scheme categorization, document links, nearest help center lookup, and mobile-first PWA experience.

## Architecture

- **Frontend**: Static HTML/CSS/JS served from `frontend/` directory on port 5000
  - Mobile-first PWA with service worker (`sw.js`) and manifest
  - Uses Web Speech API for voice recognition (fallback) + Azure Speech Services (when available)
  - Tailwind CSS via CDN for styling
  - LRU cache (50 entries, 7-day TTL) for offline support
  - State/Central scheme filtering with seasonal suggestion chips
  - Profile drawer for farmer metadata (state, crop, land, income)
  - Renders document links, help center info, and scheme type badges in responses

- **Backend**: FastAPI Python application in `backend/` directory on port 8000
  - RAG engine with keyword-based scheme search + Azure OpenAI answer generation
  - Bright Data SERP enrichment for live web snippets + document link search
  - Translation via Azure AI Translator (fallback: deep-translator/Google)
  - Speech services via Azure Speech (TTS/STT with fallback to browser APIs)
  - 55 government schemes (29 central + 26 state-level across 10 states)
  - Help center service with 50+ CSC/government office entries
  - Language detection via langdetect

- **Entry Point**: `server.py` - Starts both the backend uvicorn server and a proxying HTTP server
  - Port 5000: Frontend + API proxy (serves static files, forwards API paths to backend)
  - Port 8000: FastAPI backend (internal only)

## Key Files

- `server.py` - Main entry point, starts both servers
- `backend/app/main.py` - FastAPI app
- `backend/app/config.py` - Settings (reads from env vars / Replit Secrets)
- `backend/app/api/query.py` - Main query endpoint (search + enrichment + AI generation)
- `backend/app/api/help_centers.py` - Help centers API endpoint
- `backend/app/services/rag_engine.py` - Keyword search + Azure OpenAI answer generation
- `backend/app/services/brightdata_service.py` - Bright Data SERP enrichment + document link search
- `backend/app/services/translator.py` - Azure AI Translator with deep-translator fallback
- `backend/app/services/speech_service.py` - Azure Speech TTS/STT with browser API fallback
- `backend/app/services/recommendation_engine.py` - Data-driven scheme recommendation scoring
- `backend/app/services/help_center_service.py` - CSC/government help center lookup by state
- `backend/app/services/scheme_loader.py` - Scheme data loader with type/state filtering
- `backend/app/data/schemes.json` - 55 government schemes (central + 10 states)
- `frontend/index.html` - Main mobile-first UI
- `frontend/script.js` - API calls, cache, chat logic, scheme filtering
- `frontend/voice.js` - Voice recognition/synthesis
- `frontend/sw.js` - Service worker for offline PWA support
- `frontend/manifest.json` - PWA manifest

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main query - accepts query, language, state, occupation, income etc. Returns answer, recommendations, doc_links, nearest_centers |
| `/schemes` | GET | List schemes, filterable by `type` (central/state) and `state` |
| `/health` | GET | Health check |
| `/api/help-centers` | GET | Help centers, filterable by `state` query param |

## Environment Variables & Secrets

| Key | Type | Purpose |
|-----|------|---------|
| `AZURE_OPENAI_API_KEY` | Secret | Azure OpenAI authentication |
| `AZURE_OPENAI_ENDPOINT` | Env var | Azure OpenAI resource URL |
| `AZURE_OPENAI_DEPLOYMENT` | Env var | Model deployment name |
| `AZURE_OPENAI_API_VERSION` | Env var | API version |
| `AZURE_TRANSLATOR_KEY` | Secret | Azure AI Translator key |
| `AZURE_TRANSLATOR_ENDPOINT` | Env var | Translator endpoint (default: Microsoft API) |
| `AZURE_TRANSLATOR_REGION` | Env var | Azure region (default: eastus) |
| `AZURE_SPEECH_KEY` | Secret | Azure Speech Services key |
| `AZURE_SPEECH_REGION` | Env var | Azure Speech region (default: eastus) |
| `BRIGHTDATA_API_TOKEN` | Secret | Bright Data SERP authentication |
| `BRIGHTDATA_SERP_ZONE` | Env var | SERP zone name |
| `BRIGHTDATA_DC_PASS` | Secret | Datacenter proxy password |
| `OFFLINE_ONLY` | Env var | Set `true` to disable all external APIs |

## Running

The "Start application" workflow runs `python server.py`.

## Testing

```bash
cd backend && python -m pytest tests/ -v
```

78 tests covering: API endpoints (health, schemes, query, help-centers), edge cases (empty/long queries, XSS, malformed JSON), intent detection, scheme loading/filtering, recommendations, help centers, speech/translation services.
