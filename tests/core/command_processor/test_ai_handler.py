import pytest
from unittest.mock import Mock, patch
from app.core.ai_handler import AIHandler

@pytest.fixture
def mock_ollama_client():
    """Create a mock Ollama client for testing."""
    client = Mock()
    client.generate.return_value = {
        "response": "test_command",
        "confidence": 0.95
    }
    return client

@pytest.fixture
def mock_google_client():
    """Create a mock Google AI client for testing."""
    client = Mock()
    client.generate_content.return_value = {
        "text": "test_command",
        "confidence": 0.95
    }
    return client

def test_ai_handler_initialization_ollama():
    """Test AIHandler initialization with Ollama."""
    handler = AIHandler(model_type='ollama', ollama_base_url='http://localhost:11434')
    assert handler.model_type == 'ollama'
    assert handler.ollama_base_url == 'http://localhost:11434'

def test_ai_handler_initialization_google():
    """Test AIHandler initialization with Google AI."""
    handler = AIHandler(model_type='google', api_key='test_key', google_model_name='gemini-pro')
    assert handler.model_type == 'google'
    assert handler.google_model_name == 'gemini-pro'

def test_process_command_ollama(mock_ollama_client):
    """Test command processing with Ollama."""
    with patch('app.core.ai_handler.Ollama', return_value=mock_ollama_client):
        handler = AIHandler(model_type='ollama', ollama_base_url='http://localhost:11434')
        result = handler.process_command("test command")
        assert result["command"] == "test_command"
        assert result["confidence"] == 0.95

def test_process_command_google(mock_google_client):
    """Test command processing with Google AI."""
    with patch('google.generativeai.GenerativeModel', return_value=mock_google_client):
        handler = AIHandler(model_type='google', api_key='test_key', google_model_name='gemini-pro')
        result = handler.process_command("test command")
        assert result["command"] == "test_command"
        assert result["confidence"] == 0.95

def test_process_command_invalid_model():
    """Test command processing with invalid model type."""
    with pytest.raises(ValueError):
        AIHandler(model_type='invalid')

@pytest.mark.parametrize("command,expected_response", [
    ("list files", {"command": "ls", "confidence": 0.95}),
    ("show current directory", {"command": "pwd", "confidence": 0.95}),
    ("create new file", {"command": "touch new_file", "confidence": 0.95})
])
def test_process_command_variations(mock_ollama_client, command, expected_response):
    """Test various command processing scenarios."""
    mock_ollama_client.generate.return_value = {
        "response": expected_response["command"],
        "confidence": expected_response["confidence"]
    }
    
    with patch('app.core.ai_handler.Ollama', return_value=mock_ollama_client):
        handler = AIHandler(model_type='ollama', ollama_base_url='http://localhost:11434')
        result = handler.process_command(command)
        assert result["command"] == expected_response["command"]
        assert result["confidence"] == expected_response["confidence"] 