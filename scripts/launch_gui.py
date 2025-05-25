#!/usr/bin/env python3
"""
UaiBot GUI Launcher

This script launches the UaiBot GUI application.
It handles platform detection and configuration loading.
"""
import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from uaibot.gui.gui_launcher import main

if __name__ == "__main__":
    main() 