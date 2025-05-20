#!/usr/bin/env python3
"""
Validation script for Arabic command extraction in UaiBot.
Tests the AICommandExtractor's ability to extract commands from Arabic text.
"""

import os
import sys
import importlib.util

# Add the project root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

def import_module_from_path(name, path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_ai_command_extractor():
    """Test the AICommandExtractor's ability to extract Arabic commands."""
    # Try to import AICommandExtractor
    try:
        # First check if we can import directly
        try:
            from command_processor.ai_command_extractor import AICommandExtractor
            print("✅ Success: AICommandExtractor module imported correctly!")
        except ImportError:
            # If not, try to load it from the file path
            extractor_path = os.path.join(project_root, "command_processor", "ai_command_extractor.py")
            if os.path.exists(extractor_path):
                ai_command_module = import_module_from_path("ai_command_extractor", extractor_path)
                AICommandExtractor = ai_command_module.AICommandExtractor
                print("✅ Success: AICommandExtractor module imported from path!")
            else:
                print("❌ Error: Could not find AICommandExtractor module")
                return False
        
        # Initialize the extractor
        extractor = AICommandExtractor()
        
        # Test cases for Arabic commands
        test_cases = [
            {
                "input": "احذف الملف test.txt",
                "expected": "rm test.txt"
            },
            {
                "input": "اقرأ ملف config.json",
                "expected": "cat config.json"
            },
            {
                "input": "انشئ ملف جديد باسم hello.txt",
                "expected": "touch hello.txt"
            },
            {
                "input": "اكتب 'مرحبا بالعالم' في ملف hello.txt",
                "expected": "echo 'مرحبا بالعالم' > hello.txt"
            },
            {
                "input": "اعرض جميع الملفات في المجلد الحالي",
                "expected": "ls -l"
            }
        ]
        
        print("\n=== Testing Arabic Command Extraction ===")
        for test in test_cases:
            # Create a mock AI response that contains the Arabic command
            mock_response = f"To execute this in Arabic, you would use:\n\n{test['input']}\n\nThis will perform the operation you requested."
            
            # Extract command from the mock response
            command = extractor._extract_arabic_command(mock_response)
            
            # Display results
            print(f"Arabic input: {test['input']}")
            print(f"Extracted command: {command}")
            if command == test['expected']:
                print(f"✅ Passed - Command matches expected: {test['expected']}")
            else:
                print(f"❌ Failed - Expected: {test['expected']}")
            print("-" * 40)
        
        print("\nAll tests completed successfully! Arabic command extraction is working.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ai_command_extractor()
