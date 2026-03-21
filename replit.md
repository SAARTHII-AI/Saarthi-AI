# SaarthiAI

A voice-first AI assistant helping Indian citizens discover government schemes. Features ChatGPT-inspired voice UX, farmer profile personalization, Hindi/English with auto-detect for all Indian languages online, Google Maps integration for help centers, and offline-first PWA.

## Architecture

- **Frontend**: Static HTML/CSS/JS served from `frontend/` directory on port 5000
  - ChatGPT-inspired voice chat UI with animated voice orb (listening=green pulse, speaking=purple glow)
  - Voice interrupt: tap mic or start typing to stop speech instantly
  - Stop Speaking button visible during TTS playback
  - Smart voice selection: prefers Google/Microsoft neural voices, rate 0.9, pitch 1.05
  - Mobile-first PWA with service worker (`sw.js`) and manifest
  - Offline: Hindi + English i18n; Online: auto-detects any Indian language via Azure Translator
  - LRU cache (50 entries, 7-day TTL) for offline support with fuzzy matching
  - State/Central scheme filtering with seasonal suggestion chips
  - Profile drawer for farmer metadata (state, crop, land size, income)
  - Google Maps links on help center cards ("Open in Maps")
  - Scheme type badges, document links, and XSS protection via escapeHtml

- **Backend**: FastAPI Python application in `backend/` directory on port 8000
  - Enhanced RAG engine: keyword search with state/occupation boosting + rich context builder
  - Farmer profile passed to Azure OpenAI for personalized answers (state, crop, land, income)
  - Bright Data SERP enrichment targeting official gov sites (india.gov.in, data.gov.in, pib.gov.in)
  - Translation via Azure AI Translator (fallback: deep-translator/Google)
  - 55 government schemes (29 central + 26 state-level across 10 states)
  - Help center service with 50+ entries + Google Maps URL generation
  - Rate limiting (20 req/min) on query endpoint
  - Language detection via langdetect

- **Entry Point**: `server.py` - Starts both the backend uvicorn server and a proxying HTTP server
  - Port 5000: Frontend + API proxy
  - Port 8000: FastAPI backend (internal only)

## Key Files

- `server.py` - Main entry point, starts both servers
- `backend/app/main.py` - FastAPI app
- `backend/app/config.py` - Settings (env vars / Replit Secrets)
- `backend/app/api/query.py` - Main query endpoint with farmer profile context
- `backend/app/api/help_centers.py` - Help centers API endpoint
- `backend/app/schemas.py` - Pydantic models (QueryRequest accepts crop, land_size; HelpCenter has maps_url)
- `backend/app/services/rag_engine.py` - Enhanced RAG: keyword search with boosting + rich context + Azure OpenAI
- `backend/app/services/brightdata_service.py` - Bright Data SERP with gov site targeting
- `backend/app/services/translator.py` - Azure AI Translator with fallback
- `backend/app/services/recommendation_engine.py` - Data-driven scheme scoring
- `backend/app/services/help_center_service.py` - Help centers with Google Maps URL generation
- `backend/app/services/scheme_loader.py` - Scheme data loader with filtering
- `backend/app/data/schemes.json` - 55 government schemes
- `frontend/index.html` - ChatGPT-inspired mobile voice chat UI
- `frontend/script.js` - API calls, cache, chat, scheme filtering, Google Maps rendering
- `frontend/voice.js` - Voice recognition/synthesis with interrupt, voice selection, speaking states
- `frontend/sw.js` - Service worker for offline PWA
- `frontend/manifest.json` - PWA manifest

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main query - accepts query, language, state, occupation, income, crop, land_size. Returns answer, recommendations, doc_links, nearest_centers (with maps_url) |
| `/schemes` | GET | List schemes, filterable by `type` and `state` |
| `/health` | GET | Health check |
| `/api/help-centers` | GET | Help centers, filterable by `state` |

## Environment Variables & Secrets

| Key | Type | Purpose |
|-----|------|---------|
| `AZURE_OPENAI_API_KEY` | Secret | Azure OpenAI authentication |
| `AZURE_OPENAI_ENDPOINT` | Env var | Azure OpenAI resource URL |
| `AZURE_OPENAI_DEPLOYMENT` | Env var | Model deployment name |
| `AZURE_OPENAI_API_VERSION` | Env var | API version |
| `AZURE_TRANSLATOR_KEY` | Secret | Azure AI Translator key |
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

78 tests covering: API endpoints, edge cases, intent detection, scheme loading, recommendations, help centers, services.
