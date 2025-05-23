#!/usr/bin/env python3
"""
Script to update import paths in test files to use the uaibot package prefix.
"""

import os
import re
from pathlib import Path

def update_imports(file_path):
    """Update import statements in a file to use uaibot package prefix."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match imports from core, utils, etc.
    patterns = [
        (r'from\s+core\.', 'from uaibot.core.'),
        (r'from\s+utils\.', 'from uaibot.utils.'),
        (r'from\s+gui\.', 'from uaibot.gui.'),
        (r'import\s+core\.', 'import uaibot.core.'),
        (r'import\s+utils\.', 'import uaibot.utils.'),
        (r'import\s+gui\.', 'import uaibot.gui.')
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Updated imports in {file_path}")
    return modified

def process_directory(directory):
    """Process all Python files in a directory recursively."""
    total_updated = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports(file_path):
                    total_updated += 1
    return total_updated

def main():
    """Main function to update test imports."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Process test files
    test_dir = project_root / 'tests'
    if test_dir.exists():
        total_updated = process_directory(test_dir)
        print(f"\nUpdated imports in {total_updated} test files")
    
    # Process core files
    core_dir = project_root / 'uaibot' / 'core'
    if core_dir.exists():
        total_updated = process_directory(core_dir)
        print(f"Updated imports in {total_updated} core files")

if __name__ == '__main__':
    main() 