# Design Document: SaarthiAI

## Overview

SaarthiAI is a voice-first, multilingual AI assistant that helps Indian farmers discover and apply for government schemes through natural voice conversations. The system uses Retrieval-Augmented Generation (RAG) with Azure OpenAI, intent-aware response filtering, real-time web enrichment via Bright Data SERP, and an offline-first Progressive Web App (PWA) architecture.

The platform supports **11 Indian languages** (Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia) and is designed for low-bandwidth, intermittent connectivity environments common in rural India.

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────┐ │
│  │  Voice   │  │   Chat   │  │  Offline  │  │ Service│ │
│  │Interface │  │    UI    │  │   Cache   │  │ Worker │ │
│  │(Web      │  │(Tailwind │  │(localStorage│ │(sw.js) │ │
│  │ Speech)  │  │  CSS)    │  │+ IndexedDB)│ │        │ │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └───┬────┘ │
└───────┼──────────────┼──────────────┼────────────┼──────┘
        │              │              │            │
        └──────────────┴──────┬───────┘            │
                              │                    │
┌─────────────────────────────┼────────────────────┼──────┐
│              Proxy Server (Port 5000)            │      │
│  ┌──────────────────┐  ┌────────────────────┐    │      │
│  │ Static File      │  │ API Proxy          │    │      │
│  │ Serving           │  │ (/query, /schemes) │    │      │
│  └──────────────────┘  └─────────┬──────────┘    │      │
└──────────────────────────────────┼───────────────┘──────┘
                                   │
┌──────────────────────────────────┼──────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│                                  │                      │
│  ┌───────────────────────────────┼────────────────────┐ │
│  │              Query Orchestrator (query.py)          │ │
│  │  ┌──────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ │ │
│  │  │ Language  │ │ Intent │ │ Profile  │ │ Section │ │ │
│  │  │ Detection │ │ Detect │ │ Context  │ │ Filter  │ │ │
│  │  └──────────┘ └────────┘ └──────────┘ └─────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Service Layer                          │ │
│  │  ┌──────────────┐  ┌───────────────────┐           │ │
│  │  │  RAG Engine   │  │  Recommendation   │           │ │
│  │  │  + Azure LLM  │  │  Engine           │           │ │
│  │  │  + Conv Track  │  │  (Profile-based)  │           │ │
│  │  └──────┬───────┘  └───────────────────┘           │ │
│  │         │                                           │ │
│  │  ┌──────┴───────┐  ┌───────────────────┐           │ │
│  │  │  Bright Data │  │  Gov Data Service │           │ │
│  │  │  SERP Search │  │  (data.gov.in +   │           │ │
│  │  │  + Mandi     │  │   portal links)   │           │ │
│  │  │    Routing   │  │                   │           │ │
│  │  └──────────────┘  └───────────────────┘           │ │
│  │                                                     │ │
│  │  ┌──────────────┐  ┌───────────────────┐           │ │
│  │  │  Translator  │  │  Offline Answer   │           │ │
│  │  │  (Google)    │  │  Engine (11 langs)│           │ │
│  │  └──────────────┘  └───────────────────┘           │ │
│  │                                                     │ │
│  │  ┌──────────────┐  ┌───────────────────┐           │ │
│  │  │  Help Center │  │  Scheme Loader    │           │ │
│  │  │  Service     │  │  + Normalizer     │           │ │
│  │  │  (50+ centers│  │  (60+ schemes)    │           │ │
│  │  │  + Maps URLs)│  │                   │           │ │
│  │  └──────────────┘  └───────────────────┘           │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Middleware                              │ │
│  │  GZip Compression  │  CORS  │  Rate Limiting        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Request Flow

1. User speaks or types a query in their preferred language
2. Frontend sends query + farmer profile + conversation history to `/query`
3. **Language Detection**: Auto-detects language or uses user selection
4. **Intent Detection**: Classifies query into one of 7 intents
5. **Translation**: Translates to English for RAG search (if non-English)
6. **RAG Search**: Keyword search over 60+ schemes with state/occupation boosting
7. **Bright Data SERP**: Fetches live snippets from official gov websites (with mandi-specific routing for price queries)
8. **Azure OpenAI**: Generates conversational response using retrieved context + conversation history + farmer profile
9. **Section Filtering**: Intent determines which response sections to include (schemes, centers, links)
10. **Response**: Returns answer + filtered recommendations + doc links + nearby centers

## Core Components

### 1. Intent Detection Engine

Rule-based classifier using keyword matching in English + Hindi + Tamil + other Indian languages.

| Intent | Triggers | Response Sections |
|--------|----------|-------------------|
| `price_query` | mandi, bhav, daam, rate today, बाजार भाव | Links only (eNAM, AgMarkNet) |
| `helpline_query` | helpline, call, contact, shikayat | Centers only |
| `eligibility_check` | eligibility, patrata, who can, पात्रता | Schemes + Links |
| `benefits_query` | benefits, fayde, kya milega, लाभ | Schemes + Links |
| `document_requirements` | documents, kagaz, dastavez, दस्तावेज़ | Schemes + Links |
| `application_process` | apply, register, avedan, आवेदन | Schemes + Centers + Links |
| `scheme_search` | yojana, scheme, plan, योजना | Schemes + Links |
| `general_information` | (default fallback) | Schemes + Centers + Links |

### 2. RAG Engine with Conversation Tracking

The RAG engine is the core AI component:

**Search Phase:**
- Keyword-based search over 60+ government schemes
- State boosting: schemes matching user's state ranked higher
- Occupation boosting: farming/agriculture schemes prioritized for farmers
- Rich context builder: includes benefits, helpline numbers, application URLs, web snippets

**LLM Phase (Azure OpenAI GPT-5.3):**
- System prompt designed as a "patient village-level government scheme guide"
- Anti-hallucination guardrails: AI explicitly told not to fabricate scheme names, amounts, or dates
- Multi-turn conversation context: last 6 turns passed as chat history
- Farmer profile injected: state, crop, land size, income for personalized answers
- Language-specific prompting: AI responds directly in target language
- `max_completion_tokens=1500` (temperature not supported by this deployment)

**Caching:**
- Backend: 500-entry LRU cache, 1-hour TTL, conversation-aware cache keys
- Frontend: 150-entry LRU cache, 14-day TTL, fuzzy word-overlap matching with English + Hindi stop words

**Fallback:**
- When Azure OpenAI is unavailable, falls back to `offline_answer_engine.py`
- Template-based responses in all 11 languages with KCC-quality structured answers

### 3. Bright Data SERP Integration

Real-time web search to enrich responses with latest information:

**Scheme Queries:** Search `india.gov.in`, `data.gov.in`, `pib.gov.in`
**Price Queries:** Automatically routes to `agmarknet.gov.in`, `enam.gov.in`, `data.gov.in`

Price detection keywords: mandi, bhav, daam, rate today, market price, aaj ka bhav, बाजार भाव, मंडी

### 4. Offline-First Architecture

```
Online Mode                          Offline Mode
┌──────────────────┐                 ┌──────────────────┐
│ Azure OpenAI     │                 │ Offline Answer   │
│ + Bright Data    │                 │ Engine (templates│
│ + Gov APIs       │                 │ in 11 languages) │
│ + Translation    │                 │                  │
│                  │                 │ Cached Schemes   │
│ Full AI answers  │                 │ (localStorage)   │
│ with live data   │                 │                  │
└──────────────────┘                 │ Emergency Info   │
                                     │ (6 helplines +   │
                                     │  5 URLs)         │
                                     │                  │
                                     │ Previous Answers │
                                     │ (fuzzy cache)    │
                                     └──────────────────┘
```

**Emergency Info Cache (always available offline):**
- Kisan Call Center: 1800-180-1551
- PM-KISAN Helpline: 155261
- PMFBY Helpline: 1800-200-7710
- Soil Health Card: 1800-180-1551
- Common Service Centre: 1800-121-3468
- District Agriculture Officer (DAO)
- Emergency URLs: pmkisan.gov.in, pmfby.gov.in, mkisan.gov.in, enam.gov.in, soilhealth.dac.gov.in

**Sync on Reconnect:**
1. Browser `online` event triggers `syncOnReconnect()`
2. Fetches fresh scheme data from `/schemes`
3. Only overwrites cache on successful fetch (atomic update)
4. Updates emergency info
5. Shows localized sync status message

### 5. Multi-Language Support

All 11 languages have complete i18n coverage (23+ keys per language):

| Feature | Implementation |
|---------|---------------|
| UI Labels | Full i18n object in `script.js` with all strings localized |
| Voice Input (STT) | Web Speech API with `INDIAN_LANG_MAP` for language codes |
| Voice Output (TTS) | Smart voice selection with female preference, rate 0.92, pitch 1.12 |
| AI Responses | Language-specific system prompts; AI responds in target language |
| Offline Responses | `LANG_LABELS` in `offline_answer_engine.py` for template generation |
| Script Validation | Verifies AI response contains target language's native script characters |
| Translation Fallback | deep-translator (Google) when AI doesn't respond in correct script |

### 6. Farmer Profile System

Profile data captured via the profile drawer:
- **State**: Used for state-specific scheme filtering and recommendation boosting
- **Crop**: Injected into Azure OpenAI context for crop-specific guidance
- **Land Size**: Used for scheme eligibility (e.g., small/marginal farmer schemes)
- **Income**: Used for eligibility filtering and recommendation scoring
- **Occupation**: Boosts agriculture-related schemes in search results

### 7. GZip Compression

FastAPI `GZipMiddleware` with `minimum_size=500` bytes:
- Schemes endpoint: 67KB compressed to 17KB (74% reduction)
- Query responses: typical 40-60% reduction
- Proxy server forwards `Accept-Encoding` header for end-to-end compression

## Data Models

### Query Request
```python
class QueryRequest:
    query: str
    language: str = "auto"
    state: Optional[str]
    occupation: Optional[str]
    income: Optional[int]
    crop: Optional[str]
    land_size: Optional[str]
    conversation_history: Optional[List[ConversationMessage]]
```

### Query Response
```python
class QueryResponse:
    answer: str
    intent: str
    recommended_schemes: List[SchemeRecommendation]
    doc_links: List[DocLink]
    nearest_centers: List[HelpCenter]
```

### Conversation Message
```python
class ConversationMessage:
    role: str       # "user" or "assistant"
    content: str
```

## Security Measures

1. **URL Sanitization**: All URLs validated as `http://` or `https://` before rendering (frontend `sanitizeUrl()` + backend `_is_safe_url()`)
2. **HTML Escaping**: All user-facing text passed through `escapeHtml()` before DOM insertion
3. **Phone Sanitization**: Phone numbers in `tel:` links stripped of non-numeric characters
4. **CORS Configuration**: Wildcard origins with credentials disabled
5. **Rate Limiting**: 20 requests/minute on the query endpoint
6. **Error Isolation**: All external service calls (Azure, Bright Data, translation, gov APIs) wrapped in try/except — failures are non-fatal and gracefully degraded
7. **Anti-Hallucination**: System prompt instructs AI not to fabricate scheme names, amounts, dates, or phone numbers

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Schemes API response (compressed) | ~17KB (74% reduction) |
| Backend answer cache | 500 entries, 1-hour TTL |
| Frontend answer cache | 150 entries, 14-day TTL |
| Conversation history depth | Last 6 turns |
| LLM max tokens | 1500 completion tokens |
| Rate limit | 20 req/min per IP |
| Bright Data SERP timeout | 12 seconds |
| Proxy timeout | 55 seconds |

## Testing

145 automated tests covering:
- API endpoint behavior (query, schemes, health, help centers)
- Intent detection for all 7 intents
- Scheme loading and normalization
- Recommendation scoring
- Help center service
- RAG cache behavior
- Offline answer engine (all 11 languages)
- Farmer profile queries
- Multi-language queries
- State scheme validation
- Edge cases and error handling

```bash
cd backend && python -m pytest tests/ -v
```

## Error Handling Strategy

The system follows a "never crash" philosophy:

| Failure | Fallback |
|---------|----------|
| Azure OpenAI unavailable | Offline answer engine (template responses) |
| Bright Data SERP timeout | Skip web enrichment, use cached/local data |
| Translation failure | Return untranslated response |
| Gov API unreachable | Use pre-loaded scheme data |
| Network offline | Service worker serves cached app + localStorage data |
| Cache miss | Generate fresh response |
| Invalid URL in response | Silently filtered out by sanitizeUrl() |
