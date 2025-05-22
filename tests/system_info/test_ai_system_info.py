#!/usr/bin/env python3
"""
Test the AI handler with system information
"""

import os
import sys
import traceback

# Import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Importing AI handler module...")
    from app.core.ai_handler import get_system_info, OllamaAIHandler
    print("AI handler module imported successfully!")
    
    # Test system info function
    print("\n===== Testing system information retrieval =====")
    try:
        print("Calling get_system_info()...")
        system_info = get_system_info()
        print(f"System information: {system_info}")
        print("✅ System info test passed!")
    except Exception as e:
        print(f"❌ System info test failed: {str(e)}")
        traceback.print_exc()
    
    # Test AI prompt creation
    print("\n===== Testing AI prompt with system info =====")
    try:
        print("Creating OllamaAIHandler instance...")
        ai_handler = OllamaAIHandler(model="gemma3:4b", quiet_mode=False)
        print("OllamaAIHandler created")
        
        test_prompt = "What's the best file manager for my computer?"
        print(f"Test prompt: {test_prompt}")
        
        # Get the generated prompt without making an actual API call
        print("Getting enhanced prompt (without making API call)...")
        if hasattr(ai_handler, 'query_ai'):
            try:
                # We'll monkey-patch the handler to just return the prompt
                original_method = ai_handler._query_ollama_api
                ai_handler._query_ollama_api = lambda prompt, **kwargs: f"ENHANCED PROMPT: {prompt}"
                
                result = ai_handler.query_ai(test_prompt)
                print("\nResult contains enhanced prompt:")
                
                if "System Information" in result:
                    print("✅ System information was included in the prompt!")
                else:
                    print("❌ System information was NOT found in the prompt")
                
                # Restore original method
                ai_handler._query_ollama_api = original_method
            except Exception as e:
                print(f"❌ Error testing query_ai: {str(e)}")
                traceback.print_exc()
        else:
            print("❓ query_ai method not found in OllamaAIHandler")
            
    except Exception as e:
        print(f"❌ AI handler test failed: {str(e)}")
        traceback.print_exc()

except ImportError as e:
    print(f"Import error: {str(e)}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {str(e)}")
    traceback.print_exc()
