#!/usr/bin/env python3
# simple_test_system_info.py

import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.ai_handler import get_system_info

def main():
    """Print the system information for the current system."""
    system_info = get_system_info()
    print(f"System Info: {system_info}")
    print("\nSuccessfully ran the get_system_info() function!")

if __name__ == '__main__':
    main()
