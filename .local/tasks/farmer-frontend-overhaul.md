# Farmer-Focused Frontend Overhaul

## What & Why
Redesign and extend the existing mobile frontend to be purpose-built for farmers: farmer-specific quick actions, a persistent online/offline indicator, smarter offline-first caching, a farmer profile stored in localStorage, and connectivity-aware messaging in Hindi/Tamil/English. The current UI is generic; farmers need immediately relevant shortcuts (PM-KISAN, crop insurance, mandi prices, soil health card) and must know at a glance whether they are getting live AI answers or cached ones.

This task is tightly coordinated with Task #1 (Integrate Azure OpenAI & Bright Data): the frontend must send the farmer's profile to the backend (crop type, state, land size) so the new AI layer can return personalised scheme results, and it must gracefully fall back to cached/offline answers when the backend is unavailable.

## Done looks like
- Header shows a real-time online/offline pill badge; switches automatically as connectivity changes
- Suggestion chips are farmer-relevant (PM-KISAN, Kisan Credit Card, Crop Insurance, Mandi Prices, Soil Health Card, PMFBY)
- When offline, the app serves matching cached answers and stamps each bot reply with a "Saved answer" badge; no silent failures
- Errors distinguish network-offline from server-error and show a friendly message in the user's chosen language
- A farmer profile drawer (accessible from the avatar button) lets the user set state, primary crop, land size, and income; this is stored in localStorage and sent with every query so the backend can personalise recommendations
- Cache is keyed by query + language + farmer profile hash and stores up to 50 entries with timestamps; cached entries older than 7 days are auto-pruned
- Seasonal suggestion chips rotate based on the current month (Kharif vs Rabi planting/harvest seasons)
- Voice mic button shows a visible "no mic" fallback UI on browsers without Web Speech API support instead of silently hiding itself
- All status messages (thinking, listening, offline, error) appear in the currently selected language
- The overall layout, color scheme, and Tailwind structure are preserved; only content and logic change

## Out of scope
- Changing the backend API contract (the frontend adapts to what Task #1 delivers)
- Native mobile app packaging (PWA manifest/service worker is acceptable but not required)
- Redesigning visual identity, colors, or typography
- Adding new backend endpoints

## Tasks
1. **Connectivity layer** — Add a global online/offline detector using the `navigator.onLine` API and `online`/`offline` events; render a status pill in the header and expose a helper function `isOnline()` used by the query logic.

2. **Farmer profile module** — Build a profile drawer (slide-up sheet) triggered by the avatar button; fields: state (dropdown of Indian states), primary crop (text or select), land size (acres, numeric), income bracket. Persist to localStorage as `saarthi_farmer_profile`. Read and merge into every outgoing query payload.

3. **Offline-first query logic** — Rewrite `processQuery` in `script.js`: check connectivity first; if offline, search the cache by query similarity (substring match on cached keys), display the best cached answer with a "Saved answer" badge, and show a clear offline message in the user's language; if online, proceed with fetch, still falling back to cache on network error.

4. **Smarter cache** — Upgrade the caching layer: key = `saarthi_${hash(query+language+profileSnapshot)}`; store `{ data, timestamp, query, language }`; cap at 50 entries (LRU eviction); prune entries older than 7 days on app start.

5. **Farmer suggestion chips** — Replace the current generic chips with six farmer-focused chips: PM-KISAN, Kisan Credit Card, Crop Insurance (PMFBY), Mandi Prices, Soil Health Card, and Free Seed Scheme. Add seasonal rotation: during June–October show Kharif-season chips (paddy, soybean); during November–March show Rabi chips (wheat, mustard).

6. **Localised status & error messages** — Create a small `i18n` map for all UI strings (thinking, listening, offline, server error, saved answer) in Hindi, Tamil, and English; wire it to the language selector so every status message renders in the chosen language.

7. **Voice mic fallback UI** — Instead of hiding the mic button on unsupported browsers, replace it with a visible disabled state (greyed-out, tooltip "Voice not supported on this browser") and show a text prompt guiding users to type.

## Relevant files
- `frontend/index.html`
- `frontend/script.js`
- `frontend/voice.js`
- `frontend/style.css`
