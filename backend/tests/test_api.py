from fastapi.testclient import TestClient
from app.main import app
from app.services.intent_detection import detect_intent
from app.services.rag_engine import rag_engine

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "SaarthiAI backend is running properly."}

def test_intent_detection():
    assert detect_intent("What is the patrata for Kisan yojana?") == "eligibility_check"
    assert detect_intent("How much form do I fill? What are the documents?") == "document_requirements"
    assert detect_intent("I want to know the fayde of this scheme.") == "benefits_query"
    assert detect_intent("tell me about startup  plan") == "scheme_search"
    assert detect_intent("just looking for general instructions") == "general_information"

def test_schemes_endpoint():
    response = client.get("/schemes")
    assert response.status_code == 200
    data = response.json()
    assert "schemes" in data
    assert isinstance(data["schemes"], list)

def test_query_endpoint():
    # Make sure we have some mock data for RAG searching if tests run before real data is populated.
    if not rag_engine.schemes:
        rag_engine.schemes = [{"name": "Test Scheme", "description": "test", "eligibility": "test", "benefits": "test"}]
        # Need to build empty vector index so search does not fail if empty
        try:
            rag_engine.build_vector_index()
        except:
             pass

    request_payload = {
        "query": "मुझे किसान योजना के दस्तावेज़ बताओ",
        "language": "hi",
        "location": "UP",
        "occupation": "farmer"
    }

    response = client.post("/query", json=request_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "answer" in data
    assert "recommended_schemes" in data
    assert data["intent"] in ["scheme_search", "document_requirements"]
    
    # Must have returned recommended schemes since occupation="farmer"
    assert any([s["name"] == "PM-KISAN" for s in data["recommended_schemes"]])
