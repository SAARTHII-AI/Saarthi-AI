# SaarthiAI

A voice-first AI assistant helping Indian citizens discover government schemes. Features ChatGPT-inspired voice UX, farmer profile personalization, full i18n for 11 languages (Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia), Google Maps integration for help centers, and offline-first PWA with local scheme search engine.

## Architecture

- **Frontend**: Static HTML/CSS/JS served from `frontend/` directory on port 5000
  - ChatGPT-inspired voice chat UI with animated voice orb (listening=green pulse, speaking=purple glow)
  - Voice interrupt: tap mic or start typing to stop speech instantly
  - Stop Speaking button visible during TTS playback
  - Multi-language STT support: all 11 languages properly mapped via INDIAN_LANG_MAP
  - Smart voice selection: prefers Google/Microsoft neural voices, rate 0.88, pitch 1.05
  - Interim results shown during speech recognition
  - Mobile-first PWA with service worker (`sw.js`) and manifest
  - Full i18n for all 11 languages (20+ keys per language including offline labels)
  - Markdown rendering for AI responses (bold, italic, headings, clickable URLs)
  - Offline answer engine: caches all schemes via /schemes endpoint; keyword search + template response generation in user's selected language
  - LRU cache (50 entries, 7-day TTL) for offline support with fuzzy matching
  - State/Central scheme filtering with seasonal suggestion chips
  - Profile drawer for farmer metadata (state, crop, land size, income)
  - Google Maps links on help center cards ("Open in Maps")
  - URL sanitization: validates all links as http/https before rendering

- **Backend**: FastAPI Python application in `backend/` directory on port 8000
  - Advanced prompt engineering: structured 6-section KCC-quality responses (Benefits/Eligibility/How-to-Apply/Documents/Helpline/Follow-up)
  - Language-specific system prompts: AI responds directly in target language (Hindi, Tamil, Bengali, etc.) — with deterministic fallback translation via script detection
  - RAG engine: keyword search with state/occupation boosting + rich context builder (includes benefits, helpline, application URL, web snippets)
  - Offline answer engine (`offline_answer_engine.py`): full LANG_LABELS for all 11 languages with KCC-quality structured template answers
  - In-memory answer cache (LRU, 200 entries, 30-min TTL) for Azure OpenAI responses
  - Farmer profile passed to Azure OpenAI for personalized answers (state, crop, land, income)
  - Azure OpenAI: deployment=gpt-5.3-chat, max_completion_tokens=1500, anti-hallucination guardrails in prompt
  - Bright Data SERP enrichment targeting official gov sites (india.gov.in, data.gov.in, pib.gov.in)
  - data.gov.in API integration for live MSP data and agriculture statistics
  - Gov portal link enrichment (PM-KISAN, PMFBY, eNAM, Soil Health Card, etc.)
  - Translation via deep-translator/Google (Azure AI Translator as optional enhancement)
  - URL sanitization: all links validated as http/https before returning to frontend
  - Script-based language detection: verifies AI response is in target language's native script
  - 60+ government schemes (central + state-level) with rich data
  - Help center service with 50+ entries + Google Maps URL generation
  - Rate limiting (20 req/min) on query endpoint
  - Resilient error handling: all external service calls (Bright Data, translation, gov API) wrapped in try/except to prevent hard failures

- **Entry Point**: `server.py` - Starts both the backend uvicorn server and a proxying HTTP server
  - Port 5000: Frontend + API proxy
  - Port 8000: FastAPI backend (internal only)

## Key Files

- `server.py` - Main entry point, starts both servers
- `backend/app/main.py` - FastAPI app
- `backend/app/config.py` - Settings (env vars / Replit Secrets)
- `backend/app/api/query.py` - Main query endpoint with language detection, translation, Bright Data enrichment, Azure OpenAI, farmer profile, URL sanitization
- `backend/app/api/health.py` - Health check endpoint with scheme count
- `backend/app/api/help_centers.py` - Help centers API endpoint
- `backend/app/schemas.py` - Pydantic models (QueryRequest accepts crop, land_size; HelpCenter has maps_url)
- `backend/app/services/rag_engine.py` - RAG engine: rich system prompt with language instructions, keyword search, Azure OpenAI with 1500 token limit, answer cache, offline fallback
- `backend/app/services/offline_answer_engine.py` - KCC-quality template answers for all 11 languages with LANG_LABELS
- `backend/app/services/gov_data_service.py` - data.gov.in API integration + gov portal links
- `backend/app/services/brightdata_service.py` - Bright Data SERP with gov site targeting
- `backend/app/services/translator.py` - Translation with Google Translator fallback
- `backend/app/services/recommendation_engine.py` - Data-driven scheme scoring
- `backend/app/services/help_center_service.py` - Help centers with Google Maps URL generation
- `backend/app/services/scheme_loader.py` - Scheme data loader with normalization and filtering
- `backend/app/data/schemes.json` - 60+ government schemes with rich data
- `frontend/index.html` - ChatGPT-inspired mobile voice chat UI with all 11 languages in selector
- `frontend/script.js` - Full i18n (11 languages), markdown renderer, offline scheme engine, API calls, cache, chat, scheme filtering
- `frontend/voice.js` - Voice recognition/synthesis with multi-language support, proper INDIAN_LANG_MAP for all 11 languages
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
| `AZURE_OPENAI_DEPLOYMENT` | Env var | Model deployment name (gpt-5.3-chat) |
| `AZURE_OPENAI_API_VERSION` | Env var | API version (2025-01-01-preview) |
| `BRIGHTDATA_API_TOKEN` | Secret | Bright Data SERP authentication |
| `BRIGHTDATA_SERP_ZONE` | Env var | SERP zone name (serp_api1) |
| `BRIGHTDATA_DC_PASS` | Secret | Datacenter proxy password |
| `OFFLINE_ONLY` | Env var | Set `true` to disable all external APIs |

## Running

The "Start application" workflow runs `python server.py`.

## Testing

```bash
cd backend && python -m pytest tests/ -v
```

145 tests covering: API endpoints, edge cases, intent detection, scheme loading, recommendations, help centers, services, gov data service, RAG cache, offline answer engine, farmer profile queries, multi-language queries, state scheme validation.
