#!/usr/bin/env python3
import os
import json

try:
    config_path = os.path.join(os.path.dirname(__file__), "config", "output_styles.json")
    print(f"Reading file: {config_path}")
    print(f"File exists: {os.path.exists(config_path)}")
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    print("\nFile content (first 500 chars):")
    print(content[:500])
    print("...")
    
except Exception as e:
    print(f"Error: {e}")

