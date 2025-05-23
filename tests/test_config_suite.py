"""
Comprehensive test suite for UaiBot configuration system.
"""
import os
import json
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.uaibot.core.config_manager import ConfigManager

class TestConfigSystem(unittest.TestCase):
    """Test suite for the configuration system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_env_vars = {
            'TEST_VAR': 'test_value',
            'NESTED_VAR': 'nested_value',
            'LOG_LEVEL': 'DEBUG'
        }
        # Save original environment
        self.original_env = dict(os.environ)
        # Set test environment variables
        for key, value in self.test_env_vars.items():
            os.environ[key] = value
        self.config = ConfigManager()
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_basic_configuration(self):
        """Test basic configuration loading and access."""
        self.assertEqual(self.config.get('default_ai_provider'), 'ollama')
        self.assertEqual(self.config.get('ollama_base_url'), 'http://localhost:11434')
        self.assertEqual(self.config.get('default_ollama_model'), 'gemma3:4b')
        self.assertEqual(self.config.get('default_google_model'), 'gemini-pro')
    
    def test_environment_variable_interpolation(self):
        """Test environment variable interpolation."""
        # Test with environment variable set
        self.assertEqual(self.config.get('test_setting'), 'test_value')
        
        # Test with environment variable not set
        del os.environ['TEST_VAR']
        self.assertEqual(self.config.get('test_setting'), 'default')
        
        # Test nested interpolation
        self.assertEqual(
            self.config.get('nested_setting')['level1']['level2'],
            'nested_value'
        )
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test invalid AI provider
        with self.assertRaises(ValueError):
            self.config.set('default_ai_provider', 'invalid_provider')
            self.config.save()
        
        # Test missing required settings
        with self.assertRaises(ValueError):
            self.config.config.pop('default_ai_provider')
            self.config._validate_config()
    
    def test_configuration_persistence(self):
        """Test configuration persistence."""
        # Set a new value
        self.config.set('test_persistence', 'test_value')
        self.config.save()
        
        # Create new config instance to test loading
        new_config = ConfigManager()
        self.assertEqual(new_config.get('test_persistence'), 'test_value')
    
    def test_type_conversion(self):
        """Test type conversion of configuration values."""
        # Test boolean conversion
        self.config.set('test_bool', 'true')
        self.assertTrue(self.config.get('test_bool'))
        
        # Test integer conversion
        self.config.set('test_int', '42')
        self.assertEqual(self.config.get('test_int'), 42)
        
        # Test float conversion
        self.config.set('test_float', '3.14')
        self.assertEqual(self.config.get('test_float'), 3.14)
    
    def test_default_values(self):
        """Test default value handling."""
        # Test non-existent key with default
        self.assertEqual(self.config.get('non_existent', 'default'), 'default')
        
        # Test environment variable with default
        del os.environ['TEST_VAR']
        self.assertEqual(self.config.get('test_setting'), 'default')
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        logging_config = self.config.get('logging')
        print('DEBUG logging_config:', logging_config)
        self.assertEqual(logging_config['log_level'], 'DEBUG')  # From environment
        self.assertTrue(logging_config['log_errors'])
        self.assertTrue(logging_config['log_commands'])
    
    def test_language_support(self):
        """Test language support configuration."""
        language_support = self.config.get('language_support')
        self.assertTrue(language_support['english'])
        self.assertTrue(language_support['arabic'])
    
    def test_file_operations(self):
        """Test file operation settings."""
        file_ops = self.config.get('file_operation_settings')
        self.assertEqual(file_ops['max_results'], 20)
        self.assertEqual(file_ops['max_content_length'], 1000)
        self.assertEqual(file_ops['default_directory'], 'data')
        self.assertEqual(file_ops['test_directory'], 'tests')

def main():
    """Run the test suite."""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main() 