# SaarthiAI

A voice-first AI assistant helping Indian farmers discover and **apply for** government schemes step-by-step through natural voice conversations. Built with FastAPI, Azure OpenAI (GPT-5.3), and a mobile-first PWA frontend supporting **11 Indian languages**.

## What It Does

SaarthiAI acts as a patient, knowledgeable village-level guide that helps farmers:
- **Discover** relevant government schemes based on their profile (state, crop, land size, income)
- **Understand** eligibility criteria, benefits, and required documents in their own language
- **Apply** step-by-step with guided instructions, picking up where they left off across conversations
- **Check mandi prices** with live data from eNAM and AgMarkNet portals
- **Find help centers** with phone numbers and Google Maps directions
- **Access emergency info offline** including agriculture helplines and critical URLs

## Supported Languages

Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia

## Architecture

```
                    +-------------------+
                    |   Mobile Browser  |
                    |   (PWA + Voice)   |
                    +--------+----------+
                             |
                    +--------v----------+
                    |   Proxy Server    |
                    |   (Port 5000)     |
                    +--------+----------+
                             |
              +--------------+--------------+
              |                             |
    +---------v---------+     +-------------v-------------+
    | Static Frontend   |     |    FastAPI Backend         |
    | HTML/CSS/JS       |     |    (Port 8000)             |
    | Service Worker    |     +---+---+---+---+---+---+----+
    | Offline Cache     |         |   |   |   |   |   |
    +-------------------+         |   |   |   |   |   |
                                  v   v   v   v   v   v
                            +-----+---+---+---+---+---+------+
                            | Intent  | RAG  | Bright | Gov  |
                            | Detect  | +LLM | Data   | APIs |
                            |         |      | SERP   |      |
                            +---------+------+--------+------+
                                  |
                     +------------+------------+
                     |                         |
              +------v------+          +-------v-------+
              | Azure OpenAI|          |  Offline      |
              | GPT-5.3     |          |  Answer Engine|
              +-------------+          +---------------+
```

## Key Features

### Voice-First Interaction
- Web Speech API for speech-to-text and text-to-speech in all 11 languages
- Animated voice orb (green pulse = listening, purple glow = speaking)
- Voice interrupt: tap mic or start typing to stop speech instantly
- Smart voice selection: prefers female, premium/neural voices for clarity
- Text chunking: splits long responses at sentence boundaries for natural TTS

### AI-Powered Responses (RAG Pipeline)
- **Azure OpenAI GPT-5.3** with anti-hallucination guardrails in system prompt
- Keyword-based RAG search with state/occupation boosting over 60+ government schemes
- **Multi-turn conversation tracking**: AI remembers context across 6 turns, guides step-by-step
- **Intent-aware filtering**: 7 intents route queries to show only relevant response sections
- **Bright Data SERP enrichment**: fetches latest info from official government websites
- **Mandi price routing**: price queries automatically target agmarknet.gov.in and enam.gov.in
- Conversation-aware caching (500 entries, 1-hour TTL)

### Farmer Profile Personalization
- Profile drawer captures state, crop, land size, income, occupation
- Profile data sent to Azure OpenAI for personalized scheme recommendations
- State-specific scheme filtering (central + state-level schemes)
- Relevance scoring for recommendations based on query word overlap

### Offline-First PWA
- Service worker caches app shell for instant loading
- **Emergency info cache**: 6 agriculture helplines + 5 emergency URLs in localStorage
- **Offline answer engine**: keyword search over cached schemes with template responses in all 11 languages
- **Sync on reconnect**: atomically refreshes scheme data when internet returns (keeps old cache on failure)
- **GZip compression**: 74% reduction (67KB to 17KB for schemes endpoint)
- Localized offline feature banner in all 11 languages

### Security
- URL sanitization on both frontend and backend (validates http/https before rendering)
- Phone number sanitization in tel: links
- CORS properly configured
- Rate limiting (20 requests/minute on query endpoint)
- All external service calls wrapped in try/except for resilient error handling

## Project Structure

```
saarthi-ai/
├── server.py                          # Entry point: starts backend + proxy
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app with GZip + CORS middleware
│   │   ├── config.py                  # Environment-based settings (pydantic)
│   │   ├── schemas.py                 # Request/response Pydantic models
│   │   ├── api/
│   │   │   ├── query.py               # Main query endpoint (orchestrator)
│   │   │   ├── schemes.py             # Scheme listing endpoint
│   │   │   ├── help_centers.py        # Help centers endpoint
│   │   │   └── health.py              # Health check endpoint
│   │   ├── services/
│   │   │   ├── rag_engine.py          # RAG + Azure OpenAI + conversation tracking
│   │   │   ├── intent_detection.py    # 7-intent rule-based classifier
│   │   │   ├── recommendation_engine.py # Profile-based scheme scoring
│   │   │   ├── brightdata_service.py  # SERP enrichment + mandi price routing
│   │   │   ├── gov_data_service.py    # data.gov.in API + gov portal links
│   │   │   ├── translator.py          # Google Translator with fallback
│   │   │   ├── offline_answer_engine.py # Template responses in 11 languages
│   │   │   ├── help_center_service.py # 50+ centers + Google Maps URLs
│   │   │   ├── scheme_loader.py       # Scheme data normalization
│   │   │   └── speech_service.py      # Azure Speech Services (TTS/STT)
│   │   └── data/
│   │       └── schemes.json           # 60+ government schemes dataset
│   └── tests/
│       ├── test_api.py                # API endpoint tests
│       └── test_services.py           # Service integration tests
├── frontend/
│   ├── index.html                     # Mobile-first chat UI (Tailwind CSS)
│   ├── script.js                      # App logic, i18n, caching, API calls
│   ├── voice.js                       # Web Speech API integration
│   ├── style.css                      # Custom styles
│   ├── sw.js                          # Service worker (offline PWA)
│   └── manifest.json                  # PWA manifest
├── design.md                          # System design document
├── requirements.md                    # Requirements specification
└── replit.md                          # Technical reference (for developers)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main query endpoint. Accepts query, language, farmer profile, conversation history. Returns AI answer, scheme recommendations, document links, nearby centers. |
| `/schemes` | GET | List all schemes. Filter by `type` (central/state) and `state`. |
| `/health` | GET | Health check with loaded scheme count. |
| `/api/help-centers` | GET | Help centers with phone numbers and Google Maps URLs. Filter by `state`. |

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `AZURE_OPENAI_API_KEY` | Yes | Azure OpenAI authentication |
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI resource URL |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Model deployment name (gpt-5.3-chat) |
| `AZURE_OPENAI_API_VERSION` | No | API version (default: 2025-01-01-preview) |
| `BRIGHTDATA_API_TOKEN` | No | Bright Data SERP API authentication |
| `BRIGHTDATA_SERP_ZONE` | No | SERP zone name |
| `BRIGHTDATA_DC_PASS` | No | Datacenter proxy password |
| `OFFLINE_ONLY` | No | Set `true` to disable all external API calls |

## Setup & Running

### On Replit
The "Start application" workflow runs `python server.py`, which starts both the FastAPI backend (port 8000) and the frontend proxy server (port 5000).

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (copy `.env.example` to `.env` and fill in values).

3. Start the application:
```bash
python server.py
```

4. Open `http://localhost:5000` in your browser.

## Testing

```bash
cd backend && python -m pytest tests/ -v
```

**145 tests** covering: API endpoints, intent detection, scheme loading, recommendations, help centers, RAG cache, offline answer engine, farmer profile queries, multi-language support, state scheme validation, edge cases, and error handling.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI (Python) |
| AI/LLM | Azure OpenAI GPT-5.3 |
| Web Search | Bright Data SERP API |
| Translation | deep-translator (Google) |
| Frontend | Vanilla HTML/CSS/JS + Tailwind CSS |
| Voice | Web Speech API (browser-native) |
| Caching | In-memory LRU (backend) + localStorage (frontend) |
| Compression | GZip middleware |
| Offline | Service Worker + localStorage |
| Testing | pytest (145 tests) |
