# SaarthiAI Updated Design

## 1. Product Overview
SaarthiAI is a voice-first AI assistant for Indian farmers to discover, understand, and apply for government schemes through natural conversation. It is built as a mobile-first offline-capable PWA with multilingual support, farmer profile personalization, scheme discovery, official source enrichment, and step-by-step application guidance.

The current implementation is focused on practical, production-style behavior:
- native-script answers for readability
- romanized speech output for usable TTS
- fast backend orchestration with parallel calls
- fallback-safe behavior when any external service fails

## 2. Architecture Overview Diagram
```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ User (Mobile Browser)                                                        │
│  - voice input                                                               │
│  - text input                                                                │
│  - language selector                                                         │
│  - profile drawer                                                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      v
┌──────────────────────────────────────────────────────────────────────────────┐
│ Frontend PWA                                                                 │
│  - chat UI                                                                   │
│  - Web Speech API STT                                                        │
│  - speech synthesis TTS                                                      │
│  - local conversation history                                                │
│  - offline caches / localStorage                                             │
│  - service worker                                                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      v
┌──────────────────────────────────────────────────────────────────────────────┐
│ FastAPI + Proxy Layer                                                        │
│  - static files: / /script.js /voice.js /style.css /sw.js /manifest.json     │
│  - API routes: /query /schemes /health /help-centers                         │
│  - GZip | CORS | rate limiting                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      v
┌──────────────────────────────────────────────────────────────────────────────┐
│ Query Orchestrator                                                           │
│                                                                              │
│  Phase 1: language handling                                                  │
│   ├─ detect language                                                         │
│   ├─ translate query to English if needed                                    │
│   └─ normalize codes like hi-Latn → hi                                       │
│                                                                              │
│  Phase 2: local classification                                               │
│   └─ intent detection                                                        │
│                                                                              │
│  Phase 3: parallel retrieval                                                 │
│   ├─ RAG scheme search                                                       │
│   ├─ Bright Data SERP enrichment                                             │
│   └─ government context enrichment                                           │
│                                                                              │
│  Phase 4: parallel generation support                                        │
│   ├─ fire document link lookup alongside LLM                                 │
│   └─ build prompt context                                                    │
│                                                                              │
│  Phase 5: answer generation                                                  │
│   └─ Azure OpenAI response generation                                        │
│                                                                              │
│  Phase 6: parallel post-processing                                            │
│   ├─ answer translation                                                     │
│   ├─ recommendation translation                                             │
│   ├─ transliteration                                                        │
│   └─ final response assembly                                                │
└──────────────────────────────────────────────────────────────────────────────┘
         │                        │                         │
         │                        │                         │
         v                        v                         v
┌──────────────────┐   ┌─────────────────────┐   ┌───────────────────────────┐
│ Azure OpenAI      │   │ Azure Translator    │   │ Bright Data / Gov Sources │
│ gpt-4o-mini       │   │ detect / translate   │   │ SERP, portals, links      │
└──────────────────┘   │ transliterate        │   └───────────────────────────┘
                       └─────────────────────┘
                                      │
                                      v
┌──────────────────────────────────────────────────────────────────────────────┐
│ Response Assembly                                                            │
│  - answer                                                                   │
│  - answer_romanized                                                         │
│  - recommended_schemes                                                      │
│  - doc_links                                                                │
│  - nearest_centers                                                          │
│  - response_language                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 3. What SaarthiAI Does Well
### Core value
- Helps farmers ask questions in their own language
- Explains schemes step by step in simple language
- Suggests relevant schemes based on profile and query intent
- Shows official links, document sources, and nearby help centers
- Works even with weak or no connectivity through offline features

### Main USPs
- Voice-first UX built for low-friction use
- 11-language support with offline UI strings for the languages most Indian farmers use
- Transliteration-aware TTS so native-script responses can still be spoken naturally
- Farmer profile personalization for more relevant answers
- Parallelized backend query flow for better latency
- Offline-first PWA behavior with saved content and sync-on-reconnect
- Official government source enrichment to reduce hallucination risk

## 4. Current Implemented Architecture

### 4.1 Frontend
- Vanilla JavaScript PWA
- Mobile-first chat interface
- Voice input using Web Speech API
- Voice output using browser speech synthesis
- Language selector for 11 Indian languages
- Offline answer rendering and local cached responses
- Conversation history maintained in the browser
- Profile drawer for farmer details
- Quick action chips for common schemes and categories

### 4.2 Backend
- FastAPI backend
- API routes for query, schemes, health, and help centers
- Static frontend served through backend and proxy setup
- Rate limiting on query endpoint: 20 requests/minute
- GZip compression enabled
- Safe URL validation and response sanitization
- Environment-driven configuration using settings and secrets

### 4.3 Core Services
- `rag_engine.py` for answer generation and scheme retrieval
- `translator.py` for translation, language detection, and transliteration
- `brightdata_service.py` for SERP enrichment and document link discovery
- `gov_data_service.py` for official links and MSP context
- `help_center_service.py` for help center lookup
- `recommendation_engine.py` for scheme ranking
- `intent_detection.py` for request classification

## 5. Request Flow

### 5.1 Query pipeline
1. User submits a query in any supported language.
2. Backend detects language.
3. If needed, the query is translated to English.
4. Intent is detected locally.
5. RAG search, Bright Data search, and government enrichment run in parallel.
6. Context is built and sent to Azure OpenAI.
7. The response is generated.
8. For non-English responses:
   - the answer may be translated back into the target language
   - a romanized version may be generated for speech
9. Recommendations, document links, and help centers are assembled.
10. Response is returned as structured JSON.

### 5.2 Parallelization strategy
The backend now reduces latency by batching work that does not depend on each other:
- RAG search
- Bright Data SERP enrichment
- government enrichment
- document link lookup
- answer translation
- recommendation translation
- transliteration

### 5.3 Result handling
- Display text stays in native script when available
- Speech uses romanized text when transliteration succeeds
- If transliteration fails, the app falls back safely instead of breaking

## 6. AI and Model Stack

### 6.1 Azure OpenAI
- Current model: `gpt-4o-mini`
- Configured through `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, and `AZURE_OPENAI_API_VERSION`
- Used for scheme explanation, conversational follow-ups, and structured farmer guidance
- The system prompt forces step-by-step answers and reduces hallucination

### 6.2 Azure Translator
Azure Translator is used for:
- language detection
- translation
- transliteration

Important points:
- It supports 100+ languages overall
- SaarthiAI mainly uses it for the 11 Indian languages most relevant to farmers
- All 11 supported languages have offline UI strings, including `offlineFeatures`, `syncing`, and `syncDone`
- Transliteration is used to convert native script into Latin/romanized text for voice playback
- This makes speech usable even when native TTS voices are unavailable

### 6.3 Bright Data
Used for:
- search result enrichment
- official government snippet discovery
- document link lookup for schemes

## 7. Farmer Profile System
The farmer profile is a first-class part of the design and is passed into the backend query flow.

### Profile fields currently used
- State
- Crop
- Land size
- Income
- Occupation

### How it is used
- State improves scheme relevance and help-center filtering
- Crop improves crop-specific recommendations and query context
- Land size helps with small/marginal farmer scheme guidance
- Income helps with eligibility-aware responses
- Occupation helps rank farming-related schemes higher

### Why it matters
The assistant is not just a search bot. It personalizes recommendations and explanations based on who the farmer is and what they grow.

## 8. Multilingual Design
SaarthiAI supports 11 Indian languages:
- Hindi
- English
- Bengali
- Telugu
- Marathi
- Tamil
- Gujarati
- Kannada
- Malayalam
- Punjabi
- Odia

### Key language implementation details
- UI text is fully localized
- Voice recognition maps language codes to browser speech recognition codes
- AI responses can be generated in the user language
- Romanized transliteration is used for speech compatibility
- Offline templates also support the same language set

### Important offline coverage
Every supported language has the `offlineFeatures` i18n key so the app can clearly explain offline availability in the user’s language.
This is especially important for Indian farmers because many will rely on the app in low-connectivity situations.

## 9. Cache Layer Design
SaarthiAI uses multiple cache layers to stay fast and resilient.

### 9.1 Backend answer cache
- Located in `rag_engine.py`
- In-memory LRU-style cache
- Stores generated answers
- Uses a TTL-based expiry strategy
- Reduces repeated LLM and retrieval work for similar queries
- Cache key includes query context and profile signals

### 9.2 Frontend response cache
- Stored in browser localStorage
- Used for previously answered queries
- Helps answer repeated requests instantly
- Supports fuzzy matching so near-duplicate farmer queries can still hit cache
- Useful for slow networks and repeated scheme questions

### 9.3 Scheme cache
- Stored locally in the browser
- Holds scheme dataset fetched from the backend
- Used by the offline answer engine
- Keeps the app useful even when the network is weak or unavailable

### 9.4 Emergency Info Cache
Emergency information is preloaded locally for instant offline access.

**6 helplines:**
- Kisan Call Center — `1800-180-1551`
- PM-KISAN — `155261`
- PMFBY — `1800-200-7710`
- Soil Health — `1800-180-1551`
- CSC — `1800-121-3468`
- DAO

**5 URLs:**
- `pmkisan.gov.in`
- `pmfby.gov.in`
- `mkisan.gov.in`
- `enam.gov.in`
- `soilhealth.dac.gov.in`

This cache is used for urgent help and scheme access even when connectivity is poor.

### 9.5 Service worker cache
- Caches the app shell
- Covers HTML, CSS, JS, manifest, and icons
- Ensures the app loads quickly after first visit
- Supports offline-first behavior

### 9.6 Sync behavior
- On reconnect, the app refreshes scheme data
- Cache updates are atomic where possible
- Old cached data is kept if refresh fails
- This prevents data loss and avoids blank states

## 10. Offline-First PWA Design

### What is cached
- App shell
- CSS
- JavaScript
- Manifest
- Icons
- Scheme data
- emergency helpline info

### Offline behavior
- Saved answers can be shown without network access
- If the backend is unavailable, the app can answer from local scheme data
- On reconnect, it syncs fresh scheme data and updates caches

### User-facing offline features
- saved answers
- scheme information
- helpline numbers
- sync status messages

## 11. Data and Response Shape
The query API returns a structured response containing:
- `intent`
- `answer`
- `answer_romanized`
- `recommended_schemes`
- `response_language`
- `doc_links`
- `nearest_centers`

This keeps the frontend simple and lets voice, chat, and link rendering use different parts of the same response.

## 12. Supporting Services

### Intent detection
Rule-based intent detection is used for predictable behavior on scheme, helpline, eligibility, benefits, document, and application queries.

### Recommendation engine
Schemes are ranked using:
- state match
- occupation match
- income fit
- crop relevance
- query overlap

### Help center service
Returns nearby help centers and official contact details.

### Government data service
Adds MSP and official portal context when relevant.

## 13. Security and Reliability
- URL sanitization for external links
- HTML escaping before rendering user-facing text
- phone sanitization for tel links
- backend safe URL checks
- CORS configured for browser access
- rate limiting on `/query`
- graceful fallback on external API failure

## 14. Current Implementation Notes
- Vector search is keyword-based by design because the current data size and scheme-matching needs are better served by fast, transparent keyword retrieval without the added complexity of embeddings.
- `answer_romanized` is only returned when transliteration succeeds.
- Language codes like `hi-Latn` are normalized to simpler codes like `hi`.
- Gov links are resolved locally from keyword matching.
- The current Azure OpenAI model is `gpt-4o-mini` for lower latency.

## 15. Final Summary
SaarthiAI is currently implemented as a practical, farmer-focused assistant with three strong pillars:
1. multilingual voice-first interaction,
2. farmer profile-aware scheme guidance,
3. offline-capable, source-backed responses.

Its biggest strengths are the 11-language UX, offline support for common farmer needs, transliteration-aware speech, layered caching for responsiveness, and a backend optimized for lower latency with parallel data retrieval.
