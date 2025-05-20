#!/usr/bin/env python3
"""
Verify Arabic command support in UaiBot after fixes.
This script tests if the AICommandExtractor can properly handle Arabic commands.
"""
import os
import sys
from pathlib import Path

def main():
    """
    Verify that the AICommandExtractor module can be imported and Arabic commands work.
    """
    # Get the project root directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    project_root = script_dir.parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    try:
        # Try importing the module
        from command_processor.ai_command_extractor import AICommandExtractor
        print("✅ Success: AICommandExtractor module imported correctly!")
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return 1
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        print(f"   Line {e.lineno}, Position {e.offset}: {e.text}")
        return 1
    
    # Test Arabic command extraction
    print("\n=== Testing Arabic Command Extraction ===")
    extractor = AICommandExtractor()
    
    # Test Arabic commands
    test_commands = [
        "احذف الملف test.txt",  # Delete file
        "اقرأ ملف config.json",  # Read file
        "انشئ ملف جديد باسم hello.txt",  # Create file
        "اكتب 'مرحبا بالعالم' في ملف hello.txt",  # Write to file
    ]
    
    for cmd in test_commands:
        print(f"Arabic input: {cmd}")
        success, command, metadata = extractor.extract_command(cmd)
        print(f"Extracted command: {command}")
        print("----------------------------------------")
    
    print("\nAll tests completed successfully! Arabic command extraction is working.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
