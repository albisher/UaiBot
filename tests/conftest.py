import pytest
import os
import sys

# Add src to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def test_config():
    """Provide a test configuration."""
    return {
        'model': 'test_model',
        'api_key': 'test_key',
        'temperature': 0.7,
        'max_tokens': 100
    }

@pytest.fixture
def mock_ai_handler(test_config):
    """Provide a mock AI handler for testing."""
    from uaibot.core.ai_handler import AIHandler
    handler = AIHandler()
    handler.config = test_config
    return handler 