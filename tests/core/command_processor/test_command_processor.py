import pytest
from unittest.mock import Mock, patch
from uaibot.command_processor.CommandProcessor import CommandProcessor
from uaibot.command_processor.ShellHandler import ShellHandler

@pytest.fixture
def mock_ai_handler():
    """Create a mock AI handler for testing."""
    handler = Mock()
    handler.process_command.return_value = {
        "command": "test_command",
        "explanation": "Test explanation",
        "confidence": 0.95
    }
    return handler

@pytest.fixture
def mock_shell_handler():
    """Create a mock shell handler for testing."""
    handler = Mock()
    handler.execute_command.return_value = (0, "Command executed successfully", "")
    return handler

def test_command_processor_initialization(mock_ai_handler, mock_shell_handler):
    """Test CommandProcessor initialization."""
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    assert processor.ai_handler == mock_ai_handler
    assert processor.shell_handler == mock_shell_handler

def test_process_command_success(mock_ai_handler, mock_shell_handler):
    """Test successful command processing."""
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    result = processor.process_command("test command")
    assert "Command executed successfully" in result
    mock_ai_handler.process_command.assert_called_once_with("test command")
    mock_shell_handler.execute_command.assert_called_once()

def test_process_command_ai_error(mock_ai_handler, mock_shell_handler):
    """Test command processing with AI handler error."""
    mock_ai_handler.process_command.side_effect = Exception("AI Error")
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    result = processor.process_command("test command")
    assert "Error processing command" in result
    assert "AI Error" in result

def test_process_command_shell_error(mock_ai_handler, mock_shell_handler):
    """Test command processing with shell execution error."""
    mock_shell_handler.execute_command.return_value = (1, "", "Command failed")
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    result = processor.process_command("test command")
    assert "Command failed" in result

@pytest.mark.parametrize("command,expected_response", [
    ("ls", "Command executed successfully"),
    ("pwd", "Command executed successfully"),
    ("invalid_command", "Command failed")
])
def test_process_command_variations(mock_ai_handler, mock_shell_handler, command, expected_response):
    """Test various command processing scenarios."""
    if command == "invalid_command":
        mock_shell_handler.execute_command.return_value = (1, "", "Command not found")
    
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    result = processor.process_command(command)
    assert expected_response in result 