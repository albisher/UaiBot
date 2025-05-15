#!/usr/bin/env python3
"""
Mac platform initialization script for UaiBot
Checks for necessary dependencies and sets up Mac-specific components
"""
import os
import sys
import subprocess
import shutil
import platform

def check_python_version():
    """Check if Python version is supported"""
    required_major = 3
    required_minor = 8
    
    major, minor, _ = sys.version_info
    
    if major < required_major or (major == required_major and minor < required_minor):
        print(f"Error: Python {required_major}.{required_minor}+ required, but {major}.{minor} found.")
        return False
    return True

def check_command_available(command):
    """Check if a command is available in the system path"""
    return shutil.which(command) is not None

def check_brew_installed():
    """Check if Homebrew is installed"""
    return check_command_available('brew')

def install_brew_package(package):
    """Install a package using Homebrew"""
    try:
        print(f"Installing {package} with Homebrew...")
        subprocess.run(['brew', 'install', package], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package}: {e}")
        return False

def check_pip_installed():
    """Check if pip is installed"""
    return check_command_available('pip') or check_command_available('pip3')

def pip_install_package(package):
    """Install a package using pip"""
    pip_cmd = 'pip3' if check_command_available('pip3') else 'pip'
    try:
        print(f"Installing {package} with {pip_cmd}...")
        subprocess.run([pip_cmd, 'install', package], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package}: {e}")
        return False

def install_requirements():
    """Install Python requirements from requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'requirements.txt')
    if not os.path.exists(requirements_path):
        print(f"Error: {requirements_path} not found")
        return False
        
    pip_cmd = 'pip3' if check_command_available('pip3') else 'pip'
    try:
        print(f"Installing dependencies from {requirements_path}...")
        subprocess.run([pip_cmd, 'install', '-r', requirements_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def check_ollama_installed():
    """Check if Ollama is installed"""
    return check_command_available('ollama')

def install_ollama():
    """Install Ollama"""
    if check_brew_installed():
        return install_brew_package('ollama')
    else:
        print("Homebrew not installed. Please install Homebrew first:")
        print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False

def check_required_ollama_models(models=["gemma3:4b"]):
    """Check if required Ollama models are installed"""
    if not check_ollama_installed():
        return False
        
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        output = result.stdout
        
        missing_models = []
        for model in models:
            if model not in output:
                missing_models.append(model)
                
        if missing_models:
            print(f"Missing required Ollama models: {', '.join(missing_models)}")
            for model in missing_models:
                print(f"Installing model {model}...")
                try:
                    subprocess.run(['ollama', 'pull', model], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error installing model {model}: {e}")
                    return False
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking Ollama models: {e}")
        return False

def check_audio_dependencies():
    """Check Mac audio dependencies"""
    # PyAudio is tricky on Mac, it depends on portaudio
    if check_brew_installed():
        try:
            # Check if portaudio is installed
            result = subprocess.run(['brew', 'list', 'portaudio'], capture_output=True, text=True)
            if result.returncode != 0:
                print("portaudio not installed. Installing...")
                if not install_brew_package('portaudio'):
                    return False
                    
            # Now install PyAudio
            pip_cmd = 'pip3' if check_command_available('pip3') else 'pip'
            subprocess.run([pip_cmd, 'install', 'PyAudio'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error checking audio dependencies: {e}")
            return False
    else:
        print("Homebrew not installed. Cannot check/install audio dependencies.")
        return False

def main():
    """Main function to initialize Mac platform"""
    # Check if we're running on a Mac
    if platform.system() != 'Darwin':
        print(f"Error: This script is for macOS only, but detected {platform.system()}")
        sys.exit(1)
        
    print(f"Initializing UaiBot for macOS ({platform.mac_ver()[0]})")
    print(f"  Architecture: {platform.machine()}")
    
    # Check Python version
    if not check_python_version():
        print("Please install a compatible Python version and try again.")
        sys.exit(1)
        
    # Check for Homebrew
    if not check_brew_installed():
        print("Homebrew not installed. It's recommended for installing dependencies.")
        print("Install Homebrew with:")
        print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    else:
        print("Homebrew found.")
    
    # Check for pip
    if not check_pip_installed():
        print("pip not installed. Installing...")
        if not install_brew_package('python3-pip'):
            print("Failed to install pip. Please install it manually.")
            sys.exit(1)
    else:
        print("pip found.")
    
    # Check for audio dependencies
    print("Checking audio dependencies...")
    if check_audio_dependencies():
        print("Audio dependencies installed.")
    else:
        print("Failed to install audio dependencies.")
        
    # Install Python requirements
    print("Installing Python requirements...")
    if install_requirements():
        print("Python requirements installed successfully.")
    else:
        print("Failed to install Python requirements.")
        
    # Check for Ollama
    print("Checking for Ollama...")
    if not check_ollama_installed():
        print("Ollama not installed. Installing...")
        if install_ollama():
            print("Ollama installed successfully.")
        else:
            print("Failed to install Ollama. Please install it manually.")
    else:
        print("Ollama found.")
        
    # Check for required Ollama models
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'settings.json')
    required_models = ["gemma3:4b"]  # Default model
    
    import json
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            if 'default_ollama_model' in config:
                required_models = [config['default_ollama_model']]
    except Exception as e:
        print(f"Warning: Could not read config file: {e}")
        
    print(f"Checking for required Ollama models: {', '.join(required_models)}...")
    if check_required_ollama_models(required_models):
        print("Required Ollama models are installed.")
    else:
        print("Failed to verify/install required Ollama models.")
    
    print("\nMac platform initialization complete.")
    print("You can now run the UaiBot application with: python main.py")

if __name__ == "__main__":
    main()
