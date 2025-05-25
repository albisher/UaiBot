#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if Python 3.10+ is installed
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.10" | bc -l) )); then
    print_error "Python 3.10 or higher is required. Found version $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
python3 -m pip install -r requirements.txt

# Platform-specific setup
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    print_status "Setting up macOS-specific dependencies..."
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install qt5
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    print_status "Setting up Linux-specific dependencies..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-dev espeak
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-tkinter python3-devel espeak
    fi
fi

# Verify installation
print_status "Verifying installation..."
python3 -c "
try:
    import aiohttp
    import PyQt5
    import pyautogui
    import psutil
    import pynput
    from PIL import Image
    import pyttsx3
    import whisper
    print('All dependencies installed successfully!')
except ImportError as e:
    print(f'Error: {e}')
    exit(1)
"

# Final message
print_status "Installation complete!"
print_status "To activate the virtual environment, run: source .venv/bin/activate" 