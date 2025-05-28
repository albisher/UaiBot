"""
Unit tests for the ShellTool class.
Tests both English and Arabic command execution, safety checks, and platform-specific features.
"""
import unittest
from unittest.mock import patch, MagicMock
from labeeb.core.ai.tools.shell_tool import ShellTool
from labeeb.core.exceptions import SecurityError

class TestShellTool(unittest.TestCase):
    """Test cases for ShellTool functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.shell_tool = ShellTool(safe_mode=True, debug=True)
        
    def test_init(self):
        """Test tool initialization."""
        self.assertTrue(self.shell_tool.safe_mode)
        self.assertTrue(self.shell_tool.enable_dangerous_command_check)
        self.assertTrue(self.shell_tool.debug)
        
    async def test_safe_command_execution(self):
        """Test execution of safe commands."""
        # Test English command
        result = await self.shell_tool.execute('execute', command='ls', language='en')
        self.assertEqual(result['status'], 'success')
        self.assertIsNotNone(result['message'])
        
        # Test Arabic command
        result = await self.shell_tool.execute('execute', command='ls', language='ar')
        self.assertEqual(result['status'], 'success')
        self.assertIsNotNone(result['message'])
        
    async def test_dangerous_command_detection(self):
        """Test detection of dangerous commands."""
        with self.assertRaises(SecurityError):
            await self.shell_tool.execute('execute', command='rm -rf /', language='en')
            
    async def test_unsafe_command_detection(self):
        """Test detection of commands not in safe list."""
        result = await self.shell_tool.execute('execute', command='unknown_command', language='en')
        self.assertEqual(result['status'], 'error')
        self.assertIn("not in safe list", result['message'])
        
    def test_platform_specific_processing(self):
        """Test platform-specific command processing."""
        command = "echo 'test'"
        processed = self.shell_tool._process_command(command)
        self.assertIsNotNone(processed)
        
    def test_arabic_output_formatting(self):
        """Test Arabic text output formatting."""
        arabic_text = "مرحبا بالعالم"
        formatted = self.shell_tool._format_output(arabic_text, 'ar')
        self.assertIsNotNone(formatted)
        
    def test_available_actions(self):
        """Test tool available actions reporting."""
        actions = self.shell_tool.get_available_actions()
        self.assertIn('execute', actions)
        self.assertIn('safety_check', actions)
        self.assertIn('detect_target', actions)
        self.assertIn('list_usb', actions)
        self.assertIn('browser_content', actions)
        
    @patch('labeeb.core.platform_core.platform_manager.PlatformManager')
    async def test_platform_manager_integration(self, mock_platform_manager):
        """Test integration with platform manager."""
        mock_instance = MagicMock()
        mock_instance.execute_shell_command.return_value = "test output"
        mock_platform_manager.return_value = mock_instance
        
        result = await self.shell_tool.execute('execute', command='ls', language='en')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'test output')
        
    async def test_error_handling(self):
        """Test error handling in command execution."""
        result = await self.shell_tool.execute('execute', command=None, language='en')
        self.assertEqual(result['status'], 'error')
        self.assertIn("No command provided", result['message'])
        
    async def test_unknown_action(self):
        """Test handling of unknown actions."""
        result = await self.shell_tool.execute('unknown_action', language='en')
        self.assertEqual(result['status'], 'error')
        self.assertIn("Unknown shell tool action", result['message'])
        
if __name__ == '__main__':
    unittest.main()
