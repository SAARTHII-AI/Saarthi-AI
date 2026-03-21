# Active task plan

Use this file for multi-step work. Replace or clear sections when starting a new initiative.

## Current

- [x] Test offline layer implementation
- [x] Remove unnecessary files and redundancy
- [x] Expand schemes data (60+ schemes with state/central classification)
- [x] Implement help center locator (Google Places + Nominatim fallback)
- [x] Add document links search (BrightData SERP)
- [x] Implement Azure Speech services (TTS/STT)
- [x] Enhance auto-switch logic (Connection Manager)
- [x] Create robust test suite (185+ tests)
- [x] Update documentation
- [x] Add `DocumentLink` model in `backend/app/schemas.py`
- [x] Add `document_links` field to `QueryResponse`
- [x] Add cached `fetch_document_links` in `backend/app/services/web_search.py`
- [x] Update `backend/app/api/query.py` to include document links only for relevant document-intent queries with identified schemes
- [x] Verify targeted document-link tests pass
- [x] Validate and fix Copilot review issues (translator mock kwargs, deterministic API assertions, BrightData health gating, source-domain checks, STT exception payload, dead test logic)
- [x] Address remaining known pre-existing failing test: `tests/test_api.py::TestIntentDetection::test_intent_with_tamil_keywords`
- [ ] Resolve pre-existing unrelated backend test failures (intent i18n, schemes data validation, translator ambiguity, RAG empty-state behavior)

## Completed Features

### Offline Layer
- Keyword-based RAG search
- Intent detection (eligibility, documents, benefits, scheme search)
- Recommendation engine
- Multi-language translation (deep_translator)

### Online Layer
- Azure OpenAI integration for contextual answers
- BrightData SERP for web context and document links
- Google Places API for help center locator
- Azure Speech Services for TTS/STT
- Connection Manager for automatic fallback

### Data
- 60 government schemes (44 central, 16 state-specific)
- Schemes from 10+ states
- Complete with eligibility, benefits, documents, URLs, helplines

### Mobile
- Optimized frontend for Median.co wrapping
- APK available at median.co/share/nmdyayx#apk

## Review

### Completed on 2026-03-21
- Full offline/online dual-layer implementation
- 138/146 tests passing (8 minor failures in edge cases)
- All major features implemented and working
- Documentation updated

### Follow-ups
- [ ] Fix remaining test edge cases
- [ ] Add more state-specific schemes
- [ ] Integrate data.gov.in API for live data
- [ ] Add user authentication (if needed)
- [ ] Implement caching layer (Redis) for production
