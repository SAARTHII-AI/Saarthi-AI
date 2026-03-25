---
title: Parallelize API calls & transliterated TTS
---
# Parallelize API Calls & Transliterated TTS

  ## What & Why
  The query endpoint currently runs all external service calls sequentially (translation, Bright Data search, Gov Data API, Azure OpenAI, post-answer translation, document link search). This causes response times of 15-20+ seconds. By parallelizing independent calls, we can cut response time roughly in half.

  Additionally, browser TTS only speaks English because most devices lack Indian language voices. Instead of asking farmers to download voices, we use a transliteration approach: display the answer in the selected language's native script, but speak it using a romanized (English-letter) version that the browser's built-in English voice can pronounce naturally. This works on every device with zero setup.

  Azure Translator credentials have been provided and need to be configured as environment variables. The translator service already supports Azure Translator for translation and detection — it just needs the API key and the region set to eastasia. The transliteration feature uses the same credentials via the /transliterate endpoint.

  ## Done looks like
  - Azure Translator credentials are configured (AZURE_TRANSLATOR_KEY secret, AZURE_TRANSLATOR_REGION env var set to eastasia)
  - Query responses return noticeably faster (target: under 8-10 seconds for typical queries)
  - Bright Data search, Gov Data enrichment, and recommendation scoring run concurrently after translation
  - Post-answer document link search and gov link lookup run concurrently
  - When a non-English language is selected, the response is displayed in native script (e.g. हिंदी) but spoken aloud using the romanized transliteration (e.g. "agar aapka tractor puncture ho gaya") via the English TTS voice
  - The backend returns a new answer_romanized field alongside answer for non-English responses, using Azure Translator's transliterate endpoint
  - The frontend uses the romanized text for TTS and the native-script text for display
  - English responses continue working exactly as before (no transliteration needed)
  - Works on every phone and browser without any voice downloads

  ## Out of scope
  - Server-side Azure TTS audio generation
  - Vector search implementation
  - Streaming responses from Azure OpenAI

  ## Tasks
  1. **Configure Azure Translator credentials** — Request and set the AZURE_TRANSLATOR_KEY secret. Set AZURE_TRANSLATOR_REGION env var to eastasia. The endpoint already defaults to the correct global URL in config.py.

  2. **Parallelize pre-answer external calls** — After translating the query to English and detecting intent, run Bright Data search, Gov Data enrichment, and RAG search concurrently using asyncio.gather. These three calls are independent of each other.

  3. **Parallelize post-answer enrichment** — After generating the answer, run document link search (Bright Data), gov link lookup, and recommendation translation concurrently using asyncio.gather.

  4. **Convert blocking service calls to async** — The Bright Data service, Gov Data service, and translator service use synchronous requests library calls. Wrap them with asyncio.to_thread() so they can run in parallel without blocking the event loop.

  5. **Add transliteration to the translator service** — Add a transliterate_text method to the TranslatorService that calls Azure Translator's /transliterate endpoint to convert native-script text (Hindi, Bengali, Telugu, etc.) into Latin/Roman script. Include a mapping of language codes to Azure script codes (e.g. hi → Deva → Latn, bn → Beng → Latn, te → Telu → Latn, etc.).

  6. **Return romanized text from the query endpoint** — In the query handler, after generating and translating the final answer, call the new transliterate method for non-English responses. Add an answer_romanized field to the QueryResponse schema and populate it with the romanized version.

  7. **Update frontend TTS to use romanized text** — In the frontend, when speaking a response, use the answer_romanized field (if present) instead of the displayed answer text. Set the TTS language to English so the built-in English voice pronounces the romanized text naturally.

  ## Relevant files
  - `backend/app/api/query.py`
  - `backend/app/schemas.py`
  - `backend/app/services/brightdata_service.py`
  - `backend/app/services/gov_data_service.py`
  - `backend/app/services/translator.py`
  - `backend/app/services/rag_engine.py`
  - `backend/app/config.py`
  - `frontend/voice.js`
  - `frontend/script.js`