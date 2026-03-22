# Requirements Document: SaarthiAI

## Introduction

SaarthiAI is a voice-first AI assistant designed to help Indian farmers discover, understand, and apply for government schemes through natural conversations in their own language. The platform uses Retrieval-Augmented Generation (RAG) with Azure OpenAI, real-time web enrichment, and offline-first PWA architecture to serve users in low-connectivity rural environments.

The system supports 11 Indian languages (Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia) and prioritizes accessibility for users with limited digital literacy.

## Glossary

- **SaarthiAI**: The AI-powered voice assistant platform
- **Farmer Profile**: User metadata (state, crop, land size, income, occupation) used for personalization
- **RAG Engine**: Retrieval-Augmented Generation component that searches scheme data and generates AI responses
- **Intent Detection**: Rule-based classifier that routes queries to appropriate response types
- **Offline Cache**: localStorage-based storage for schemes, emergency info, and previous answers
- **Conversation History**: Multi-turn context tracking (last 6 turns) for step-by-step guidance
- **Mandi Price Routing**: Automatic redirection of price queries to agriculture market data sources
- **SERP Enrichment**: Real-time web search via Bright Data to fetch latest government information

## Requirements

### Requirement 1: Government Scheme Discovery

**User Story:** As a farmer, I want to discover government schemes relevant to my profile, so that I can access benefits available to me.

#### Acceptance Criteria

1. WHEN a farmer searches for schemes, THE system SHALL return relevant schemes based on their state, occupation, crop, land size, and income
2. WHEN displaying scheme information, THE system SHALL present eligibility criteria, benefits, required documents, and application steps in simple language
3. WHEN a farmer asks about a specific scheme, THE system SHALL provide step-by-step application guidance using multi-turn conversation
4. THE system SHALL maintain a database of 60+ government schemes (central + state-level) with rich metadata
5. WHEN scheme information is enriched via SERP, THE system SHALL only include results from verified government websites (india.gov.in, pib.gov.in, pmkisan.gov.in, etc.)

**Status:** Implemented. 60+ schemes loaded. RAG search with state/occupation boosting. Profile-based recommendation scoring. Azure OpenAI generates personalized responses.

### Requirement 2: Step-by-Step Application Guidance

**User Story:** As a farmer with limited digital literacy, I want the AI to guide me through the application process step by step, so that I can complete my application without confusion.

#### Acceptance Criteria

1. WHEN a farmer asks how to apply for a scheme, THE system SHALL break the process into numbered steps
2. THE system SHALL remember the conversation context across multiple turns (minimum 6 turns)
3. WHEN a farmer returns to continue an application, THE system SHALL pick up from where they left off
4. THE system SHALL ask follow-up questions to clarify the farmer's situation before providing guidance
5. WHEN the AI generates a response, THE system SHALL include direct links to official application portals

**Status:** Implemented. Multi-turn conversation tracking (6 turns). Conversation-aware system prompt designed as "patient village-level guide." New Chat button for fresh topics.

### Requirement 3: Voice-First Multi-Language Interface

**User Story:** As a farmer who may not be comfortable reading or typing, I want to interact with the platform using voice in my regional language, so that I can get information naturally.

#### Acceptance Criteria

1. THE system SHALL support voice input and output in 11 Indian languages: Hindi, English, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Odia
2. WHEN a user speaks a query, THE system SHALL convert speech to text using the Web Speech API with language-specific recognition
3. WHEN providing responses, THE system SHALL generate audio output using text-to-speech with female voice preference
4. THE system SHALL allow voice interrupt: tapping the mic or starting to type stops speech immediately
5. THE system SHALL auto-detect the user's language when set to "Auto Detect" mode
6. WHEN voice recognition fails, THE system SHALL provide text input as a fallback

**Status:** Implemented. All 11 languages mapped via INDIAN_LANG_MAP. Smart voice selection (female, premium/neural preferred). Text chunking at 180-char sentence boundaries. Interim results shown during recognition.

### Requirement 4: Intent-Aware Response Filtering

**User Story:** As a farmer asking about mandi prices, I want to see price-relevant information, not unrelated scheme recommendations cluttering the response.

#### Acceptance Criteria

1. THE system SHALL classify queries into 7 intents: scheme_search, eligibility_check, benefits_query, document_requirements, application_process, price_query, helpline_query
2. WHEN intent is `price_query`, THE system SHALL exclude scheme recommendations and centers, showing only relevant links (eNAM, AgMarkNet)
3. WHEN intent is `helpline_query`, THE system SHALL show nearby centers and exclude scheme recommendations and document links
4. WHEN intent is `application_process`, THE system SHALL include schemes, centers, and links
5. THE system SHALL route price queries to agriculture-specific sites (agmarknet.gov.in, enam.gov.in) instead of generic scheme sites

**Status:** Implemented. 7-intent rule-based classifier in `intent_detection.py`. Response section filtering in `query.py`. Bright Data mandi price routing in `brightdata_service.py`.

### Requirement 5: Mandi Price Information

**User Story:** As a farmer, I want to check current mandi prices for my crops, so that I can make informed selling decisions.

#### Acceptance Criteria

1. WHEN a farmer asks about crop prices (using keywords: mandi, bhav, daam, rate today, etc.), THE system SHALL search agriculture market data portals
2. THE system SHALL target official sources: agmarknet.gov.in, enam.gov.in, data.gov.in
3. WHEN live price data is unavailable, THE system SHALL provide direct links to eNAM portal with instructions on how to check prices
4. THE system SHALL NOT fabricate or hallucinate price numbers

**Status:** Implemented. Price keyword detection in English, Hindi, and mixed-language. SERP routing to mandi-specific sites. Anti-hallucination guardrails in system prompt.

### Requirement 6: Offline-First Functionality

**User Story:** As a farmer in a rural area with unreliable internet, I want to access critical information even when offline, so that connectivity issues don't prevent me from getting help.

#### Acceptance Criteria

1. THE system SHALL cache all scheme data locally via the /schemes endpoint
2. THE system SHALL store emergency information offline: 6 agriculture helplines (Kisan Call Center 1800-180-1551, PM-KISAN 155261, PMFBY 1800-200-7710, Soil Health 1800-180-1551, CSC 1800-121-3468, DAO) + 5 emergency URLs
3. WHEN offline, THE system SHALL generate responses using cached scheme data and template-based answers in all 11 languages
4. WHEN offline, THE system SHALL show a localized banner indicating available offline features
5. WHEN connectivity is restored, THE system SHALL atomically sync fresh data (keeping old cache if sync fails)
6. THE system SHALL compress API responses using GZip (target: >70% reduction)

**Status:** Implemented. Service worker caches app shell. Emergency info in localStorage. Offline answer engine with full LANG_LABELS. Sync-on-reconnect with atomic update. GZip middleware: 74% compression (67KB to 17KB).

### Requirement 7: Farmer Profile Personalization

**User Story:** As a farmer, I want the system to remember my profile details, so that recommendations are relevant to my specific situation.

#### Acceptance Criteria

1. THE system SHALL capture farmer profile: state, crop, land size, income, occupation
2. WHEN generating AI responses, THE system SHALL include profile context for personalized answers
3. THE system SHALL filter and boost scheme recommendations based on state and occupation
4. THE system SHALL display state-specific schemes when a state is selected
5. THE system SHALL provide seasonal suggestion chips based on current farming context

**Status:** Implemented. Profile drawer in frontend. Profile data sent with every query request. Azure OpenAI receives profile context. State boosting in RAG search. Recommendation scoring based on profile fields.

### Requirement 8: Nearby Help Centers

**User Story:** As a farmer needing in-person assistance, I want to find nearby help centers with phone numbers and directions, so that I can visit or call for help.

#### Acceptance Criteria

1. THE system SHALL provide 50+ help center entries with name, type, phone, address, district
2. WHEN showing centers, THE system SHALL include Google Maps links ("Open in Maps")
3. THE system SHALL filter centers by state
4. WHEN intent is `helpline_query` or `application_process`, THE system SHALL include nearby centers in the response

**Status:** Implemented. 50+ centers in help_center_service.py. Google Maps URL generation. State-based filtering. Intent-based inclusion in response sections.

### Requirement 9: Caching and Performance

**User Story:** As a platform operator, I want the system to respond quickly and minimize API costs, so that the service remains sustainable and responsive.

#### Acceptance Criteria

1. THE backend SHALL cache AI responses (500 entries, 1-hour TTL) with conversation-aware cache keys
2. THE frontend SHALL cache responses (150 entries, 14-day TTL) with fuzzy word-overlap matching
3. THE system SHALL pre-cache 8 popular farmer queries on page load
4. THE system SHALL compress responses using GZip middleware (minimum_size=500 bytes)
5. THE system SHALL rate-limit the query endpoint (20 requests/minute)
6. THE system SHALL apply request timeouts: 12s for Bright Data SERP, 55s for proxy

**Status:** Implemented. Dual-layer caching (backend LRU + frontend localStorage). Fuzzy matching with English + Hindi stop words (threshold 0.4). GZip compression. Rate limiting via SlowAPI.

### Requirement 10: Security

**User Story:** As a user, I want my interactions to be safe from injection attacks and data exposure, so that I can trust the platform.

#### Acceptance Criteria

1. THE system SHALL validate all URLs as http/https before rendering in the frontend
2. THE system SHALL sanitize phone numbers in tel: links (strip non-numeric characters)
3. THE system SHALL escape all user-facing text before DOM insertion
4. THE system SHALL configure CORS with credentials disabled when using wildcard origins
5. THE system SHALL wrap all external service calls in error handlers to prevent cascade failures
6. THE system SHALL instruct the AI not to fabricate scheme names, amounts, dates, or phone numbers

**Status:** Implemented. `sanitizeUrl()` on frontend. `_is_safe_url()` on backend. `escapeHtml()` for all text rendering. CORS with `allow_credentials=False`. Anti-hallucination system prompt. Resilient error handling throughout.

### Requirement 11: Web Search Enrichment

**User Story:** As a farmer, I want the system to include the latest information from official government sources, not just pre-loaded data.

#### Acceptance Criteria

1. THE system SHALL enrich responses with live snippets from official government websites via Bright Data SERP
2. THE system SHALL target verified domains: india.gov.in, data.gov.in, pib.gov.in, agmarknet.gov.in, enam.gov.in
3. WHEN SERP search fails or times out (12s), THE system SHALL gracefully fall back to local data without showing errors
4. THE system SHALL include relevant government portal links in responses (PM-KISAN, PMFBY, eNAM, Soil Health Card, etc.)

**Status:** Implemented. Bright Data SERP with gov site targeting. Mandi price routing. Gov portal link enrichment in gov_data_service.py. 12s timeout with graceful fallback.

### Requirement 12: AI Response Quality

**User Story:** As a farmer, I want accurate, clear responses in my language that I can trust and act on.

#### Acceptance Criteria

1. THE system SHALL respond in the user's selected language using language-specific system prompts
2. WHEN the AI response is not in the target language's script, THE system SHALL translate it using Google Translator
3. THE system SHALL verify responses contain the correct script (Devanagari for Hindi, Tamil script for Tamil, etc.)
4. THE system SHALL NOT hallucinate scheme names, monetary amounts, dates, or phone numbers
5. THE system SHALL limit response length to 1500 tokens for conciseness
6. WHEN the LLM is unavailable, THE system SHALL generate structured template responses in all 11 languages

**Status:** Implemented. Language-specific system prompts. Script-based validation. Anti-hallucination guardrails. max_completion_tokens=1500. Offline answer engine with KCC-quality templates.
