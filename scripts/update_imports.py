#!/usr/bin/env python3
import os
import re
from pathlib import Path

def update_imports(directory):
    """Update all imports from 'app' to 'labeeb' in Python files."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update imports
                    updated_content = re.sub(
                        r'from\s+app\.',
                        'from labeeb.',
                        content
                    )
                    updated_content = re.sub(
                        r'import\s+app\.',
                        'import labeeb.',
                        updated_content
                    )
                    
                    if content != updated_content:
                        print(f"Updating imports in {file_path}")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == '__main__':
    src_dir = Path('src')
    update_imports(src_dir) 