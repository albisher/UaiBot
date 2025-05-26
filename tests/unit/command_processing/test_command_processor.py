import pytest
from labeeb.core.command_processor import CommandProcessor, CommandResult

@pytest.fixture
def command_processor():
    """Provide a CommandProcessor instance for testing."""
    return CommandProcessor()

def test_command_processor_initialization(command_processor):
    """Test that CommandProcessor initializes correctly."""
    assert command_processor is not None
    assert hasattr(command_processor, 'commands')
    assert hasattr(command_processor, 'handlers')
    assert isinstance(command_processor.commands, dict)
    assert isinstance(command_processor.handlers, dict)

def test_command_processor_register_command(command_processor):
    """Test command registration."""
    test_command = "test_command"
    test_handler = lambda x: x
    
    command_processor.register_command(test_command, test_handler)
    assert test_command in command_processor.commands
    assert command_processor.commands[test_command] == test_handler

def test_command_processor_process_command(command_processor):
    """Test command processing."""
    test_command = "echo"
    test_handler = lambda x: f"Echo: {x}"
    
    command_processor.register_command(test_command, test_handler)
    result = command_processor.process_command(f"{test_command} Hello")
    assert isinstance(result, CommandResult)
    assert result.success
    assert result.output == "Echo: Hello"
    assert result.error is None

def test_command_processor_invalid_command(command_processor):
    """Test handling of invalid commands."""
    result = command_processor.process_command("invalid_command")
    assert isinstance(result, CommandResult)
    assert not result.success
    assert result.output is None
    assert "Unknown command" in result.error 