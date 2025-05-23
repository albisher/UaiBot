#!/usr/bin/env python3
"""
UaiBot Launcher - Delegates to src/uaibot/core/main.py
"""
import sys
from pathlib import Path

# Add src to sys.path so we can import core modules
project_root = Path(__file__).parent.resolve()
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from uaibot.core.main import main

if __name__ == '__main__':
    main() 