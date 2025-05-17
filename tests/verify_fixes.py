#!/usr/bin/env python3
"""
Final verification script for UaiBot fixes
"""

import os
import sys
import traceback
import time

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_fixes():
    """Verify that both fixes have been properly applied"""
    print("====================================================")
    print("UaiBot Fix Verification")
    print("====================================================")
    
    # Check 1: find_folders method with include_cloud parameter
    print("\n1. Verifying find_folders fix with include_cloud parameter...")
    try:
        from core.shell_handler import ShellHandler
        shell = ShellHandler(safe_mode=False)
        
        # Try to call the method with the parameter that was causing issues
        result = shell.find_folders("notes", include_cloud=True)
        print("✅ find_folders method called successfully with include_cloud parameter!")
        print(f"Result excerpt: {result[:100]}...")
    except TypeError as e:
        if "unexpected keyword argument 'include_cloud'" in str(e):
            print("❌ FAILED: Still encountering 'unexpected keyword argument include_cloud' error!")
            print(f"Error: {str(e)}")
        else:
            print(f"❌ FAILED: TypeError: {str(e)}")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {str(e)}")
        traceback.print_exc()
    
    # Check 2: System information in AI prompts
    print("\n2. Verifying system information addition to AI prompts...")
    try:
        from core.ai_handler import get_system_info, OllamaAIHandler
        
        # First check if the function exists
        if not callable(get_system_info):
            print("❌ FAILED: get_system_info function is not callable or does not exist!")
            return
        
        # Check system info output
        system_info = get_system_info()
        print(f"System info detected: {system_info[:50]}...")
        
        # Create a mock AI handler to check if system info is added to prompts
        class TestAIHandler(OllamaAIHandler):
            """Test class that extends OllamaAIHandler to check prompt enhancement"""
            def _query_ollama_api(self, prompt, **kwargs):
                """Mock method that just returns the prompt for checking"""
                return f"PROMPT_INSPECT: {prompt}"
        
        test_handler = TestAIHandler(model="gemma3:4b", quiet_mode=False)
        result = test_handler.query_ai("Test prompt")
        
        if "System Information" in result and system_info in result:
            print("✅ System information is successfully added to AI prompts!")
        else:
            print("❌ FAILED: System information not found in AI prompts!")
            print(f"Prompt result: {result[:100]}...")
    except ImportError:
        print("❌ FAILED: Could not import required modules!")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ FAILED: Unexpected error in AI handler test: {str(e)}")
        traceback.print_exc()
    
    print("\n====================================================")
    print("Verification completed!")
    print("====================================================")

if __name__ == "__main__":
    verify_fixes()
