#!/usr/bin/env python3
"""
System Health Check for UaiBot
- Detects OS and environment
- Checks for Ollama installation and path
- Verifies required Ollama models (e.g., gemma3:4b)
- Updates config/settings.json as needed
"""
import os
import sys
import platform
import subprocess
import json
import shutil
from pathlib import Path
import logging
from app.platform_core.platform_manager import PlatformManager

CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'settings.json'
REQUIRED_MODEL = 'gemma3:4b'

logger = logging.getLogger(__name__)

def detect_os():
    return platform.system().lower()

def find_ollama():
    # Try to find ollama in PATH
    ollama_path = shutil.which('ollama')
    if ollama_path:
        return ollama_path
    # Mac-specific locations
    for p in ['/opt/homebrew/bin/ollama', '/usr/local/bin/ollama']:
        if os.path.exists(p):
            return p
    return None

def check_ollama_installed():
    return find_ollama() is not None

def check_ollama_running():
    try:
        result = subprocess.run(['pgrep', '-f', 'ollama serve'], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def check_model_installed(model):
    ollama_path = find_ollama()
    if not ollama_path:
        return False
    try:
        result = subprocess.run([ollama_path, 'list'], capture_output=True, text=True)
        return model in result.stdout
    except Exception:
        return False

def install_model(model):
    ollama_path = find_ollama()
    if not ollama_path:
        return False
    try:
        print(f"Pulling Ollama model: {model} ...")
        subprocess.run([ollama_path, 'pull', model], check=True)
        return True
    except Exception as e:
        print(f"Error installing model {model}: {e}")
        return False

def update_config(model, base_url):
    if not CONFIG_PATH.exists():
        print(f"Config file not found: {CONFIG_PATH}")
        return False
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        config['default_ollama_model'] = model
        config['ollama_base_url'] = base_url
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Updated config/settings.json with model '{model}' and base_url '{base_url}'")
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

def check_system_health():
    """Check overall system health using the platform manager."""
    platform_manager = PlatformManager()
    platform_info = platform_manager.get_platform_info()
    
    health_status = {
        'platform': platform_info['name'],
        'system': platform_info['system'],
        'architecture': platform_info['architecture'],
        'features': {},
        'issues': []
    }
    
    # Check platform-specific features
    for feature, status in platform_info['features'].items():
        health_status['features'][feature] = {
            'enabled': status.get('enabled', False),
            'status': 'ok' if status.get('enabled', False) else 'disabled'
        }
    
    # Check paths
    for path_type, path in platform_info['paths'].items():
        if not os.path.exists(path):
            health_status['issues'].append(f"Missing {path_type} directory: {path}")
    
    return health_status

def main():
    print("\n=== UaiBot System Health Check ===\n")
    os_name = detect_os()
    print(f"Detected OS: {os_name}")

    ollama_path = find_ollama()
    if ollama_path:
        print(f"Ollama found at: {ollama_path}")
    else:
        print("Ollama is NOT installed or not in PATH.")
        print("Please install Ollama from https://ollama.com/download and ensure it is in your PATH.")
        sys.exit(1)

    if check_ollama_running():
        print("Ollama server is running.")
    else:
        print("Ollama server is NOT running. Please start it with 'ollama serve' in another terminal.")

    if check_model_installed(REQUIRED_MODEL):
        print(f"Ollama model '{REQUIRED_MODEL}' is installed.")
    else:
        print(f"Ollama model '{REQUIRED_MODEL}' is NOT installed.")
        if install_model(REQUIRED_MODEL):
            print(f"Model '{REQUIRED_MODEL}' installed successfully.")
        else:
            print(f"Failed to install model '{REQUIRED_MODEL}'.")
            sys.exit(1)

    # Update config
    base_url = 'http://localhost:11434'
    update_config(REQUIRED_MODEL, base_url)

    health = check_system_health()
    print("\nSystem Health Status:")
    print(f"Platform: {health['platform']}")
    print(f"System: {health['system']}")
    print(f"Architecture: {health['architecture']}")
    
    print("\nFeatures:")
    for feature, status in health['features'].items():
        print(f"- {feature}: {status['status']}")
    
    if health['issues']:
        print("\nIssues Found:")
        for issue in health['issues']:
            print(f"- {issue}")
    else:
        print("\nNo issues found.")

    print("\nSystem health check complete. UaiBot is ready to use!\n")

if __name__ == "__main__":
    main() 