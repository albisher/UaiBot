"""
Platform-specific utility functions for Labeeb.

This module provides various platform-specific utility functions used throughout the application.
"""
import os
# import platform  # No longer needed
from pathlib import Path
import json
import sys
import subprocess
from labeeb.core.platform_core.platform_utils import get_platform_name, is_windows, is_mac, is_linux

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None

def get_descriptive_platform_name():
    """
    Get a more descriptive name for the current platform.
    
    Returns:
        str: Descriptive platform name
    """
    system = get_platform_name().lower()
    system_info = platform.uname()
    
    if system == 'darwin':
        mac_ver = platform.mac_ver()[0]
        # Map major version to OS name
        macos_names = {
            "10.15": "Catalina",
            "11.": "Big Sur",
            "12.": "Monterey",
            "13.": "Ventura",
            "14.": "Sonoma",
            "15.": "Sequoia",
        }
        
        for ver, name in macos_names.items():
            if mac_ver.startswith(ver):
                return f"macOS {name} ({mac_ver})"
        # Default case
        return f"macOS ({mac_ver})"
        
    elif system == 'linux':
        # Try to get distribution info
        try:
            import distro
            dist_name, version, _ = distro.linux_distribution()
            if dist_name:
                return f"{dist_name} {version}"
        except ImportError:
            pass
            
        # Fallback to reading release files
        release_files = [
            "/etc/os-release",
            "/etc/lsb-release",
            "/etc/debian_version",
            "/etc/redhat-release",
        ]
        
        for rf in release_files:
            if os.path.isfile(rf):
                with open(rf, 'r') as f:
                    content = f.read()
                    if 'NAME=' in content and 'VERSION=' in content:
                        try:
                            name = content.split('NAME=')[1].split('\n')[0].strip('"\'')
                            version = content.split('VERSION=')[1].split('\n')[0].strip('"\'')
                            return f"{name} {version}"
                        except:
                            pass
                    elif 'DISTRIB_DESCRIPTION' in content:
                        try:
                            description = content.split('DISTRIB_DESCRIPTION=')[1].split('\n')[0].strip('"\'')
                            return description
                        except:
                            pass
        
        # Last resort fallback
        return f"Linux {system_info.release}"
        
    elif system == 'windows':
        win_ver = platform.win32_ver()[0]
        win_ed = platform.win32_edition()
        return f"Windows {win_ver} {win_ed}"
        
    else:
        # Generic fallback
        return f"{system_info.system} {system_info.release}"

def get_project_root():
    """
    Get the path to the project root directory.
    
    Returns:
        Path: Path to the project root
    """
    return Path(__file__).parent.parent

def load_config():
    """
    Load configuration from settings.json
    
    Returns:
        dict: Configuration data
    """
    try:
        config_file = os.path.join(get_project_root(), "config", "settings.json")
        if not os.path.isfile(config_file):
            # Try to create config directory if it doesn't exist
            os.makedirs(os.path.join(get_project_root(), "config"), exist_ok=True)
            with open(config_file, 'w') as f:
                default_config = {
                    "default_ai_provider": "ollama",
                    "ollama_base_url": "http://localhost:11434",
                    "default_ollama_model": "gemma:7b",
                    "shell_safe_mode": True,
                    "interactive_mode": True,
                    "shell_dangerous_check": True
                }
                json.dump(default_config, f, indent=2)
            print(f"Created default configuration at {config_file}")
            return default_config
            
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            
        return config_data
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def is_interactive_session():
    """
    Determine if the current session is interactive (connected to a terminal).
    
    Returns:
        bool: True if running in an interactive session, False otherwise
    """
    # Check if stdin is connected to a TTY
    if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
        return True
    
    # Check environment variables that might indicate an interactive session
    if os.environ.get('PS1') or os.environ.get('TERM'):
        return True
        
    return False 