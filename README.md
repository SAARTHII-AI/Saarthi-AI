<div align="center">

# Saarthi AI

**Voice-first AI assistant helping Indian farmers discover and apply for government schemes — in their own language.**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--5.3-0078D4?style=flat&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![PWA](https://img.shields.io/badge/PWA-Offline_Ready-5A0FC8?style=flat&logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)
[![Languages](https://img.shields.io/badge/Languages-11_Indian-FF9933?style=flat)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*Over 100 million Indian farmers are eligible for government schemes they never hear about. Saarthi AI bridges this gap with a patient, multilingual voice assistant that speaks the way they do.*

</div>

---

## Overview

Saarthi AI is a mobile-first progressive web app that acts as a knowledgeable, patient guide for Indian farmers navigating government welfare schemes. Through natural voice conversations in 11 languages, farmers can discover schemes they qualify for, understand eligibility and required documents, and receive step-by-step application guidance — all without needing to read complex government portals or fill forms alone.

The assistant also provides live mandi (market) prices, nearby help center locations with directions, and critical agriculture helpline access even when offline.

---

## Features

### Voice-First Conversations
- Natural speech interaction via Web Speech API in all 11 supported languages
- Animated voice orb with visual feedback (listening, speaking, idle states)
- Voice interrupt: tap or type to stop speech instantly
- Optimized TTS with sentence-boundary chunking for natural delivery

### Scheme Discovery and Application Guidance
- RAG pipeline over 60+ central and state government schemes
- Profile-aware recommendations based on state, crop, land size, income, and occupation
- Multi-turn conversation memory (6 turns) for step-by-step walkthroughs
- Anti-hallucination guardrails to ensure only verified scheme information is shared

### Live Market Prices
- Real-time mandi price queries routed to eNAM and AgMarkNet portals
- Bright Data SERP enrichment for the latest data from official government sources

### Help Center Locator
- 50+ agriculture help centers with phone numbers
- Google Maps directions to the nearest center based on farmer's state

### Offline Emergency Access
- Service worker caches the full app shell for instant loading without connectivity
- 6 agriculture helplines and 5 emergency URLs stored locally
- Offline answer engine with keyword search and template responses in all 11 languages
- Automatic sync when connectivity returns (with graceful fallback to cached data)

### Security and Performance
- URL and phone number sanitization on both frontend and backend
- Rate limiting (20 req/min) and CORS configuration
- GZip compression (74% payload reduction)
- Resilient error handling on all external service calls

---

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

---

## Supported Languages

| Language | Language | Language |
|----------|----------|----------|
| Hindi | Telugu | Kannada |
| English | Marathi | Malayalam |
| Bengali | Tamil | Punjabi |
| Gujarati | Odia | |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Azure OpenAI API access (GPT-5.3 deployment)
- Bright Data API token (optional, for SERP enrichment)

### Installation

```bash
git clone https://github.com/your-username/saarthi-ai.git
cd saarthi-ai
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and provide:

| Variable | Required | Purpose |
|----------|----------|---------|
| `AZURE_OPENAI_API_KEY` | Yes | Azure OpenAI authentication |
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI resource URL |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Model deployment name |
| `BRIGHTDATA_API_TOKEN` | No | SERP enrichment for live government data |
| `OFFLINE_ONLY` | No | Set `true` to run without external APIs |

### Run

```bash
python server.py
```

Open `http://localhost:5000` in a mobile browser (or use responsive mode in desktop).

### Tests

```bash
cd backend && python -m pytest tests/ -v
```

145 tests covering API endpoints, intent detection, RAG, recommendations, offline engine, and multi-language support.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| AI / LLM | Azure OpenAI GPT-5.3 |
| Search Enrichment | Bright Data SERP API |
| Voice | Web Speech API (browser-native) |
| Frontend | Vanilla JS + Tailwind CSS (PWA) |
| Offline | Service Worker + localStorage |
| Translation | deep-translator (Google) |
| Testing | pytest |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main conversational endpoint — accepts query, language, profile, and history |
| `/schemes` | GET | List schemes, filterable by type and state |
| `/api/help-centers` | GET | Help centers with phone and directions, filterable by state |
| `/health` | GET | Health check with loaded scheme count |

---

<div align="center">

*Built to serve the farmers who feed a nation.*

</div>
