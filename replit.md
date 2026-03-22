# SaarthiAI

A voice-first AI assistant helping Indian citizens discover and **apply for** government schemes through step-by-step voice conversations. Features multi-turn conversation tracking, farmer profile personalization, full i18n for 11 languages (Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia), Google Maps integration for help centers, and offline-first PWA with intelligent caching.

## Architecture

- **Frontend**: Static HTML/CSS/JS served from `frontend/` directory on port 5000
  - ChatGPT-inspired voice chat UI with animated voice orb (listening=green pulse, speaking=purple glow)
  - **Conversation tracking**: maintains conversation history across messages; AI remembers previous questions and guides farmers step by step
  - **New Chat button**: resets conversation context for a fresh topic
  - Voice interrupt: tap mic or start typing to stop speech instantly
  - Stop Speaking button visible during TTS playback
  - Multi-language STT support: all 11 languages properly mapped via INDIAN_LANG_MAP
  - Smart voice selection: strongly prefers female voices, premium/neural voices; rate 0.92, pitch 1.12 for clarity
  - Text chunking: splits long responses into 180-char chunks at sentence/phrase boundaries for clear TTS
  - Interim results shown during speech recognition
  - Mobile-first PWA with service worker (`sw.js`) and manifest
  - Full i18n for all 11 languages (23+ keys per language including offline labels, sync messages, feature indicators)
  - Markdown rendering for AI responses (bold, italic, headings, clickable URLs)
  - Offline answer engine: caches all schemes via /schemes endpoint; keyword search + template response generation in user's selected language
  - **Emergency info cache**: 6 agriculture helplines (Kisan Call Center, PM-KISAN, PMFBY, Soil Health, CSC, DAO) + 5 emergency URLs stored in localStorage for offline access
  - **Offline feature banner**: when offline, shows localized banner indicating available features (saved answers, scheme info, helpline numbers)
  - **Sync on reconnect**: when internet comes back, atomically fetches fresh scheme data (keeps old cache if fetch fails), updates emergency info, shows sync status
  - **Enhanced LRU cache**: 150 entries, 14-day TTL, fuzzy word-overlap matching (filters stop words in English + Hindi), pre-caches 8 popular farmer queries
  - State/Central scheme filtering with seasonal suggestion chips
  - Profile drawer for farmer metadata (state, crop, land size, income)
  - Google Maps links on help center cards ("Open in Maps")
  - URL sanitization: validates all links as http/https before rendering

- **Backend**: FastAPI Python application in `backend/` directory on port 8000
  - **Conversation-aware AI**: accepts conversation_history in requests; passes multi-turn context to Azure OpenAI so AI can guide farmers step-by-step through scheme applications
  - **Step-by-step system prompt**: AI acts as a patient village-level guide — breaks application process into steps, asks follow-up questions, picks up from where it left off
  - Language-specific system prompts: AI responds directly in target language (Hindi, Tamil, Bengali, etc.) — with deterministic fallback translation via script detection
  - RAG engine: keyword search with state/occupation boosting + rich context builder (includes benefits, helpline, application URL, web snippets)
  - Offline answer engine (`offline_answer_engine.py`): full LANG_LABELS for all 11 languages with KCC-quality structured template answers
  - **In-memory answer cache**: LRU, 500 entries, 1-hour TTL, conversation-aware cache keys
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
  - **GZip compression**: all API responses >500 bytes compressed (67KB→17KB for schemes, 74% reduction)
  - Rate limiting (20 req/min) on query endpoint
  - Resilient error handling: all external service calls (Bright Data, translation, gov API) wrapped in try/except to prevent hard failures

- **Entry Point**: `server.py` - Starts both the backend uvicorn server and a proxying HTTP server
  - Port 5000: Frontend + API proxy
  - Port 8000: FastAPI backend (internal only)

## Key Files

- `server.py` - Main entry point, starts both servers
- `backend/app/main.py` - FastAPI app
- `backend/app/config.py` - Settings (env vars / Replit Secrets)
- `backend/app/api/query.py` - Main query endpoint with language detection, translation, Bright Data enrichment, Azure OpenAI, farmer profile, conversation history, URL sanitization
- `backend/app/api/health.py` - Health check endpoint with scheme count
- `backend/app/api/help_centers.py` - Help centers API endpoint
- `backend/app/schemas.py` - Pydantic models (QueryRequest accepts crop, land_size, conversation_history; ConversationMessage for multi-turn; HelpCenter has maps_url)
- `backend/app/services/rag_engine.py` - RAG engine: conversation-aware system prompt, multi-turn message building (last 6 turns), keyword search, Azure OpenAI with 1500 token limit, conversation-aware cache, offline fallback
- `backend/app/services/offline_answer_engine.py` - KCC-quality template answers for all 11 languages with LANG_LABELS
- `backend/app/services/gov_data_service.py` - data.gov.in API integration + gov portal links
- `backend/app/services/brightdata_service.py` - Bright Data SERP with gov site targeting
- `backend/app/services/translator.py` - Translation with Google Translator fallback
- `backend/app/services/recommendation_engine.py` - Data-driven scheme scoring
- `backend/app/services/help_center_service.py` - Help centers with Google Maps URL generation
- `backend/app/services/scheme_loader.py` - Scheme data loader with normalization and filtering
- `backend/app/data/schemes.json` - 60+ government schemes with rich data
- `frontend/index.html` - ChatGPT-inspired mobile voice chat UI with New Chat button and all 11 languages in selector
- `frontend/script.js` - Full i18n (11 languages), conversation tracking, markdown renderer, offline scheme engine, enhanced fuzzy cache, API calls, chat, scheme filtering
- `frontend/voice.js` - Voice recognition/synthesis with female voice preference, multi-language support, text chunking for clarity
- `frontend/sw.js` - Service worker for offline PWA
- `frontend/manifest.json` - PWA manifest

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main query - accepts query, language, state, occupation, income, crop, land_size, conversation_history. Returns answer, recommendations, doc_links, nearest_centers (with maps_url) |
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
