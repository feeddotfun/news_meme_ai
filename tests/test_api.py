import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_version(client):
    """Test the version endpoint."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert "version" in response.json()

@pytest.mark.asyncio
async def test_get_news(client, mock_news_response):
    """Test the news endpoint."""
    with patch('app.services.news_service.NewsService.fetch_news', 
               return_value=mock_news_response):
        response = client.get("/api/v1/news")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Bitcoin Reaches New All-Time High"

@pytest.mark.asyncio
async def test_get_news_empty(client):
    """Test the news endpoint with empty response."""
    with patch('app.services.news_service.NewsService.fetch_news', 
               return_value=None):
        response = client.get("/api/v1/news")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_generate_memes(client, mock_news_response, mock_meme_response):
    """Test the meme generation endpoint."""
    with patch('app.services.news_service.NewsService.fetch_news',
               return_value=mock_news_response), \
         patch('app.services.news_to_ai_service.NewsToAIService.process_news_batch',
               return_value=mock_meme_response):
        response = client.get("/api/v1/memes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ticker"] == "LAMBO"

@pytest.mark.asyncio
async def test_generate_memes_no_news(client):
    """Test meme generation with no news available."""
    with patch('app.services.news_service.NewsService.fetch_news',
               return_value=None):
        response = client.get("/api/v1/memes")
        assert response.status_code == 404

def test_cors_middleware(client):
    """Test CORS middleware configuration."""
    response = client.options(
        "/api/v1/health",
        headers={
            "origin": "http://localhost:3000",
            "access-control-request-method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

def test_timing_middleware(client):
    """Test timing middleware."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    assert float(response.headers["x-process-time"]) >= 0

def test_internal_only_middleware_localhost(client):
    """Test internal only middleware with localhost."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

def test_internal_only_middleware_external(client):
    """Test internal only middleware with external IP."""
    class MockClient:
        def __init__(self, host):
            self.host = host

    with patch('starlette.requests.HTTPConnection.client', 
              new_callable=lambda: MockClient("8.8.8.8")):
        with pytest.raises(HTTPException) as exc_info:
            client.get("/api/v1/health")
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Access denied"