# SaarthiAI

A voice-first AI assistant helping Indian citizens discover government schemes. Features ChatGPT-inspired voice UX, farmer profile personalization, full i18n for 11 languages (Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia), Google Maps integration for help centers, and offline-first PWA with local scheme search engine.

## Architecture

- **Frontend**: Static HTML/CSS/JS served from `frontend/` directory on port 5000
  - ChatGPT-inspired voice chat UI with animated voice orb (listening=green pulse, speaking=purple glow)
  - Voice interrupt: tap mic or start typing to stop speech instantly
  - Stop Speaking button visible during TTS playback
  - Multi-language STT support: Hindi, English, Marathi, Bengali, Telugu, Tamil, Kannada, Gujarati, Punjabi, Odia, Malayalam
  - Smart voice selection: prefers Google/Microsoft neural voices, rate 0.88, pitch 1.05
  - Interim results shown during speech recognition
  - Mobile-first PWA with service worker (`sw.js`) and manifest
  - Full i18n for all 11 languages (20+ keys per language including offline labels)
  - Offline answer engine: caches all schemes via /schemes endpoint; keyword search + template response generation in user's selected language
  - LRU cache (50 entries, 7-day TTL) for offline support with fuzzy matching
  - State/Central scheme filtering with seasonal suggestion chips
  - Profile drawer for farmer metadata (state, crop, land size, income)
  - Google Maps links on help center cards ("Open in Maps")
  - Fixed language selector dropdown with proper arrow icon (no overlap)
  - Scheme type badges, document links, and XSS protection via escapeHtml

- **Backend**: FastAPI Python application in `backend/` directory on port 8000
  - Enhanced RAG engine: keyword search with state/occupation boosting + rich context builder (includes benefits, helpline, application URL)
  - Offline answer engine (`offline_answer_engine.py`): generates structured template answers when Azure OpenAI unavailable
  - In-memory answer cache (LRU, 200 entries, 30-min TTL) for Azure OpenAI responses
  - Farmer profile passed to Azure OpenAI for personalized answers (state, crop, land, income)
  - data.gov.in API integration for live MSP data and agriculture statistics
  - Gov portal link enrichment (PM-KISAN, PMFBY, eNAM, Soil Health Card, etc.)
  - Bright Data SERP enrichment targeting official gov sites (india.gov.in, data.gov.in, pib.gov.in)
  - Translation via Azure AI Translator (fallback: deep-translator/Google)
  - 55+ government schemes (central + state-level) with rich data: benefits, eligibility, helpline, application_url, documents
  - Scheme loader normalizes new JSON format (scope→type, states[]→state, application_url→documents_links)
  - Help center service with 50+ entries + Google Maps URL generation
  - Health endpoint returns schemes_loaded count
  - Rate limiting (20 req/min) on query endpoint
  - Language detection via langdetect

- **Entry Point**: `server.py` - Starts both the backend uvicorn server and a proxying HTTP server
  - Port 5000: Frontend + API proxy
  - Port 8000: FastAPI backend (internal only)

## Key Files

- `server.py` - Main entry point, starts both servers
- `backend/app/main.py` - FastAPI app
- `backend/app/config.py` - Settings (env vars / Replit Secrets)
- `backend/app/api/query.py` - Main query endpoint with farmer profile context + gov data enrichment
- `backend/app/api/health.py` - Health check endpoint with scheme count
- `backend/app/api/help_centers.py` - Help centers API endpoint
- `backend/app/schemas.py` - Pydantic models (QueryRequest accepts crop, land_size; HelpCenter has maps_url)
- `backend/app/services/rag_engine.py` - Enhanced RAG: keyword search with boosting + rich context + Azure OpenAI + answer cache + offline fallback
- `backend/app/services/offline_answer_engine.py` - Template-based answer generation for offline/no-Azure mode
- `backend/app/services/gov_data_service.py` - data.gov.in API integration + gov portal links
- `backend/app/services/brightdata_service.py` - Bright Data SERP with gov site targeting
- `backend/app/services/translator.py` - Azure AI Translator with fallback
- `backend/app/services/recommendation_engine.py` - Data-driven scheme scoring
- `backend/app/services/help_center_service.py` - Help centers with Google Maps URL generation
- `backend/app/services/scheme_loader.py` - Scheme data loader with normalization and filtering
- `backend/app/data/schemes.json` - 55+ government schemes with rich data
- `frontend/index.html` - ChatGPT-inspired mobile voice chat UI
- `frontend/script.js` - Full i18n (11 languages), offline scheme engine, API calls, cache, chat, scheme filtering
- `frontend/voice.js` - Voice recognition/synthesis with multi-language support, interrupt, voice selection
- `frontend/sw.js` - Service worker for offline PWA
- `frontend/manifest.json` - PWA manifest

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main query - accepts query, language, state, occupation, income, crop, land_size. Returns answer, recommendations, doc_links, nearest_centers (with maps_url) |
| `/schemes` | GET | List schemes, filterable by `type` and `state` |
| `/health` | GET | Health check with schemes_loaded count |
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

145 tests covering: API endpoints, edge cases, intent detection, scheme loading, recommendations, help centers, services, gov data service, RAG cache, offline answer engine, farmer profile queries, multi-language queries, state scheme validation.
