# Architecture Update: Latency Optimization & Streaming Answers

This document outlines the major backend and frontend optimizations deployed to aggressively tackle latency bottlenecks on the `/query` endpoint.

The application has been structurally upgraded to use **SQLite** indexing and **Server-Sent Events (SSE) Streaming** to simulate real-time typing. This makes the UI feel instantly responsive, completely eliminating the "frozen" waiting period while heavy data-scraping runs in the background.

## 💡 Major Improvements
1. **Part-by-Part (Chunked) UI Tracking:** Instead of waiting up to 10 seconds for the entire RAG pipeline to finish processing, the platform now uses an asynchronous stream connection. When a user asks a question, they instantly receive the localized "draft" profile match while the rest of the Azure LLM response dynamically "types" over the screen token-by-token. 
2. **SQLite Integration:** We moved away from strictly relying on the heavy `.json` array loop in Python. We’ve added SQLAlchemy to populate a localized `saarthi.db` SQLite environment. This prepares us for advanced querying and reduces expensive RAM usage dynamically.
3. **No Offline Compromises:** The frontend's `localStorage` dictionary architecture remains 100% intact, maintaining our strict offline-capabilities rule.

## 📁 Exact Files Changed

### Dependencies
* **Files:** `requirements.txt` & `backend/requirements.txt`
* **Change:** Added `sqlalchemy` and `sse-starlette` packages.

### Database Initialization
* **Files:** 
  * `backend/app/database.py` *(New)*
  * `backend/app/models.py` *(Modified)*
  * `backend/app/main.py` *(Modified)*
* **Details:** 
  * Created the new SQLite `engine` definition and `SessionLocal` generator connecting to `saarthi.db`. 
  * Replaced the stubbed dummy model with a concrete SQLAlchemy `Scheme` table indexing specific fields like `state`, `crop`, and `benefits`.
  * Hooked `Base.metadata.create_all()` into the FastApi `@app.on_event("startup")` lifecycle so the JSON schemas securely migrate into SQL safely upon first boot.

### Streaming & RAG
* **Files:** 
  * `backend/app/services/rag_engine.py` *(Modified)*
  * `backend/app/api/query.py` *(Modified)*
* **Details:** 
  * Added a brand new `generate_answer_stream()` function. It passes `stream=True` directly into the Azure OpenAI completions API to retrieve partial string fragments.
  * Completely deleted the rigid Pydantic JSON REST return response. Refactored the core `/query` endpoint into a recursive asynchronous generator returning an `EventSourceResponse`. It pushes structured events downstream (`initial_data`, `llm_chunk`, `final_data`) sequentially.

### Frontend UI
* **Files:** `frontend/script.js` *(Modified)*
* **Details:** 
  * Completely re-engineered the `processQuery()` async function. Instead of running a blocking `await response.json()`, it actively parses the chunked TCP stream via `response.body.getReader()`. 
  * Added `createStreamingResponseContainer()` and DOM-manipulating utilities to print standard markdown text sequentially onto the `chat-box` without breaking HTML constraints.
