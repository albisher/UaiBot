"""
Command Processor Test module for UaiBot.

This module provides test cases for the command processor,
including unit tests, integration tests, and performance tests.

The module includes:
- Unit tests for command processing
- Integration tests for AI model interaction
- Performance tests for command execution
- Test utilities and fixtures

Example:
    >>> python -m pytest src/uaibot/core/command_processor/command_processor_test.py -v
"""
import pytest
import logging
import json
import os
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from unittest.mock import Mock, patch
from .command_processor import CommandProcessor, CommandResult
from .command_processor_utils import validate_command, check_command_safety
from ..config_manager import ConfigManager
from ..model_manager import ModelManager
from ..ai_handler import AIHandler

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for test responses
T = TypeVar('T')
TestResponse = TypeVar('TestResponse')

@dataclass
class TestConfig:
    """Configuration for tests."""
    test_dir: str = "tests/command_processor"
    test_data_dir: str = "tests/data"
    test_results_dir: str = "tests/results"

@dataclass
class TestResult:
    """Result of a test."""
    success: bool
    message: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@pytest.fixture
def config():
    """Create a test configuration."""
    return ConfigManager()

@pytest.fixture
def model_manager(config):
    """Create a test model manager."""
    return ModelManager(config)

@pytest.fixture
def ai_handler(model_manager):
    """Create a test AI handler."""
    return AIHandler(model_manager)

@pytest.fixture
def command_processor(ai_handler):
    """Create a test command processor."""
    return CommandProcessor(ai_handler)

def test_validate_command():
    """Test command validation."""
    # Test valid command
    result = validate_command("What is the weather?")
    assert result.is_valid
    assert not result.error
    
    # Test empty command
    result = validate_command("")
    assert not result.is_valid
    assert result.error == "Empty or invalid command"
    
    # Test long command
    result = validate_command("a" * 300)
    assert not result.is_valid
    assert result.error == "Command too long"
    
    # Test invalid command structure
    result = validate_command("!@#$%^&*()")
    assert not result.is_valid
    assert result.error == "Invalid command structure"

def test_check_command_safety():
    """Test command safety checks."""
    # Test safe command
    result = check_command_safety("What is the weather?")
    assert result.is_safe
    assert not result.error
    
    # Test dangerous command (strict)
    result = check_command_safety("rm -rf /", "strict")
    assert not result.is_safe
    assert "Dangerous command pattern detected" in result.error
    
    # Test dangerous command (moderate)
    result = check_command_safety("rm -rf /", "moderate")
    assert not result.is_safe
    assert "Dangerous command pattern detected" in result.error
    
    # Test dangerous command (basic)
    result = check_command_safety("rm -rf /", "basic")
    assert not result.is_safe
    assert "Dangerous command pattern detected" in result.error

def test_process_command(command_processor):
    """Test command processing."""
    # Test valid command
    result = command_processor.process_command("What is the weather?")
    assert isinstance(result, CommandResult)
    assert result.success
    assert result.output
    assert not result.error
    
    # Test invalid command
    result = command_processor.process_command("")
    assert isinstance(result, CommandResult)
    assert not result.success
    assert not result.output
    assert result.error == "Invalid command format"
    
    # Test dangerous command
    result = command_processor.process_command("rm -rf /")
    assert isinstance(result, CommandResult)
    assert not result.success
    assert not result.output
    assert result.error == "Command failed safety check"

def test_save_command_result():
    """Test saving command results."""
    # Create test data
    command = "What is the weather?"
    result = {
        "success": True,
        "output": "The weather is sunny",
        "metadata": {
            "model": "ollama",
            "tokens": 10
        }
    }
    
    # Test saving result
    try:
        filepath = save_command_result(command, result)
        assert os.path.exists(filepath)
        
        # Verify file contents
        with open(filepath, "r") as f:
            saved_data = json.load(f)
            assert saved_data["command"] == command
            assert saved_data["result"] == result
            
    finally:
        # Clean up test file
        if os.path.exists(filepath):
            os.remove(filepath)

def test_command_processor_integration(config, model_manager, ai_handler, command_processor):
    """Test command processor integration."""
    # Test command processing with AI
    result = command_processor.process_command("What is the weather?")
    assert isinstance(result, CommandResult)
    assert result.success
    assert result.output
    assert not result.error
    
    # Test command processing with invalid AI response
    with patch.object(ai_handler, "process_prompt", side_effect=Exception("AI error")):
        result = command_processor.process_command("What is the weather?")
        assert isinstance(result, CommandResult)
        assert not result.success
        assert not result.output
        assert result.error == "AI error"

def test_command_processor_performance(command_processor):
    """Test command processor performance."""
    import time
    
    # Test processing time
    start_time = time.time()
    result = command_processor.process_command("What is the weather?")
    end_time = time.time()
    
    assert isinstance(result, CommandResult)
    assert result.success
    assert end_time - start_time < 5.0  # Should process within 5 seconds

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 