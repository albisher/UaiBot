#!/usr/bin/env python3
"""
Runner script for validating the Arabic command extraction.
"""

import os
import sys
import subprocess

def run_validation():
    """Run the validation script for Arabic command extraction."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Path to the validation script
    validation_script = os.path.join(script_dir, "validate_arabic_commands.py")
    
    # Execute the validation script
    print(f"Running validation script: {validation_script}")
    result = subprocess.run([sys.executable, validation_script], capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    # Check if the validation was successful
    if result.returncode == 0 and "All tests completed successfully" in result.stdout:
        print("\n✅ Validation successful!")
        return True
    else:
        print("\n❌ Validation failed.")
        return False

if __name__ == "__main__":
    run_validation()
