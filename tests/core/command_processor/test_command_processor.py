import pytest
from unittest.mock import Mock
from uaibot.core.command_processor import CommandProcessor

@pytest.fixture
def mock_ai_handler():
    """Create a mock AI handler."""
    handler = Mock()
    handler.process_command.return_value = {
        "command": "```shell\necho 'Test command'\n```"
    }
    return handler

@pytest.fixture
def mock_shell_handler():
    """Create a mock shell handler."""
    handler = Mock()
    handler.execute_command.return_value = "Command executed successfully"
    return handler

def test_command_processor_initialization(mock_ai_handler, mock_shell_handler):
    """Test CommandProcessor initialization."""
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    assert processor.ai_handler == mock_ai_handler
    assert processor.shell_handler == mock_shell_handler
    assert not processor.quiet_mode
    assert not processor.fast_mode

def test_process_command_success(mock_ai_handler, mock_shell_handler):
    """Test successful command processing."""
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    result = processor.process_command("echo 'test'")
    assert isinstance(result, str)
    assert "Command executed successfully" in result
    mock_ai_handler.process_command.assert_not_called()
    mock_shell_handler.execute_command.assert_called_once()

def test_process_command_ai_error(mock_ai_handler, mock_shell_handler):
    """Test command processing with AI handler error."""
    mock_ai_handler.process_command.side_effect = Exception("AI Error")
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    with pytest.raises(Exception) as excinfo:
        processor.process_command("test command")
    assert "AI Error" in str(excinfo.value)
    mock_ai_handler.process_command.assert_called_once()
    mock_shell_handler.execute_command.assert_not_called()

def test_process_command_shell_error(mock_ai_handler, mock_shell_handler):
    """Test command processing with shell execution error."""
    mock_shell_handler.execute_command.side_effect = Exception("Command failed")
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    with pytest.raises(Exception) as excinfo:
        processor.process_command("ls")
    assert "Command failed" in str(excinfo.value)
    mock_ai_handler.process_command.assert_not_called()
    mock_shell_handler.execute_command.assert_called_once()

@pytest.mark.parametrize("command,expected_contains,is_direct_shell", [
    ("ls", "Command executed successfully", True),
    ("pwd", "Command executed successfully", True),
    ("invalid_command", "No valid command found in the response", False)
])
def test_process_command_variations(mock_ai_handler, mock_shell_handler, command, expected_contains, is_direct_shell):
    """Test various command processing scenarios."""
    processor = CommandProcessor(mock_ai_handler, mock_shell_handler)
    if command == "invalid_command":
        result = processor.process_command(command)
        assert isinstance(result, str)
        assert expected_contains in result
        mock_ai_handler.process_command.assert_called_once()
        mock_shell_handler.execute_command.assert_not_called()
    else:
        result = processor.process_command(command)
        assert isinstance(result, str)
        assert expected_contains in result
        mock_ai_handler.process_command.assert_not_called()
        mock_shell_handler.execute_command.assert_called_once() 