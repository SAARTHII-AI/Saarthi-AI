import pytest
# Dummy placeholder tests for service level testing
# The actual logic is mostly tested through the endpoints in test_api.py

def test_recommendation_engine():
    from backend.app.services.recommendation_engine import recommend_schemes
    
    user_data = {"occupation": "student", "age": 20}
    results = recommend_schemes(user_data)
    
    assert isinstance(results, list)
    assert any([r["name"] == "Digital India" for r in results])
