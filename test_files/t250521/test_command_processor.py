import unittest
import os
import tempfile
import shutil
import json
from src.core.command_processor import CommandProcessor

class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for file operations
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize command processor with AI-driven processing
        self.processor = CommandProcessor(use_regex=False)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        
    def test_file_commands(self):
        """Test file-related commands."""
        # Test create file
        result = self.processor.execute_command('create a new file called test.txt')
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists("test.txt"))
        
        # Test write file
        result = self.processor.execute_command('write "Hello World" to test.txt')
        self.assertEqual(result["status"], "success")
        
        # Test read file
        result = self.processor.execute_command('read the contents of test.txt')
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "Hello World")
        
        # Test append file
        result = self.processor.execute_command('add "!" to test.txt')
        self.assertEqual(result["status"], "success")
        
        # Test read after append
        result = self.processor.execute_command('read test.txt')
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "Hello World!")
        
        # Test list files
        result = self.processor.execute_command('show me all files')
        self.assertEqual(result["status"], "success")
        self.assertIn("test.txt", result["files"])
        
        # Test search files
        result = self.processor.execute_command('find files containing test')
        self.assertEqual(result["status"], "success")
        self.assertIn("test.txt", result["files"])
        
        # Test delete file
        result = self.processor.execute_command('delete test.txt')
        self.assertEqual(result["status"], "success")
        self.assertFalse(os.path.exists("test.txt"))
        
    def test_system_commands(self):
        """Test system-related commands."""
        # Test system status
        result = self.processor.execute_command('what is the system status')
        self.assertEqual(result["status"], "success")
        self.assertIn("system", result)
        
        # Test CPU info
        result = self.processor.execute_command('show me the CPU information')
        self.assertEqual(result["status"], "success")
        self.assertIn("cpu_percent", result)
        
        # Test memory info
        result = self.processor.execute_command('what is the memory usage')
        self.assertEqual(result["status"], "success")
        self.assertIn("total", result)
        
        # Test disk info
        result = self.processor.execute_command('show disk information')
        self.assertEqual(result["status"], "success")
        self.assertIn("partitions", result)
        
        # Test network info
        result = self.processor.execute_command('what is the network status')
        self.assertEqual(result["status"], "success")
        self.assertIn("bytes_sent", result)
        
        # Test process info
        result = self.processor.execute_command('show running processes')
        self.assertEqual(result["status"], "success")
        self.assertIn("processes", result)
        
        # Test system logs
        result = self.processor.execute_command('show system logs')
        self.assertEqual(result["status"], "success")
        self.assertIn("logs", result)
        
    def test_language_commands(self):
        """Test language-related commands."""
        # Test set language
        result = self.processor.execute_command('change language to Arabic')
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["language"], "ar")
        
        # Test detect language
        result = self.processor.execute_command('what language is this text in: Hello World')
        self.assertEqual(result["status"], "success")
        self.assertIn("detected_language", result)
        
        # Test translate
        result = self.processor.execute_command('translate Hello World to Arabic')
        self.assertEqual(result["status"], "success")
        self.assertIn("translated_text", result)
        
        # Test supported languages
        result = self.processor.execute_command('what languages are supported')
        self.assertEqual(result["status"], "success")
        self.assertIn("supported_languages", result)
        
    def test_utility_commands(self):
        """Test utility commands."""
        # Test help
        result = self.processor.execute_command('help me')
        self.assertEqual(result["status"], "success")
        self.assertIn("help", result)
        
        # Test version
        result = self.processor.execute_command('what version are you')
        self.assertEqual(result["status"], "success")
        self.assertIn("version", result)
        
        # Test status
        result = self.processor.execute_command('show me the system status')
        self.assertEqual(result["status"], "success")
        self.assertIn("system_status", result)
        
        # Test configuration
        result = self.processor.execute_command('show configuration')
        self.assertEqual(result["status"], "success")
        self.assertIn("configuration", result)
        
        # Test logs
        result = self.processor.execute_command('show logs')
        self.assertEqual(result["status"], "success")
        self.assertIn("logs", result)
        
        # Test debug mode
        result = self.processor.execute_command('turn on debug mode')
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["debug_mode"])
        
        result = self.processor.execute_command('turn off debug mode')
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["debug_mode"])
        
        # Test errors
        result = self.processor.execute_command('show errors')
        self.assertEqual(result["status"], "success")
        self.assertIn("errors", result)
        
    def test_command_history(self):
        """Test command history functionality."""
        # Execute some commands
        self.processor.execute_command('help me')
        self.processor.execute_command('show version')
        self.processor.execute_command('show status')
        
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