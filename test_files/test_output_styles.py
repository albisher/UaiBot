#!/usr/bin/env python3
"""
Simple test for output styles
"""
import os
import json
import sys

# Get the project root path
project_root = os.path.abspath(os.path.dirname(__file__))

# Define the config path
config_path = os.path.join(project_root, "config", "output_styles.json")

try:
    # Attempt to load the config file
    print(f"Trying to load config from: {config_path}")
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(f"Config loaded successfully:")
    print(f"- Themes: {list(config.get('themes', {}).keys())}")
    
    # Print some sample emoji
    emoji_set = config.get("emoji_sets", {}).get("default", {})
    print(f"- Sample emojis: success={emoji_set.get('success')}, warning={emoji_set.get('warning')}")
    
except Exception as e:
    print(f"Error: {e}")
    
print("Script completed.")
