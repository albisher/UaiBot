import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "test_mode": True,
        "output_verbosity": "normal",
        "default_ai_provider": "ollama",
        "ollama_base_url": "http://localhost:11434"
    }

@pytest.fixture(scope="session")
def temp_log_dir(tmp_path_factory):
    """Create a temporary directory for test logs."""
    log_dir = tmp_path_factory.mktemp("logs")
    return log_dir

@pytest.fixture(scope="function")
def mock_platform_manager(monkeypatch):
    """Mock platform manager for testing."""
    class MockPlatformManager:
        def __init__(self):
            self.platform_supported = True
            self.platform_name = "test_platform"
        
        def initialize(self):
            pass
        
        def cleanup(self):
            pass
        
        def get_platform_info(self):
            return {
                "name": "test_platform",
                "version": "1.0.0",
                "capabilities": ["test"]
            }
    
    monkeypatch.setattr("platform_uai.platform_manager.PlatformManager", MockPlatformManager)
    return MockPlatformManager() 