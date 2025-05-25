import pytest
from uaibot.core.ai_handler import AIHandler
from uaibot.core.model_manager import ModelManager
from uaibot.core.config_manager import ConfigManager

@pytest.fixture
def model_manager():
    """Provide a ModelManager instance for testing."""
    config_manager = ConfigManager()
    return ModelManager(config_manager)

@pytest.fixture
def ai_handler(model_manager):
    """Provide an AIHandler instance for testing."""
    return AIHandler(model_manager)

def test_ai_handler_initialization(ai_handler):
    """Test that AIHandler initializes correctly."""
    assert ai_handler is not None
    assert hasattr(ai_handler, 'model_manager')
    assert hasattr(ai_handler, 'prompt_config')
    assert hasattr(ai_handler, 'command_extractor')

def test_ai_handler_process_prompt(ai_handler):
    """Test basic prompt processing."""
    prompt = "echo Hello World"
    result = ai_handler.process_prompt(prompt)
    assert result is not None
    assert hasattr(result, 'text')
    assert hasattr(result, 'raw_response')
    assert hasattr(result, 'metadata')

def test_ai_handler_invalid_prompt(ai_handler):
    """Test handling of invalid prompts."""
    result = ai_handler.process_prompt("")
    assert result is not None
    assert hasattr(result, 'text')
    assert hasattr(result, 'raw_response')
    assert hasattr(result, 'metadata')
    # Optionally check for error or empty plan
    assert result.text is not None 