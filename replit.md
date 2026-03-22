# SaarthiAI — Technical Reference

A voice-first AI assistant helping Indian farmers discover and **apply for** government schemes step-by-step through natural voice conversations. Supports 11 Indian languages with offline-first PWA architecture, Azure OpenAI GPT-5.3, Bright Data SERP enrichment, multi-turn conversation tracking, and farmer profile personalization.

---

## Architecture Overview

```
User (Mobile Browser) → Proxy Server (Port 5000) → FastAPI Backend (Port 8000)
                                                          ↓
                                            ┌─────────────┴─────────────┐
                                            │    Query Orchestrator      │
                                            │                           │
                                    ┌───────┴───────┐                   │
                                    │ Intent Detect  │                   │
                                    │ (7 intents)    │                   │
                                    └───────┬───────┘                   │
                                            │                           │
                              ┌─────────────┼─────────────┐             │
                              ↓             ↓             ↓             │
                        RAG Engine    Bright Data    Gov Data API        │
                        + Azure LLM   SERP Search   + Portal Links      │
                        + Conv Track  + Mandi Route                     │
                              │             │             │             │
                              └─────────────┼─────────────┘             │
                                            ↓                           │
                                  Section Filtering                     │
                                  (schemes/centers/links                │
                                   based on intent)                     │
                                            ↓                           │
                                   Response + GZip                      │
```

### Two-Server Setup

- **Port 5000** — Python HTTP proxy server (`server.py`)
  - Serves static frontend files from `frontend/` directory
  - Proxies API requests (`/query`, `/schemes`, `/health`, `/api/help-centers`) to backend
  - Forwards `Accept-Encoding` header for end-to-end GZip compression
  - 55-second proxy timeout for slow Azure OpenAI responses
  - Normalizes trailing slashes for API paths

- **Port 8000** — FastAPI backend (`backend/app/main.py`)
  - GZipMiddleware (minimum_size=500 bytes)
  - CORS middleware (allow_origins=["*"], allow_credentials=False)
  - Rate limiting: 20 requests/minute on query endpoint
  - All API routes registered via FastAPI routers

---

## Feature Deep Dives

### 1. Azure OpenAI Integration

- **Deployment**: `gpt-5.3-chat`
- **API Version**: `2025-01-01-preview`
- **Endpoint**: Configured via `AZURE_OPENAI_ENDPOINT` env var
- **Max Tokens**: `max_completion_tokens=1500` (temperature parameter NOT supported by this deployment)
- **System Prompt**: Designed as a "patient village-level government scheme guide"
  - Instructs AI to break application processes into numbered steps
  - Anti-hallucination guardrails: must not fabricate scheme names, amounts, dates, phone numbers
  - Language-specific: prompt tells AI to respond directly in target language
  - Includes farmer profile context (state, crop, land size, income)
  - Includes web snippets from Bright Data SERP for real-time accuracy

### 2. Multi-Turn Conversation Tracking

**Frontend:**
- `conversationHistory[]` array stores all user/assistant messages
- Sent as `conversation_history` in POST body
- `conversationToken` guard prevents duplicate submissions
- "New Chat" button resets history for fresh topics
- Conversation-aware cache keys include history summary

**Backend:**
- `_build_conversation_messages()` in `rag_engine.py` builds Azure OpenAI messages array
- Last 6 turns included as context (system + history + current query)
- Cache key incorporates `history_summary` for conversation-specific caching

### 3. Multi-Layer Cache Architecture

| Layer | Location | Size | TTL | Matching |
|-------|----------|------|-----|----------|
| Backend LRU | In-memory (rag_engine.py) | 500 entries | 1 hour | Exact key (query + profile + history_summary) |
| Frontend LRU | localStorage (script.js) | 150 entries | 14 days | Fuzzy word-overlap (threshold 0.4) |
| Scheme Cache | localStorage | Full dataset | Until sync | Exact key `saarthi_schemes_cache` |
| Emergency Cache | localStorage | 6 helplines + 5 URLs | Permanent | Exact key `saarthi_emergency_info` |
| Service Worker | CacheStorage | App shell files | Until new SW | URL-based |

**Frontend Fuzzy Matching:**
- Filters English stop words (the, is, a, how, what, etc.) and Hindi stop words (ka, ke, ki, hai, etc.)
- Calculates word overlap ratio between query and cached keys
- Threshold: 0.4 (40% word overlap = cache hit)
- Pre-caches 8 popular farmer queries on page load

### 4. Intent Detection & Response Filtering

`intent_detection.py` — Rule-based classifier using keyword matching in English + Hindi + Tamil + other Indian languages:

| Intent | Keywords (samples) | Schemes | Centers | Links |
|--------|--------------------|---------|---------|-------|
| `price_query` | mandi, bhav, daam, rate today, बाजार भाव, मंडी | No | No | Yes |
| `helpline_query` | helpline, call, contact, shikayat, toll free | No | Yes | No |
| `eligibility_check` | eligibility, patrata, who can, पात्रता, தகுதி | Yes | No | Yes |
| `benefits_query` | benefits, fayde, kya milega, लाभ, நன்மைகள் | Yes | No | Yes |
| `document_requirements` | documents, kagaz, dastavez, दस्तावेज़ | Yes | No | Yes |
| `application_process` | apply, register, avedan, आवेदन | Yes | Yes | Yes |
| `scheme_search` | yojana, scheme, plan, योजना, திட்டம் | Yes | No | Yes |
| `general_information` | (default) | Yes | Yes | Yes |

Relevance scoring: scheme recommendations are filtered by query word overlap with scheme name/description.

### 5. Bright Data SERP Enrichment

`brightdata_service.py` routes search queries to different government sites based on intent:

**Scheme Queries:** `site:india.gov.in OR site:data.gov.in OR site:pib.gov.in`
**Price Queries:** `site:agmarknet.gov.in OR site:enam.gov.in OR site:data.gov.in`

Price detection keywords: `mandi, market price, crop price, bhav, daam, rate today, selling price, mandi price, mandi rate, aaj ka bhav, aaj ka daam, bazaar, बाजार भाव, मंडी`

- 12-second timeout on SERP requests
- Failure is non-fatal: responses generated without web enrichment

### 6. Offline-First PWA

**Service Worker (`sw.js`):**
- Caches app shell (HTML, CSS, JS, manifest, icons)
- Network-first strategy for API calls
- Cache-first fallback for static assets

**Emergency Info Cache:**
- 6 helplines: Kisan Call Center (1800-180-1551), PM-KISAN (155261), PMFBY (1800-200-7710), Soil Health (1800-180-1551), CSC (1800-121-3468), DAO
- 5 URLs: pmkisan.gov.in, pmfby.gov.in, mkisan.gov.in, enam.gov.in, soilhealth.dac.gov.in
- Written to localStorage on page load and on reconnect

**Offline Answer Engine (`offline_answer_engine.py`):**
- Full `LANG_LABELS` for all 11 languages
- Template-based responses structured like KCC (Kisan Call Center) answers
- Keyword search over cached scheme data
- Generates localized answers with scheme details, benefits, eligibility

**Sync on Reconnect:**
1. Browser `online` event → `syncOnReconnect()`
2. Fetch `/schemes` → success: atomically replace cache / failure: keep old cache
3. Update emergency info
4. Show localized sync status (all 11 languages have `syncing` and `syncDone` i18n keys)

**Offline Feature Banner:**
- When offline, shows localized message: "Offline mode active: saved answers, scheme info, helpline numbers available"
- All 11 languages have `offlineFeatures` i18n key

### 7. GZip Compression

- Backend: `GZipMiddleware(minimum_size=500)` in `main.py`
- Proxy: `server.py` forwards `Accept-Encoding` header from client to backend
- Compression results: 67KB → 17KB for `/schemes` endpoint (74% reduction)

### 8. Multi-Language Support (11 Languages)

| Code | Language | Script |
|------|----------|--------|
| `hi` | Hindi | Devanagari |
| `en` | English | Latin |
| `bn` | Bengali | Bengali |
| `te` | Telugu | Telugu |
| `mr` | Marathi | Devanagari |
| `ta` | Tamil | Tamil |
| `gu` | Gujarati | Gujarati |
| `kn` | Kannada | Kannada |
| `ml` | Malayalam | Malayalam |
| `pa` | Punjabi | Gurmukhi |
| `or` | Odia | Odia |

**Implementation layers:**
- Frontend i18n: 23+ keys per language in `script.js` (UI labels, offline messages, sync status, error messages)
- Voice STT: `INDIAN_LANG_MAP` maps language codes to Web Speech API BCP-47 codes
- Voice TTS: Smart voice selection preferring female voices, premium/neural; rate=0.92, pitch=1.12
- AI responses: Language-specific system prompts; script-based validation after generation
- Translation fallback: deep-translator (Google) when AI responds in wrong script
- Offline templates: Full LANG_LABELS in offline_answer_engine.py

### 9. Farmer Profile System

Profile data captured via the profile drawer (slide-out panel in frontend):

| Field | Usage |
|-------|-------|
| State | State-specific scheme filtering, recommendation boosting, help center filtering |
| Crop | Injected into Azure OpenAI context for crop-specific guidance |
| Land Size | Scheme eligibility (small/marginal farmer schemes) |
| Income | Eligibility filtering, recommendation scoring |
| Occupation | Agriculture scheme boosting in RAG search |

Profile persists in the browser session and is sent with every `/query` request.

### 10. Recommendation Engine

`recommendation_engine.py` — Data-driven scheme scoring based on:
- State match (schemes for user's state ranked higher)
- Occupation match (agriculture schemes boosted for farmers)
- Income eligibility
- Crop relevance
- Query word overlap (relevance scoring in query.py)

### 11. Help Center Service

`help_center_service.py` — 50+ entries with:
- Name, type, phone, address, district
- Google Maps URL generation (`https://www.google.com/maps/search/...`)
- State-based filtering
- Included in responses for `helpline_query` and `application_process` intents

### 12. Gov Data Service

`gov_data_service.py` provides:
- data.gov.in API integration for live MSP (Minimum Support Price) data
- Agriculture statistics
- Government portal link enrichment:
  - PM-KISAN: pmkisan.gov.in
  - PMFBY: pmfby.gov.in
  - eNAM: enam.gov.in
  - Soil Health Card: soilhealth.dac.gov.in
  - KCC: pmkisan.gov.in (KCC section)
  - Maandhan: maandhan.in

### 13. Security

- **URL sanitization**: `sanitizeUrl()` on frontend validates all URLs as http/https before rendering in href attributes
- **HTML escaping**: `escapeHtml()` applied to all text before DOM insertion
- **Phone sanitization**: Non-numeric characters stripped from tel: links
- **Backend URL validation**: `_is_safe_url()` checks protocol on all returned links
- **CORS**: `allow_origins=["*"]`, `allow_credentials=False`
- **Rate limiting**: SlowAPI, 20 req/min on query endpoint
- **Anti-hallucination prompt**: AI instructed not to fabricate scheme names, amounts, dates, phone numbers
- **Error isolation**: All external calls (Azure, Bright Data, translation, gov APIs) wrapped in try/except

---

## Key Files

### Backend (`backend/app/`)
| File | Purpose |
|------|---------|
| `main.py` | FastAPI app setup, GZip + CORS middleware |
| `config.py` | pydantic-settings based configuration from env vars |
| `schemas.py` | Pydantic models: QueryRequest, ConversationMessage, SchemeRecommendation, DocLink, HelpCenter |
| `api/query.py` | Main query endpoint: orchestrates language detection, intent detection, RAG, Bright Data, recommendations, section filtering, URL sanitization |
| `api/schemes.py` | Scheme listing endpoint with type/state filtering |
| `api/help_centers.py` | Help centers endpoint with state filtering |
| `api/health.py` | Health check with loaded scheme count |
| `services/rag_engine.py` | RAG engine: keyword search, Azure OpenAI chat, conversation-aware system prompt, multi-turn message building (last 6 turns), 500-entry LRU cache, offline fallback |
| `services/intent_detection.py` | 7-intent rule-based classifier (price_query, helpline_query, eligibility_check, benefits_query, document_requirements, application_process, scheme_search) |
| `services/recommendation_engine.py` | Profile-based scheme scoring and ranking |
| `services/brightdata_service.py` | Bright Data SERP with gov site targeting + mandi price routing |
| `services/gov_data_service.py` | data.gov.in API + government portal link enrichment |
| `services/translator.py` | deep-translator (Google) with fallback handling |
| `services/offline_answer_engine.py` | Template responses in 11 languages with KCC-quality structure |
| `services/help_center_service.py` | 50+ centers + Google Maps URL generation |
| `services/scheme_loader.py` | Scheme data loading and normalization |
| `services/speech_service.py` | Azure Speech Services (TTS/STT) |
| `data/schemes.json` | 60+ government schemes with rich metadata |

### Frontend (`frontend/`)
| File | Purpose |
|------|---------|
| `index.html` | Mobile-first chat UI with Tailwind CSS, language selector, profile drawer, scheme chips, New Chat button |
| `script.js` | App logic: i18n (11 langs, 23+ keys each), conversation tracking, markdown renderer, offline scheme engine, fuzzy LRU cache, emergency cache, sync-on-reconnect, API calls, URL sanitization |
| `voice.js` | Web Speech API: STT/TTS with INDIAN_LANG_MAP, female voice preference, text chunking (180 chars), interim results |
| `style.css` | Custom styles and animations |
| `sw.js` | Service worker: app shell caching, network-first API strategy |
| `manifest.json` | PWA manifest |

### Root
| File | Purpose |
|------|---------|
| `server.py` | Entry point: starts FastAPI backend + proxy server (55s timeout) |
| `design.md` | System architecture and design document |
| `requirements.md` | Requirements specification with acceptance criteria |
| `README.md` | Project overview, setup, and usage guide |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main query. Body: `{query, language, state, occupation, income, crop, land_size, conversation_history}`. Returns: `{answer, intent, recommended_schemes, doc_links, nearest_centers}` |
| `/schemes` | GET | List schemes. Params: `type` (central/state), `state`. Returns array of scheme objects. |
| `/health` | GET | Health check. Returns: `{status, schemes_loaded}` |
| `/api/help-centers` | GET | Help centers. Params: `state`. Returns array of center objects with maps_url. |

---

## Environment Variables & Secrets

| Key | Type | Required | Purpose |
|-----|------|----------|---------|
| `AZURE_OPENAI_API_KEY` | Secret | Yes | Azure OpenAI authentication |
| `AZURE_OPENAI_ENDPOINT` | Env var | Yes | Azure OpenAI resource URL |
| `AZURE_OPENAI_DEPLOYMENT` | Env var | Yes | Model deployment name (gpt-5.3-chat) |
| `AZURE_OPENAI_API_VERSION` | Env var | No | API version (default: 2025-01-01-preview) |
| `BRIGHTDATA_API_TOKEN` | Secret | No | Bright Data SERP API authentication |
| `BRIGHTDATA_SERP_ZONE` | Env var | No | SERP zone name (serp_api1) |
| `BRIGHTDATA_DC_PASS` | Secret | No | Datacenter proxy password |
| `OFFLINE_ONLY` | Env var | No | Set `true` to disable all external API calls |
| `AZURE_TRANSLATOR_KEY` | Env var | No | Azure AI Translator (optional enhancement) |
| `AZURE_SPEECH_KEY` | Env var | No | Azure Speech Services (optional) |
| `DATA_GOV_API_KEY` | Env var | No | data.gov.in API key (optional) |

---

## Running

The "Start application" workflow runs `python server.py`.

This starts:
1. FastAPI backend on port 8000 (uvicorn)
2. Frontend proxy server on port 5000 (Python HTTPServer)

---

## Testing

```bash
cd backend && python -m pytest tests/ -v
```

**145 tests** covering:
- API endpoint behavior (query, schemes, health, help centers)
- Intent detection (all 7 intents with English, Hindi, Tamil keywords)
- Scheme loading and data normalization
- Recommendation engine scoring
- Help center service (filtering, Maps URL generation)
- RAG engine caching behavior
- Offline answer engine (template generation in 11 languages)
- Farmer profile queries (state, crop, land size, income)
- Multi-language query handling
- State scheme validation
- Edge cases and error handling
- URL sanitization
- Conversation history handling
