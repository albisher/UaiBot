#!/usr/bin/env python3
"""
Test file operations for UaiBot
This script tests the file operations functionalities of UaiBot
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the necessary functions
from main import parse_file_request, handle_file_operation

def test_file_create_with_date():
    """Test creating a file with today's date"""
    test_request = "inside test_files folder, create new file name it today.txt and add to it the date on top then save."
    
    # Parse the request
    parsed = parse_file_request(test_request)
    print("Parsed request:", parsed)
    
    # Handle the operation
    result = handle_file_operation(parsed)
    print("Operation result:", result)
    
    # Verify the file was created
    expected_path = os.path.join("test_files", "today.txt")
    if os.path.exists(expected_path):
        print(f"✅ File created successfully at {expected_path}")
        with open(expected_path, 'r') as f:
            content = f.read().strip()
        print(f"File content: {content}")
        
        # Check if the date is present
        try:
            # Try to parse the date to verify format
            datetime.strptime(content.split()[0], "%Y-%m-%d")
            print("✅ Date format is correct")
        except ValueError:
            print("❌ Date format is incorrect")
    else:
        print(f"❌ File not created at {expected_path}")

def test_create_file_in_custom_folder():
    """Test creating a file in a specific folder"""
    test_request = "create new file example.py in test_files/subfolder"
    
    # Create the subfolder if it doesn't exist
    if not os.path.exists("test_files/subfolder"):
        os.makedirs("test_files/subfolder")
        
    # Parse the request
    parsed = parse_file_request(test_request)
    print("Parsed request:", parsed)
    
    # Handle the operation
    result = handle_file_operation(parsed)
    print("Operation result:", result)
    
    # Verify the file was created
    expected_path = os.path.join("test_files", "subfolder", "example.py")
    if os.path.exists(expected_path):
        print(f"✅ File created successfully at {expected_path}")
    else:
        print(f"❌ File not created at {expected_path}")

def run_all_tests():
    """Run all the test functions"""
    print("=== Testing File Creation with Date ===")
    test_file_create_with_date()
    print("\n=== Testing File Creation in Custom Folder ===")
    test_create_file_in_custom_folder()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test UaiBot file operations")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--create-date", action="store_true", help="Test creating file with date")
    parser.add_argument("--create-folder", action="store_true", help="Test creating file in custom folder")
    
    args = parser.parse_args()
    
    if args.all or (not args.create_date and not args.create_folder):
        run_all_tests()
    else:
        if args.create_date:
            test_file_create_with_date()
        if args.create_folder:
            test_create_file_in_custom_folder()
