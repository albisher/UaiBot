"""
Utility functions for the UaiBot project
"""
import os
import sys
import json
import platform

def get_project_root():
    """Return the absolute path to the project root directory"""
    # Assuming this file is in the core/ directory
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_config():
    """Load the configuration from config/settings.json"""
    config_path = os.path.join(get_project_root(), "config", "settings.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found. Please create it.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode {config_path}. Please check its format.")
        return None

def save_config(config_data):
    """Save the configuration to config/settings.json"""
    config_path = os.path.join(get_project_root(), "config", "settings.json")
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def get_platform_name():
    """Return the platform name (mac, jetson, or ubuntu)"""
    system = platform.system().lower()
    
    if system == 'darwin':
        return 'mac'
    elif system == 'linux':
        # Check for Jetson-specific indicators
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().lower()
                if 'jetson' in model:
                    return 'jetson'
        except:
            pass
        # Default to Ubuntu for Linux
        return 'ubuntu'
    else:
        return None

def ensure_directory_exists(directory):
    """Ensure a directory exists, create it if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False