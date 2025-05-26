"""
Unit tests for the Labeeb agent implementation.
"""

import pytest
from app.core.ai.agents.labeeb_agent import LabeebAgent
from app.platform_core.platform_manager import PlatformManager

@pytest.fixture
def agent():
    """Create a test instance of LabeebAgent"""
    return LabeebAgent()

@pytest.fixture
def platform_manager():
    """Create a test instance of PlatformManager"""
    return PlatformManager()

def test_agent_initialization(agent):
    """Test that the agent initializes correctly"""
    assert agent is not None
    assert agent.platform_manager is not None
    assert agent.platform_info is not None
    assert agent.handlers is not None

def test_agent_process_command(agent):
    """Test command processing"""
    result = agent.process_command("test command")
    assert result is not None
    assert 'status' in result
    assert 'platform' in result
    assert 'command' in result

def test_agent_info(agent):
    """Test agent information retrieval"""
    info = agent.get_agent_info()
    assert info is not None
    assert info['name'] == 'Labeeb'
    assert 'platform' in info
    assert 'version' in info
    assert 'features' in info
    assert 'handlers' in info
