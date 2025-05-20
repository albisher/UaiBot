#!/usr/bin/env python3

"""
Cleanup script to remove syntax errors from UaiBot code.
This script removes problematic format examples and fixes syntax issues.
"""

import os
import re
import sys

def clean_file(file_path):
    """Clean a file by removing syntax errors."""
    print(f"Cleaning file: {file_path}")
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove problematic content
    # Remove format examples in comments
    content = re.sub(r'FORMAT \d+.*?```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'MULTILINGUAL SUPPORT:.*?SAFETY INSTRUCTIONS', '', content, flags=re.DOTALL)
    content = re.sub(r'SAFETY INSTRUCTIONS:.*?IMPORTANT:', '', content, flags=re.DOTALL)
    content = re.sub(r'IMPORTANT:.*?Now process', '', content, flags=re.DOTALL)
    content = re.sub(r'Now process.*?Extract', '', content, flags=re.DOTALL)
    
    # Remove "..." in doc comments as they're problematic
    content = re.sub(r'""".*?Extract detailed implementation requirements', '"""', content, flags=re.DOTALL)
    
    # Write the cleaned content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Cleaned file: {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        clean_file(file_path)
    else:
        print("Please provide a file path to clean")
        sys.exit(1)
