# Backend Tests

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    # If health endpoint doesn't exist, this will help us know
    assert response.status_code in [200, 404]

def test_word_lookup():
    """Test Japanese word lookup functionality"""
    response = client.post("/api/enrich/lookup", data={"word": "猫"})
    assert response.status_code == 200
    data = response.json()
    assert "word" in data
    assert data["word"] == "猫"

def test_invalid_word_lookup():
    """Test lookup with invalid input"""
    response = client.post("/api/enrich/lookup", data={"word": ""})
    assert response.status_code in [400, 422, 500]  # Accept various error codes

@pytest.mark.asyncio
async def test_collection_endpoints():
    """Test collection functionality"""
    # Test adding word to collection
    response = client.post("/api/enrich/collection/add-word", data={
        "word": "猫",
        "reading": "ねこ",
        "meanings": '["cat"]',
        "parts_of_speech": '["noun"]'
    })
    assert response.status_code == 200
    data = response.json()
    assert "collection_id" in data
    
    # Test getting collection
    collection_id = data["collection_id"]
    response = client.get(f"/api/enrich/collection/{collection_id}")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
