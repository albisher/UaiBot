#!/usr/bin/env python3
"""macOS platform initialization module for the Labeeb system.

This module provides functionality for:
- System requirements verification
- Permission setup and management
- Service initialization
- Environment configuration
- Platform-specific setup

The module handles the initialization of macOS-specific components and
ensures proper setup of the Labeeb platform on macOS systems.
"""
import os
import sys
import subprocess
import platform

def check_macos():
    """Check if we're running on macOS"""
    if platform.system() != 'Darwin':
        print(f"Error: This script is for macOS only, but detected {platform.system()}")
        sys.exit(1)
        
    print(f"Running on macOS {platform.mac_ver()[0]} ({platform.machine()})")
    
    # Check if running on Apple Silicon
    if platform.machine() not in ['arm64', 'aarch64']:
        print(f"Warning: This script is optimized for Apple Silicon, but detected {platform.machine()}")
        print("Some features may not work correctly.")
    else:
        print("Apple Silicon detected.")

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None

def install_dependencies():
    """Install necessary dependencies"""
    print("\nInstalling required dependencies...")
    
    # Check for Homebrew
    if not os.path.exists('/opt/homebrew/bin/brew') and not os.path.exists('/usr/local/bin/brew'):
        print("Homebrew not found. Installing...")
        brew_install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        print("Executing Homebrew installation script...")
        result = run_command(brew_install_cmd, check=False)
        
        # Check if successful
        if not os.path.exists('/opt/homebrew/bin/brew') and not os.path.exists('/usr/local/bin/brew'):
            print("Failed to install Homebrew. Please install it manually and try again.")
            print("Visit https://brew.sh for instructions.")
            sys.exit(1)
        else:
            print("Homebrew installed successfully.")
    else:
        print("Homebrew already installed.")
    
    # Determine Homebrew path
    brew_path = '/opt/homebrew/bin/brew' if os.path.exists('/opt/homebrew/bin/brew') else '/usr/local/bin/brew'
    
    # Update Homebrew
    print("Updating Homebrew...")
    run_command(f"{brew_path} update", check=False)
    
    # Install necessary packages
    packages = ["python", "portaudio", "ollama", "libusb"]
    for package in packages:
        print(f"Installing {package}...")
        result = run_command(f"{brew_path} install {package}")
        if result:
            print(f"{package} installed or updated.")
    
    # Install Python packages
    print("\nInstalling Python packages...")
    requirements_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "requirements.txt")
    run_command(f"pip3 install -r {requirements_file}")

def setup_ollama():
    """Set up Ollama and required models"""
    print("\nSetting up Ollama...")
    
    # Check if Ollama is installed
    if not os.path.exists('/opt/homebrew/bin/ollama') and not os.path.exists('/usr/local/bin/ollama'):
        print("Ollama not installed. Please install it with 'brew install ollama'")
        return
        
    # Determine Ollama path
    ollama_path = '/opt/homebrew/bin/ollama' if os.path.exists('/opt/homebrew/bin/ollama') else '/usr/local/bin/ollama'
    
    # Check if Ollama is running
    ollama_running = run_command(f"pgrep -f 'ollama serve'")
    if not ollama_running:
        print("Ollama is not running. Starting Ollama server...")
        # Start Ollama in the background
        subprocess.Popen([ollama_path, "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Ollama server started.")
    else:
        print("Ollama server is already running.")
    
    # Get configuration
    import json
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "settings.json")
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        default_model = config.get('default_ollama_model', 'gemma3:4b')
    except:
        default_model = 'gemma3:4b'
        
    # Check if model is installed
    models = run_command(f"{ollama_path} list")
    if default_model not in models:
        print(f"Installing Ollama model {default_model}...")
        run_command(f"{ollama_path} pull {default_model}")
        print(f"Model {default_model} installed.")
    else:
        print(f"Ollama model {default_model} is already installed.")

def setup_platform_specific():
    """Set up platform specific components"""
    print("\nSetting up platform-specific components...")
    
    # Create audio directory if it doesn't exist
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio", "recordings")
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"Created directory: {audio_dir}")
    
    # Run platform test script
    print("\nTesting platform-specific components...")
    platform_test_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "test_platform_components.py")
    
    if os.path.exists(platform_test_script):
        print("Running platform test...")
        subprocess.run([sys.executable, platform_test_script])
    else:
        print(f"Platform test script not found: {platform_test_script}")

def main():
    """Main function"""
    print("Labeeb Mac M4 Setup")
    print("===================")
    
    # Check if running on macOS
    check_macos()
    
    # Install dependencies
    install_dependencies()
    
    # Set up Ollama
    setup_ollama()
    
    # Set up platform-specific components
    setup_platform_specific()
    
    print("\nSetup complete!")
    print("\nTo run Labeeb:")
    print("1. Terminal mode: python3 main.py")
    print("2. GUI mode: python3 gui_launcher.py")

if __name__ == "__main__":
    main()
