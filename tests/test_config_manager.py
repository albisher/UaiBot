"""
Test script for UaiBot configuration manager.
"""
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.uaibot.core.config_manager import ConfigManager

def test_config_manager():
    """Test the configuration manager functionality."""
    print("\nTesting configuration manager...")
    
    # Initialize the configuration manager
    config = ConfigManager()
    
    # Test getting configuration values
    print("\nTesting configuration values:")
    print(f"AI Provider: {config.get('default_ai_provider')}")
    print(f"Ollama URL: {config.get('ollama_base_url')}")
    print(f"Ollama Model: {config.get('default_ollama_model')}")
    print(f"Google Model: {config.get('default_google_model')}")
    
    # Test environment variable interpolation
    print("\nTesting environment variable interpolation:")
    
    # Test with environment variable set
    os.environ['TEST_VAR'] = 'test_value'
    config.set('test_setting', '${TEST_VAR:-default}')
    print(f"With TEST_VAR set: {config.get('test_setting')}")
    
    # Test with environment variable not set
    del os.environ['TEST_VAR']
    print(f"Without TEST_VAR set: {config.get('test_setting')}")
    
    # Test nested interpolation
    os.environ['NESTED_VAR'] = 'nested_value'
    config.set('nested_setting', {
        'level1': {
            'level2': '${NESTED_VAR:-default}'
        }
    })
    print(f"Nested interpolation: {config.get('nested_setting')}")
    
    # Test configuration validation
    print("\nTesting configuration validation:")
    try:
        config.set('default_ai_provider', 'invalid_provider')
        config.save()
        print("✗ Validation failed: Invalid provider accepted")
    except ValueError as e:
        print(f"✓ Validation working: {str(e)}")
    
    # Restore valid configuration
    config.set('default_ai_provider', 'ollama')
    config.save()
    
    print("\nConfiguration manager tests completed!")

if __name__ == "__main__":
    test_config_manager() 