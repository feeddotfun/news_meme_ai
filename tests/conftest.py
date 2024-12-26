import os
import sys
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

# Add the project root directory to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# Now we can import from app
from app import create_app

@pytest.fixture
def app():
    """Create a fresh app instance for each test."""
    return create_app()

@pytest.fixture(autouse=True)
def mock_inference_client(monkeypatch):
    """Mock HuggingFace InferenceClient for all tests."""
    mock_client = MagicMock()
    
    def mock_init(self, model, token):
        self.model = model
        self.token = token
    
    monkeypatch.setattr("huggingface_hub.InferenceClient.__init__", mock_init)
    return mock_client

@pytest.fixture
def client(app):
    """Create a test client using the app fixture."""
    return TestClient(app)

@pytest.fixture
def mock_news_response():
    """Mock news response for testing."""
    return [
        {
            "title": "Bitcoin Reaches New All-Time High",
            "source": "CryptoNews"
        },
        {
            "title": "Ethereum 2.0 Launch Successful",
            "source": "BlockchainDaily"
        }
    ]

@pytest.fixture
def mock_meme_response():
    """Mock meme response for testing."""
    return [
        {
            "news": "Bitcoin Reaches New All-Time High",
            "meme": "MoonLambo (LAMBO) riding the green candles 🚀",
            "ticker": "LAMBO",
            "name": "MoonLambo",
            "image": "https://example.com/image1.jpg",
            "timestamp": "2024-12-26 10:00:00"
        }
    ]