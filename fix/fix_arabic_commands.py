#!/usr/bin/env python3
"""
Fix script for Arabic command support in UaiBot.
This script fixes the syntax error in ai_command_extractor.py where 'في' is used instead of 'in'.
"""
import os
import re
import sys
from pathlib import Path

def find_and_fix_arabic_operator_issues(file_path):
    """
    Find and fix Arabic operator issues in the given file.
    
    Args:
        file_path: Path to the file to check and fix
        
    Returns:
        tuple: (fixed_count, file_content) - Number of fixes made and updated content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace Arabic 'في' with Python 'in' operator
        content_fixed = re.sub(r'(["\'a-zA-Z_0-9\s]+)\s+في\s+', r'\1 in ', content)
        
        # Count fixes
        fixes_count = content.count(' في ') - content_fixed.count(' في ')
        
        return fixes_count, content_fixed
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, None

def main():
    # Get the project root directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    project_root = script_dir.parent
    
    # File with known issue
    ai_extractor_path = project_root / "command_processor" / "ai_command_extractor.py"
    
    if not ai_extractor_path.exists():
        print(f"❌ File not found: {ai_extractor_path}")
        return 1
        
    print(f"Checking {ai_extractor_path} for Arabic operator issues...")
    fixes_count, fixed_content = find_and_fix_arabic_operator_issues(ai_extractor_path)
    
    if fixes_count > 0:
        # Backup original file
        backup_path = ai_extractor_path.with_suffix(ai_extractor_path.suffix + '.bak')
        print(f"Making backup of original file to: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            with open(ai_extractor_path, 'r', encoding='utf-8') as orig:
                f.write(orig.read())
        
        # Write fixed content
        print(f"Fixed {fixes_count} Arabic operator issues. Writing changes...")
        with open(ai_extractor_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
            
        print(f"✅ Successfully fixed {fixes_count} issues in {ai_extractor_path}")
    else:
        print(f"✅ No issues found in {ai_extractor_path}")
    
    # Look for other potential files with the same issue
    print("\nChecking other Python files for potential Arabic operator issues...")
    
    potential_issues = 0
    for py_file in project_root.rglob("*.py"):
        if py_file == ai_extractor_path or py_file == Path(__file__):
            continue
            
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                content = f.read()
                if ' في ' in content:
                    print(f"⚠️ Potential issue found in: {py_file}")
                    potential_issues += 1
            except Exception:
                # Skip files with encoding issues
                pass
    
    if potential_issues == 0:
        print("✅ No other files with potential Arabic operator issues found.")
    else:
        print(f"⚠️ Found {potential_issues} files with potential Arabic operator issues.")
        print("   Please run the fix script on those files if needed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
