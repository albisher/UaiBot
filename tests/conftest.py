import pytest
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test fixtures and utilities
from labeeb.core.ai.Labeeb_agent import Labeeb
from labeeb.core.cache import Cache
from labeeb.core.auth import AuthManager
from labeeb.core.plugins import PluginManager

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
    from labeeb.core.ai_handler import AIHandler
    handler = AIHandler()
    handler.config = test_config
    return handler

@pytest.fixture
def Labeeb_agent():
    """Create a Labeeb instance for testing."""
    return Labeeb(debug=True)

@pytest.fixture
def cache():
    """Create a Cache instance for testing."""
    return Cache(cache_dir=str(Path(__file__).parent / "test_cache"))

@pytest.fixture
def auth_manager():
    """Create an AuthManager instance for testing."""
    return AuthManager(config_dir=str(Path(__file__).parent / "test_config"))

@pytest.fixture
def plugin_manager():
    """Create a PluginManager instance for testing."""
    return PluginManager(plugins_dir=str(Path(__file__).parent / "test_plugins"))

@pytest.fixture(autouse=True)
def cleanup_test_dirs():
    """Clean up test directories before and after tests."""
    test_dirs = [
        Path(__file__).parent / "test_cache",
        Path(__file__).parent / "test_config",
        Path(__file__).parent / "test_plugins"
    ]
    
    # Clean up before tests
    for dir_path in test_dirs:
        if dir_path.exists():
            for file in dir_path.glob("*"):
                if file.is_file():
                    file.unlink()
    
    yield
    
    # Clean up after tests
    for dir_path in test_dirs:
        if dir_path.exists():
            for file in dir_path.glob("*"):
                if file.is_file():
                    file.unlink() 