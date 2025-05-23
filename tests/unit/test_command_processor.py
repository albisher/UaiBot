import unittest
import os
import tempfile
import shutil
import json
from unittest.mock import Mock
from uaibot.core.command_processor import CommandProcessor

class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for file operations
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create mock handlers
        self.mock_ai_handler = Mock()
        self.mock_ai_handler.get_ai_response.return_value = "```shell\necho 'Test command'\n```"
        
        self.mock_shell_handler = Mock()
        self.mock_shell_handler.execute_command.return_value = (0, "Command executed successfully", "")
        
        # Initialize command processor with mock handlers
        self.processor = CommandProcessor(self.mock_ai_handler, self.mock_shell_handler)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        
    def test_file_commands(self):
        """Test file-related commands."""
        # Test create file
        result = self.processor.process_command('create a new file called test.txt')
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists("test.txt"))
        
        # Test write file
        result = self.processor.process_command('write "Hello World" to test.txt')
        self.assertIsInstance(result, str)
        
        # Test read file
        result = self.processor.process_command('read the contents of test.txt')
        self.assertIsInstance(result, str)
        self.assertIn("Hello World", result)
        
        # Test append file
        result = self.processor.process_command('add "!" to test.txt')
        self.assertIsInstance(result, str)
        
        # Test read after append
        result = self.processor.process_command('read test.txt')
        self.assertIsInstance(result, str)
        self.assertIn("Hello World!", result)
        
        # Test list files
        result = self.processor.process_command('show me all files')
        self.assertIsInstance(result, str)
        self.assertIn("test.txt", result)
        
        # Test search files
        result = self.processor.process_command('find files containing test')
        self.assertIsInstance(result, str)
        self.assertIn("test.txt", result)
        
        # Test delete file
        result = self.processor.process_command('delete test.txt')
        self.assertIsInstance(result, str)
        self.assertFalse(os.path.exists("test.txt"))
        
    def test_system_commands(self):
        """Test system-related commands."""
        # Test system status
        result = self.processor.process_command('what is the system status')
        self.assertIsInstance(result, str)
        self.assertIn("system", result)
        
        # Test CPU info
        result = self.processor.process_command('show me the CPU information')
        self.assertIsInstance(result, str)
        self.assertIn("cpu_percent", result)
        
        # Test memory info
        result = self.processor.process_command('what is the memory usage')
        self.assertIsInstance(result, str)
        self.assertIn("total", result)
        
        # Test disk info
        result = self.processor.process_command('show disk information')
        self.assertIsInstance(result, str)
        self.assertIn("partitions", result)
        
        # Test network info
        result = self.processor.process_command('what is the network status')
        self.assertIsInstance(result, str)
        self.assertIn("bytes_sent", result)
        
        # Test process info
        result = self.processor.process_command('show running processes')
        self.assertIsInstance(result, str)
        self.assertIn("processes", result)
        
        # Test system logs
        result = self.processor.process_command('show system logs')
        self.assertIsInstance(result, str)
        self.assertIn("logs", result)
        
    def test_language_commands(self):
        """Test language-related commands."""
        # Test set language
        result = self.processor.process_command('change language to Arabic')
        self.assertIsInstance(result, str)
        self.assertIn("ar", result)
        
        # Test detect language
        result = self.processor.process_command('what language is this text in: Hello World')
        self.assertIsInstance(result, str)
        self.assertIn("detected_language", result)
        
        # Test translate
        result = self.processor.process_command('translate Hello World to Arabic')
        self.assertIsInstance(result, str)
        self.assertIn("translated_text", result)
        
        # Test supported languages
        result = self.processor.process_command('what languages are supported')
        self.assertIsInstance(result, str)
        self.assertIn("supported_languages", result)
        
    def test_utility_commands(self):
        """Test utility commands."""
        # Test help
        result = self.processor.process_command('help me')
        self.assertIsInstance(result, str)
        self.assertIn("help", result)
        
        # Test version
        result = self.processor.process_command('what version are you')
        self.assertIsInstance(result, str)
        self.assertIn("version", result)
        
        # Test status
        result = self.processor.process_command('show me the system status')
        self.assertIsInstance(result, str)
        self.assertIn("system_status", result)
        
        # Test configuration
        result = self.processor.process_command('show configuration')
        self.assertIsInstance(result, str)
        self.assertIn("configuration", result)
        
        # Test logs
        result = self.processor.process_command('show logs')
        self.assertIsInstance(result, str)
        self.assertIn("logs", result)
        
        # Test debug mode
        result = self.processor.process_command('turn on debug mode')
        self.assertIsInstance(result, str)
        self.assertIn("debug_mode", result)
        
        result = self.processor.process_command('turn off debug mode')
        self.assertIsInstance(result, str)
        self.assertIn("debug_mode", result)
        
        # Test errors
        result = self.processor.process_command('show errors')
        self.assertIsInstance(result, str)
        self.assertIn("errors", result)
        
    def test_command_history(self):
        """Test command history functionality."""
        # Execute some commands
        self.processor.process_command('help me')
        self.processor.process_command('show version')
        self.processor.process_command('show status')
        
        # Check command history
        history = self.processor.get_command_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], 'help me')
        self.assertEqual(history[1], 'show version')
        self.assertEqual(history[2], 'show status')
        
        # Check current command
        self.assertEqual(self.processor.get_current_command(), 'show status')

if __name__ == '__main__':
    unittest.main() 