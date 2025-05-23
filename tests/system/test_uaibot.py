import pytest
from uaibot.main import UaiBot
from unittest.mock import Mock, patch

def test_uaibot_initialization(mock_platform_manager, test_config):
    """Test UaiBot initialization."""
    with patch('core.utils.load_config', return_value=test_config):
        bot = UaiBot()
        assert bot.platform_manager.platform_supported
        assert bot.output_verbosity == test_config['output_verbosity']

def test_uaibot_process_single_command(mock_platform_manager, test_config):
    """Test processing a single command."""
    with patch('core.utils.load_config', return_value=test_config), \
         patch('command_processor.CommandProcessor.process_command', return_value="Test response"):
        bot = UaiBot()
        result = bot.process_single_command("test command")
        assert result == "Test response"

def test_uaibot_unsupported_platform():
    """Test behavior with unsupported platform."""
    with patch('platform_uai.platform_manager.PlatformManager') as mock_manager:
        mock_instance = mock_manager.return_value
        mock_instance.platform_supported = False
        mock_instance.platform_name = "unsupported"
        
        with pytest.raises(SystemExit):
            UaiBot()

@pytest.mark.parametrize("command,expected", [
    ("exit", None),
    ("quit", None),
    ("bye", None),
    ("test command", "Test response")
])
def test_uaibot_command_processing(mock_platform_manager, test_config, command, expected):
    """Test various command processing scenarios."""
    with patch('core.utils.load_config', return_value=test_config), \
         patch('command_processor.CommandProcessor.process_command', return_value="Test response"):
        bot = UaiBot()
        if command in ["exit", "quit", "bye"]:
            with pytest.raises(SystemExit):
                bot.process_single_command(command)
        else:
            result = bot.process_single_command(command)
            assert result == expected 