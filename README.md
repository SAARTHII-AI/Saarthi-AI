# SaarthiAI

Voice-first assistant to help citizens discover and understand **Indian government schemes** in **Hindi**, **Tamil**, **Telugu**, and **English**. The backend uses local scheme data plus optional **Azure OpenAI**, **Azure Speech**, and **Bright Data** web enrichment (including help center lookup), with a **fully offline fallback** when credentials or network are unavailable.

## Features

### Core Features
- **Multi-language support**: Hindi, English, Tamil, Telugu with auto-detection
- **60+ Government Schemes**: Central and state-specific schemes with detailed eligibility, benefits, and required documents
- **Smart Intent Detection**: Understands eligibility, document requirements, benefits queries
- **Personalized Recommendations**: Based on occupation, age, income, and location

### Online Features (when configured)
- **AI-powered Answers**: Azure OpenAI for contextual, grounded responses
- **Document Links Search**: BrightData SERP for official document download links
- **Nearby Help Centers**: Bright Data SERP-based lookup for locating CSC Centers, e-Seva Kendras, Government Offices
- **Speech Services**: Azure Text-to-Speech and Speech-to-Text for voice interactions
- **Auto-switch**: Intelligent fallback to offline mode when services are unavailable

### Offline Features
- **Keyword-based Search**: Fast local search without external dependencies
- **Template Responses**: Bilingual answers with scheme information
- **Works without internet**: All core functionality available offline

## What's in the repo

| Part | Role |
|------|------|
| **`backend/`** | FastAPI API with `/query`, `/schemes`, `/health`, `/help-centers`, `/speech`, `/connection` endpoints |
| **`frontend/`** | Static HTML/JS with Web Speech API; API base URL is [environment-aware](frontend/script.js) |
| **`template.yaml`** | AWS SAM: container image Lambda + API Gateway |
| **`tasks/`**, **`AGENTS.md`** | Agent workflow notes for contributors |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SaarthiAI Backend                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │  Query API  │   │ Speech API  │   │Help Centers │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                  │                  │
│  ┌──────▼──────────────────▼────────────────▼──────┐           │
│  │              Connection Manager                  │           │
│  │    (Auto-switch between Online/Offline modes)   │           │
│  └──────┬──────────────────┬────────────────┬──────┘           │
│         │                  │                │                   │
│  ┌──────▼──────┐   ┌───────▼───────┐  ┌──────▼──────┐         │
│  │ Azure OpenAI│   │ BrightData    │  │ BrightData  │         │
│  │   (LLM)     │   │ (Web Search)  │  │ (Places)    │         │
│  └─────────────┘   └───────────────┘  └─────────────┘         │
│                                                                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │              Offline Layer (Always Available)    │           │
│  │  • RAG Engine (Keyword Search)                   │           │
│  │  • 60+ Schemes Data (Central + State)            │           │
│  │  • Intent Detection                              │           │
│  │  • Recommendation Engine                         │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Python 3.11+** (3.13 works locally; use 3.11 for closest parity with Docker/Lambda base images)

## Local setup

1. **Virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Dependencies** — **Canonical file is repo root `requirements.txt`.** `backend/requirements.txt` mirrors it (`-r ../requirements.txt`). Either:

   ```bash
   pip install -r requirements.txt
   # or (equivalent dependency graph)
   pip install -r backend/requirements.txt
   ```

3. **Environment**

   Copy **`.env.example`** → **`.env`** at the repo root (or under `backend/`). Fill Azure / Bright Data values as needed. See **`AGENTS.md`** for security notes.

4. **Run the API**

   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Open **http://127.0.0.1:8000/docs** for Swagger.

5. **Frontend**

   Open **`frontend/index.html`** in the browser (or serve the folder). Local file / localhost uses **`http://localhost:8000`**; other hosts use the deployed backend URL.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Main query endpoint - processes questions and returns answers |
| `/schemes` | GET | List all available government schemes |
| `/health` | GET | Health check |
| `/help-centers/nearby` | POST | Find nearby government service centers |
| `/help-centers/details/{place_id}` | GET | Get details of a specific center |
| `/speech/tts` | POST | Text-to-Speech conversion |
| `/speech/stt` | POST | Speech-to-Text transcription |
| `/speech/status` | GET | Speech service status |
| `/connection/status` | GET | Connection status and service health |
| `/connection/mode` | GET | Current connection mode (online/offline/degraded) |

## Tests

```bash
cd backend
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest tests/test_api.py        # API tests only
pytest tests/test_services.py   # Service tests only
pytest --cov=app tests/         # With coverage report
```

Tests use **`pytest-asyncio`** and mock external services to run fully offline.

## Configuration

### Required for Online Features

| Variable | Service | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI | Endpoint URL |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI | API key |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI | Model deployment name |
| `BRIGHTDATA_API_TOKEN` | BrightData | Bearer token for SERP API |
| `BRIGHTDATA_SERP_ZONE` | BrightData | SERP zone name |
| `AZURE_SPEECH_KEY` | Azure Speech | For TTS/STT |
| `AZURE_SPEECH_REGION` | Azure Speech | Region (e.g., centralindia) |

### Offline Mode

Set `OFFLINE_ONLY=true` to force offline mode (no external API calls).

## Mobile App

The frontend is optimized for mobile use. Wrap with [Median.co](https://median.co) for native app distribution:
- APK: https://median.co/share/nmdyayx#apk

## Deployment

| Target | Notes |
|--------|--------|
| **AWS Lambda (SAM)** | `sam build && sam deploy` using **`template.yaml`**. Pass stack parameters for optional Azure/Bright Data env vars (see template). |
| **Vercel** | `backend/vercel.json` + `backend/api/index.py` |
| **Docker** | From **repo root**: `docker build -f backend/Dockerfile .` · Lambda image uses root **`requirements.txt`** via **`backend/Dockerfile.lambda`**. |

## Data Sources

- **Schemes data**: `backend/app/data/schemes.json` - 60+ central and state government schemes
- **State coverage**: Maharashtra, Madhya Pradesh, Telangana, Andhra Pradesh, Uttar Pradesh, Bihar, Odisha, Jharkhand, Himachal Pradesh, Chhattisgarh
- **Data reliability**: Official sources (gov.in, nic.in) prioritized in search results

## Agent / Task Workflow

See **`AGENTS.md`** and **`tasks/agent-workflow.md`**.

## Contributing

1. Follow the workflow in `tasks/agent-workflow.md`
2. Run tests before submitting: `cd backend && pytest`
3. Update `tasks/lessons.md` with any patterns discovered

## License

MIT
