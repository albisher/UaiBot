#!/usr/bin/env python3
"""
Script to update import paths in Python files to use the uaibot package prefix.
"""
import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping non-UTF-8 file: {file_path}")
        return
    
    # Update from uaibot.core.X to from uaibot.core.X
    updated_content = re.sub(
        r'from\s+core\.',
        'from uaibot.core.',
        content
    )
    
    # Update import uaibot.core.X to import uaibot.core.X
    updated_content = re.sub(
        r'import\s+core\.',
        'import uaibot.core.',
        updated_content
    )
    
    if content != updated_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Updated imports in {file_path}")

def main():
    """Main function to update imports in all Python files."""
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Walk through all Python files
    for root, dirs, files in os.walk(project_root):
        # Skip virtual environment directories
        if '.venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                update_imports_in_file(file_path)

if __name__ == '__main__':
    main() 