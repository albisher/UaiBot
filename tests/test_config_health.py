"""
Health check for UaiBot configuration system.
"""
import os
import json
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from uaibot.core.config_manager import ConfigManager
from uaibot.core.key_manager import KeyManager

def check_directory_structure():
    """Check if all required directories exist."""
    required_dirs = ['config', 'log', 'data', 'tests']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
            os.makedirs(dir_name, exist_ok=True)
    
    if missing_dirs:
        print(f"Created missing directories: {', '.join(missing_dirs)}")
    else:
        print("✓ All required directories exist")

def check_config_files():
    """Check if all required configuration files exist and are valid."""
    config_manager = ConfigManager()
    key_manager = KeyManager()
    
    # Check settings.json
    if not os.path.exists('config/settings.json'):
        print("✗ Missing settings.json")
        return False
    
    # Check user_settings.json
    if not os.path.exists('config/user_settings.json'):
        print("✗ Missing user_settings.json")
        return False
    
    # Validate JSON files
    try:
        with open('config/settings.json', 'r') as f:
            json.load(f)
        with open('config/user_settings.json', 'r') as f:
            json.load(f)
        print("✓ All configuration files contain valid JSON")
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in configuration files: {e}")
        return False
    
    # Check API keys if using Google AI
    if config_manager.get('default_ai_provider') == 'google':
        google_api_key = key_manager.ensure_key(
            'GOOGLE_API_KEY',
            "Google API key is required for using Google AI services.\n"
            "You can get an API key from: https://console.cloud.google.com/apis/credentials"
        )
        if not google_api_key:
            print("⚠ Google API key not set. Google AI services will not be available.")
        else:
            print("✓ Google API key is configured")
    
    return True

def check_file_permissions():
    """Check if configuration files have correct permissions."""
    config_files = [
        'config/settings.json',
        'config/user_settings.json',
        'config/keys/encrypted_keys.json'
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path):
            mode = os.stat(file_path).st_mode & 0o777
            if mode != 0o600:
                os.chmod(file_path, 0o600)
                print(f"Updated permissions for {file_path}")
    
    print("✓ All configuration files have correct permissions")

def main():
    """Run all health checks."""
    print("\nRunning UaiBot configuration health checks...\n")
    
    check_directory_structure()
    check_config_files()
    check_file_permissions()
    
    print("\nHealth check completed!")

if __name__ == '__main__':
    main() 