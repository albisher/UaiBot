#!/usr/bin/env python3
"""
Utility script to update Python imports across the project.
Handles both regular imports and test imports.
"""

import os
import re
from pathlib import Path
from typing import List, Set

def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in the given directory."""
    return list(Path(directory).rglob("*.py"))

def update_imports(file_path: Path, is_test: bool = False) -> None:
    """Update imports in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Update relative imports
    if is_test:
        # For test files, update imports to use src directory
        content = re.sub(
            r'from (?!\.)([a-zA-Z_][a-zA-Z0-9_]*) import',
            r'from src.\1 import',
            content
        )
    else:
        # For regular files, ensure proper relative imports
        content = re.sub(
            r'from (?!\.)([a-zA-Z_][a-zA-Z0-9_]*) import',
            r'from .\1 import',
            content
        )

    with open(file_path, 'w') as f:
        f.write(content)

def main():
    """Main function to update imports across the project."""
    # Update regular source files
    src_dir = Path("src")
    if src_dir.exists():
        for file_path in find_python_files(str(src_dir)):
            update_imports(file_path)

    # Update test files
    tests_dir = Path("tests")
    if tests_dir.exists():
        for file_path in find_python_files(str(tests_dir)):
            update_imports(file_path, is_test=True)

if __name__ == "__main__":
    main() 