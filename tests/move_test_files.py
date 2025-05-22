#!/usr/bin/env python3
"""
Script to organize test files into their proper directories.
"""

import os
import shutil
from pathlib import Path

def organize_test_files():
    """Organize test files into their proper directories."""
    # Get the test directory
    test_dir = Path(__file__).parent
    
    # Define test file mappings
    test_mappings = {
        'core/command_processor/': [
            'test_ai_command_extractor.py',
            'test_command_processor.py',
            'test_ai_command_interpreter.py',
            'test_ai_handler.py'
        ],
        'core/file_operations/': [
            'test_file_operations.py'
        ],
        'core/ai/': [
            'test_ai_performance_tracker.py',
            'test_model_config_manager.py'
        ],
        'system/': [
            'test_uaibot.py',
            'test_browser_launch.py',
            'test_pyautogui_env.py'
        ]
    }
    
    # Create directories if they don't exist
    for directory in test_mappings.keys():
        os.makedirs(test_dir / directory, exist_ok=True)
    
    # Move files to their proper locations
    for directory, files in test_mappings.items():
        for file in files:
            source = test_dir / file
            if source.exists():
                destination = test_dir / directory / file
                print(f"Moving {source} to {destination}")
                shutil.move(str(source), str(destination))

if __name__ == '__main__':
    organize_test_files() 