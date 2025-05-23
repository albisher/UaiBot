#!/usr/bin/env python3

import json
import logging
from uaibot.core.command_processor.ai_command_extractor import AICommandExtractor
from uaibot.core.command_processor.ai_driven_processor import AIDrivenProcessor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_command_extraction():
    """Test the command extraction functionality."""
    extractor = AICommandExtractor()
    processor = AIDrivenProcessor()
    
    # Test cases
    test_cases = [
        # Test 1: Simple JSON command
        {
            "input": '{"command": "ls -la", "explanation": "List files", "confidence": 0.95, "type": "shell"}',
            "description": "Simple JSON command"
        },
        # Test 2: JSON in code block
        {
            "input": '```json\n{"file_operation": "create", "operation_params": {"filename": "test.txt"}, "explanation": "Create file", "confidence": 0.95, "type": "file"}\n```',
            "description": "JSON in code block"
        },
        # Test 3: Natural language command
        {
            "input": "Run the command: ls -la",
            "description": "Natural language command"
        },
        # Test 4: Arabic command
        {
            "input": "نفذ الامر: ls -la",
            "description": "Arabic command"
        },
        # Test 5: Error case
        {
            "input": "I cannot execute this command because it's unsafe",
            "description": "Error case"
        }
    ]
    
    print("\nTesting Command Extraction:")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print("-" * 30)
        print(f"Input: {test_case['input']}")
        
        # Test extractor
        success, command, metadata = extractor.extract_command(test_case['input'])
        print("\nExtractor Results:")
        print(f"Success: {success}")
        print(f"Command: {command}")
        print(f"Metadata: {json.dumps(metadata, indent=2)}")
        
        # Test processor
        success, command, metadata = processor.extract_command(test_case['input'])
        print("\nProcessor Results:")
        print(f"Success: {success}")
        print(f"Command: {command}")
        print(f"Metadata: {json.dumps(metadata, indent=2)}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_command_extraction() 