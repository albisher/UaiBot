#!/usr/bin/env python3
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# Set display environment variable
os.environ['DISPLAY'] = ''

# Simply try to import the class
from input_control import MouseKeyboardHandler

print(f"Successfully imported MouseKeyboardHandler from input_control")

# Create an instance
handler = MouseKeyboardHandler()

print(f"Successfully created MouseKeyboardHandler instance")
print(f"Simulation mode: {handler._simulate_only}")

# Test simple methods
print("Testing move_mouse method")
handler.move_mouse(100, 100)

print("Done!")
