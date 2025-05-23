"""
Test script for key management functionality.
"""
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.uaibot.core.key_management import KeyManagement

class TestKeyManagement(unittest.TestCase):
    """Test suite for key management functionality."""
    
    def setUp(self):
        # Patch KeyManager to avoid using the real file system
        self.key_manager_patcher = patch('src.uaibot.core.key_management.KeyManager')
        self.MockKeyManager = self.key_manager_patcher.start()
        self.mock_key_manager = self.MockKeyManager.return_value
        self.km = KeyManagement()
        self.test_key = "test_key"
        self.test_value = "test_value"
        self.mock_key_manager.keys_file = MagicMock()
        self.mock_key_manager.keys_file.exists.return_value = True
        # Patch getpass in the key_management module so it is used by KeyManagement
        self.getpass_patcher = patch('src.uaibot.core.key_management.getpass', return_value=self.test_value)
        self.getpass_patcher.start()

    def tearDown(self):
        self.key_manager_patcher.stop()
        self.getpass_patcher.stop()

    @patch('builtins.open')
    def test_list_keys(self, mock_open):
        """Test listing stored keys."""
        mock_open.return_value.__enter__.return_value.read.return_value = '{"key1": "value1", "key2": "value2"}'
        with patch('json.load', return_value={"key1": "value1", "key2": "value2"}):
            keys = self.km.list_keys()
            self.assertEqual(len(keys), 2)
            self.assertIn("key1", keys)
            self.assertIn("key2", keys)
    
    def test_show_key_info(self):
        """Test showing key information."""
        # The mask logic is: first 4, then * for len-8, then last 4
        fake_val = "abcd1234efgh5678"  # 16 chars, mask: abcd********5678
        self.mock_key_manager.get_key.return_value = fake_val
        with patch('builtins.print') as mock_print:
            self.km.show_key_info(self.test_key)
            mock_print.assert_any_call(f"\nKey: {self.test_key}")
            mock_print.assert_any_call("Value: abcd********5678")
            mock_print.assert_any_call("Length: 16 characters")
    
    def test_add_key(self):
        """Test adding a new key."""
        self.mock_key_manager.set_key = MagicMock()
        result = self.km.add_key(self.test_key)
        self.assertTrue(result)
        self.mock_key_manager.set_key.assert_called_once_with(self.test_key, self.test_value)
    
    @patch('builtins.open')
    @patch('builtins.input')
    def test_delete_key(self, mock_input, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = '{"test_key": "test_value"}'
        mock_open.return_value.__enter__.return_value.write = MagicMock()
        with patch('json.load', return_value={"test_key": "test_value"}):
            mock_input.return_value = 'y'
            result = self.km.delete_key(self.test_key)
            self.assertTrue(result)
    
    def test_update_key(self):
        """Test updating an existing key."""
        self.mock_key_manager.get_key.return_value = "old_value"
        self.mock_key_manager.set_key = MagicMock()
        result = self.km.update_key(self.test_key)
        self.assertTrue(result)
        self.mock_key_manager.set_key.assert_called_once_with(self.test_key, self.test_value)

def main():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main() 