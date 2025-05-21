#!/usr/bin/env python3
"""
Script to move test files to the correct directory structure.
"""
import os
import shutil
from pathlib import Path

def move_test_files():
    """Move test files to the correct directory structure."""
    # Define source and destination directories
    source_dir = Path('test_files')
    dest_dir = Path('tests')
    
    # Create necessary subdirectories
    test_dirs = {
        'file_operations': dest_dir / 'file_operations',
        'system_info': dest_dir / 'system_info',
        'command_processing': dest_dir / 'command_processing',
        'multilingual': dest_dir / 'multilingual',
        'utils': dest_dir / 'utils'
    }
    
    for dir_path in test_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Define file mappings
    file_mappings = {
        'test_file_operations.py': test_dirs['file_operations'],
        'test_system_info.py': test_dirs['system_info'],
        'test_system_info_in_requests.py': test_dirs['system_info'],
        'test_command_processor.py': test_dirs['command_processing'],
        'test_command_processing_enhanced.py': test_dirs['command_processing'],
        'test_multilingual.py': test_dirs['multilingual'],
        'verify_multilingual.py': test_dirs['multilingual'],
        'test_ai_command_extractor.py': test_dirs['command_processing'],
        'test_ai_driven_extractor.py': test_dirs['command_processing'],
        'test_ai_response_cache.py': test_dirs['command_processing'],
        'test_ai_system_info.py': test_dirs['system_info']
    }
    
    # Move files
    for filename, dest_dir in file_mappings.items():
        source_file = source_dir / filename
        if source_file.exists():
            try:
                shutil.move(str(source_file), str(dest_dir / filename))
                print(f"Moved {filename} to {dest_dir}")
            except Exception as e:
                print(f"Error moving {filename}: {str(e)}")
    
    # Move remaining test files to tests directory
    for file in source_dir.glob('test_*.py'):
        if file.name not in file_mappings:
            try:
                shutil.move(str(file), str(dest_dir / file.name))
                print(f"Moved {file.name} to {dest_dir}")
            except Exception as e:
                print(f"Error moving {file.name}: {str(e)}")

if __name__ == '__main__':
    move_test_files() 