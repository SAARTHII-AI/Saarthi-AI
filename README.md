# SaarthiAI

A voice-first AI assistant that helps citizens discover and understand government schemes in Hindi and Tamil. The system works with low bandwidth and provides simplified explanations using a Retrieval-Augmented Generation (RAG) pipeline.

## Architecture Description

The system includes:

- **FastAPI Backend**: Serves the API endpoints for querying and fetching schemes.
- **RAG Engine**: Uses a local Vector Database (FAISS) and SentenceTransformers to retrieve the top matching schemes for a user's query and generate a response.
- **Intent Detection**: Rule-based detection routing queries appropriately based on keywords.
- **Recommendation Engine**: Rules for recommending extra schemes based on location, age, income.
- **Lightweight Frontend**: HTML/JS frontend using Web Speech API for offline speech-to-text and text-to-speech interaction.

## Setup Instructions

### Local Development Steps

1. Create a virtual environment and activate it:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ingest schemes text data into FAISS vector database:

```bash
python scripts/ingest_schemes.py
```

4. Run the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

5. Open `frontend/index.html` in your browser.

### Docker Deployment Guide

To run via Docker:

```bash
docker-compose up --build
```

This will start the backend service on port 8000.
