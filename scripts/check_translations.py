#!/usr/bin/env python3
"""Script to check for untranslated strings in the codebase.

This script:
- Scans Python files for user-facing strings
- Identifies strings that should be translated
- Reports potential translation issues
- Suggests improvements
"""

import os
import re
from pathlib import Path
from typing import List, Set, Dict, Any
from dataclasses import dataclass
from enum import Enum

class StringType(Enum):
    """Types of user-facing strings."""
    SIMPLE = "simple"
    PLURAL = "plural"
    FORMAT = "format"
    HTML = "html"
    MARKDOWN = "markdown"

@dataclass
class StringInfo:
    """Information about a user-facing string."""
    file_path: Path
    line_number: int
    string_type: StringType
    content: str
    context: str

def find_python_files() -> List[Path]:
    """Find all Python files in the codebase.
    
    Returns:
        List[Path]: List of Python file paths
    """
    src_dir = Path("src")
    if not src_dir.exists():
        print("No src directory found")
        return []

    return list(src_dir.rglob("*.py"))

def is_translated_string(line: str) -> bool:
    """Check if a line contains a translated string.
    
    Args:
        line: Line of code to check
        
    Returns:
        bool: True if the line contains a translated string
    """
    # Check for _() or ngettext() calls
    if re.search(r'_\s*\(|ngettext\s*\(', line):
        return True
    return False

def is_user_facing_string(line: str) -> bool:
    """Check if a line contains a user-facing string.
    
    Args:
        line: Line of code to check
        
    Returns:
        bool: True if the line contains a user-facing string
    """
    # Skip comments and docstrings
    if line.strip().startswith(('#', '"""', "'''")):
        return False

    # Skip empty lines
    if not line.strip():
        return False

    # Check for string literals
    if re.search(r'["\'](.*?)["\']', line):
        return True
    return False

def get_string_type(line: str) -> StringType:
    """Determine the type of a user-facing string.
    
    Args:
        line: Line of code containing the string
        
    Returns:
        StringType: Type of the string
    """
    if re.search(r'ngettext\s*\(', line):
        return StringType.PLURAL
    if re.search(r'\{.*?\}', line):
        return StringType.FORMAT
    if re.search(r'<[^>]+>', line):
        return StringType.HTML
    if re.search(r'[#*_`]', line):
        return StringType.MARKDOWN
    return StringType.SIMPLE

def analyze_file(file_path: Path) -> List[StringInfo]:
    """Analyze a Python file for user-facing strings.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List[StringInfo]: List of user-facing strings found
    """
    strings = []
    try:
        with file_path.open(encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return strings

    for i, line in enumerate(lines, 1):
        if is_user_facing_string(line) and not is_translated_string(line):
            string_type = get_string_type(line)
            strings.append(StringInfo(
                file_path=file_path,
                line_number=i,
                string_type=string_type,
                content=line.strip(),
                context="\n".join(lines[max(0, i-2):min(len(lines), i+2)])
            ))

    return strings

def generate_report(strings: List[StringInfo]) -> None:
    """Generate a report of untranslated strings.
    
    Args:
        strings: List of user-facing strings found
    """
    if not strings:
        print("No untranslated strings found!")
        return

    print("\nUntranslated Strings Report")
    print("=" * 50)

    # Group strings by type
    by_type: Dict[StringType, List[StringInfo]] = {}
    for string in strings:
        by_type.setdefault(string.string_type, []).append(string)

    # Print summary
    print("\nSummary:")
    print("-" * 20)
    for string_type, type_strings in by_type.items():
        print(f"{string_type.value.title()} strings: {len(type_strings)}")

    # Print detailed report
    print("\nDetailed Report:")
    print("-" * 20)
    for string_type, type_strings in by_type.items():
        print(f"\n{string_type.value.title()} Strings:")
        print("-" * 20)
        for string in type_strings:
            print(f"\nFile: {string.file_path}")
            print(f"Line: {string.line_number}")
            print(f"Content: {string.content}")
            print("Context:")
            print(string.context)
            print("-" * 20)

    # Print recommendations
    print("\nRecommendations:")
    print("-" * 20)
    print("1. Use the translation functions for all user-facing strings:")
    print("   - _() for simple strings")
    print("   - ngettext() for plural strings")
    print("2. Consider using translation comments for context")
    print("3. Keep format arguments consistent across translations")
    print("4. Use meaningful message IDs")
    print("5. Document any special formatting or context")

def main() -> None:
    """Main function to check for untranslated strings."""
    print("Starting translation check...")

    # Find Python files
    py_files = find_python_files()
    if not py_files:
        print("No Python files found")
        return

    # Analyze files
    all_strings = []
    for file_path in py_files:
        print(f"Analyzing {file_path}...")
        strings = analyze_file(file_path)
        all_strings.extend(strings)

    # Generate report
    generate_report(all_strings)

    print("\nTranslation check completed!")

if __name__ == "__main__":
    main() 