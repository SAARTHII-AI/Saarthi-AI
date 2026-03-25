# SaarthiAI — Technical Reference

## Overview
SaarthiAI is a voice-first AI assistant designed to help Indian farmers discover and apply for government schemes. It supports 11 Indian languages, leveraging an offline-first Progressive Web App (PWA) architecture. The project's vision is to bridge the information gap for farmers, providing step-by-step guidance through natural voice conversations, personalized scheme recommendations, and real-time information. Key capabilities include multi-turn conversation tracking, farmer profile personalization, and integration with government data sources.

## User Preferences
I prefer that the agent focuses on iterative development, delivering functional components frequently. When making significant architectural decisions or changes to core functionalities, please ask for confirmation first. I also prefer detailed explanations of complex technical choices.

## System Architecture
The application features a FastAPI backend serving both static frontend files and API routes. The frontend is a mobile-first PWA, optimized for offline use and multi-language support across 11 Indian languages.

**UI/UX Decisions:**
- Mobile-first chat interface with a user-friendly design.
- Tailwind CSS for styling.
- Language selector and profile drawer for personalization.
- Markdown rendering for rich text display in chat.
- Offline feature banner to inform users about offline capabilities.

**Technical Implementations:**
- **Azure OpenAI Integration:** Utilizes `gpt-5.3-chat` for natural language understanding and generation, with a system prompt tailored as a "patient village-level government scheme guide." It includes anti-hallucination guardrails and incorporates farmer profile context and web snippets.
- **Multi-Turn Conversation Tracking:** Both frontend and backend manage conversation history to maintain context across interactions. The backend uses the last 6 turns for context.
- **Multi-Layer Cache Architecture:** Employs a combination of backend in-memory LRU cache, frontend localStorage LRU cache with fuzzy matching, and dedicated localStorage caches for schemes and emergency information. A Service Worker caches app shell files for offline access.
- **Intent Detection & Response Filtering:** A rule-based classifier identifies 7 intents (`price_query`, `helpline_query`, `eligibility_check`, `benefits_query`, `document_requirements`, `application_process`, `scheme_search`, `general_information`) to tailor responses and data retrieval.
- **Offline-First PWA:** Implemented with a Service Worker for app shell caching and a network-first strategy for API calls. It includes an offline answer engine providing template-based responses, emergency info caching, and sync-on-reconnect functionality. PWA is fully installable on Android and iOS with proper manifest, PNG icons (72–512px), apple-touch-icon meta tags (including 180x180 for iOS), and standalone display mode. Icons are served from `/icons/` via both the proxy server and FastAPI static mount.
- **GZip Compression:** Enabled on the backend to reduce payload size for faster data transfer.
- **Parallelized API Calls:** The `/query` endpoint uses `asyncio.gather` and `asyncio.to_thread` to run RAG search, Bright Data SERP, and gov data enrichment concurrently, significantly reducing response times.
- **Transliterated TTS:** For non-English responses, Azure Translator's `/transliterate` endpoint converts native script text (e.g., Hindi Devanagari) to romanized Latin script (`answer_romanized` field). The frontend speaks this romanized text using an English TTS voice, avoiding the need for native-language voice downloads. Display still shows native script. Returns `null` when transliteration is unavailable, so frontend falls back to native-language TTS.
- **Multi-Language Support:** Comprehensive i18n for 11 Indian languages, covering UI labels, voice STT/TTS (Web Speech API with smart voice selection), AI responses (language-specific prompts), and offline templates.
- **Farmer Profile System:** Captures state, crop, land size, income, and occupation to personalize scheme recommendations and contextualize AI responses.
- **Recommendation Engine:** Scores schemes based on state, occupation, income eligibility, crop relevance, and query word overlap.
- **Help Center Service:** Provides filtered help center information with Google Maps URL generation.
- **Gov Data Service:** Integrates with data.gov.in for live MSP data and enriches responses with relevant government portal links.
- **Security:** Includes URL sanitization, HTML escaping, phone sanitization, backend URL validation, CORS, rate limiting (20 req/min on query), anti-hallucination prompts, and error isolation for external calls.

**System Design Choices:**
- **FastAPI:** Chosen for its high performance and ease of use in building APIs.
- **Pydantic:** Used for configuration and data validation.
- **Rule-based Intent Detection:** Provides predictable and controllable intent classification across multiple languages.
- **Separation of Concerns:** Services are modularized (e.g., `rag_engine.py`, `brightdata_service.py`, `recommendation_engine.py`) for maintainability.

## External Dependencies
- **Azure OpenAI:** For large language model capabilities (`gpt-5.3-chat`).
- **Bright Data:** Used for SERP (Search Engine Results Page) enrichment, targeting specific government websites for real-time information.
- **data.gov.in API:** Integrated for fetching live Minimum Support Price (MSP) data and other agricultural statistics.
- **Google Maps API:** Used for generating map URLs for help centers.
- **Web Speech API:** Utilized on the frontend for Speech-to-Text (STT) and Text-to-Speech (TTS) functionalities.
- **Azure Translator:** Used for language detection, translation, and transliteration (native script to Latin/romanized) via the Cognitive Services API. Configured with `AZURE_TRANSLATOR_KEY` secret and `AZURE_TRANSLATOR_REGION=eastasia` env var.
- **deep-translator (Google Translate):** Used as a fallback for translation in multilingual contexts.
- **SlowAPI:** For rate limiting on API endpoints.
- **uvicorn:** ASGI server for running the FastAPI application.