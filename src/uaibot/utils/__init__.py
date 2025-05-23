"""
Utility functions for UaiBot.
Shared across different modules.

This package provides various utility functions for:
- Platform detection
- Configuration handling
- Output formatting
- File operations
"""
import os
import platform
from pathlib import Path
import json
import sys
import subprocess

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None

# Optional imports to make formatting utilities available directly
try:
    from .output_formatter import (
        EMOJI, format_header, format_table_row, format_box,
        format_status_line, format_list, create_divider
    )
except ImportError:
    # Output formatter not available, ignore
    pass

def get_platform_name():
    """
    Get a more descriptive name for the current platform.
    
    Returns:
        str: Descriptive platform name
    """
    system = platform.system().lower()
    
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
        return f"Linux {platform.release()}"
        
    elif system == 'windows':
        win_ver = platform.version()
        win_ed = platform.win32_edition() if hasattr(platform, 'win32_edition') else ""
        return f"Windows {win_ver} {win_ed}"
        
    else:
        # Generic fallback
        return f"{platform.system()} {platform.release()}"

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
                    "google_api_key": "YOUR_GOOGLE_API_KEY",
                    "default_google_model": "gemini-1.0-pro",
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
        
    # Check if running in a Jupyter notebook
    try:
        from .IPython import get_ipython
        if get_ipython() is not None:
            return True
    except (ImportError, NameError):
        pass
        
    return False

try:
    from .IPython import get_ipython
except ImportError:
    def get_ipython():
        return None
