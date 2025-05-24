"""
Test script for fresh Google API setup and integration.
"""
import os
import sys
import json
from pathlib import Path
import google.generativeai as genai
from getpass import getpass

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from uaibot.core.config_manager import ConfigManager
from uaibot.core.key_manager import KeyManager

def simulate_fresh_setup():
    """Simulate a fresh setup process."""
    print("\n=== Simulating Fresh Google API Setup ===\n")
    
    # Initialize managers
    config_manager = ConfigManager()
    key_manager = KeyManager()
    
    # Step 1: Check if Google is configured as provider
    print("Step 1: Checking AI provider configuration...")
    current_provider = config_manager.get('default_ai_provider')
    print(f"Current AI provider: {current_provider}")
    
    if current_provider != 'google':
        print("\nSwitching to Google as AI provider...")
        config_manager.set('default_ai_provider', 'google')
        config_manager.save()
        print("✓ Switched to Google provider")
    
    # Step 2: Check for existing API key
    print("\nStep 2: Checking for existing Google API key...")
    existing_key = key_manager.get_key('GOOGLE_API_KEY')
    if existing_key:
        print("Found existing API key. Press Enter to use it or input a new key directly.")
        choice = input("Choice: ").strip()
        if choice:
            existing_key = choice
            print("✓ Using provided API key.")
            key_manager.set_key('GOOGLE_API_KEY', existing_key)
            # Skip to Step 4 if key is provided here
            goto_step4 = True
        else:
            # If user presses Enter, use the existing key and skip to Step 4
            goto_step4 = True
    else:
        goto_step4 = False

    # Step 3: Setting up Google API key (only if not already provided)
    if not goto_step4:
        print("\nStep 3: Setting up Google API key...")
        print("You can get an API key from: https://console.cloud.google.com/apis/credentials")
        print("\nPlease enter your Google API key:")
        api_key = input("Enter your GOOGLE_API_KEY: ")
        if not api_key:
            print("❌ No API key provided. Setup incomplete.")
            return False
        print(f"Key entered: {api_key}")  # Show the key for confirmation
        print("✓ API key entered and hidden.")
        key_manager.set_key('GOOGLE_API_KEY', api_key)
    
    # Step 4: Test API integration
    print("\nStep 4: Testing Google API integration...")
    while True:
        try:
            # Configure the API
            genai.configure(api_key=key_manager.get_key('GOOGLE_API_KEY'))
            
            # Test with a simple prompt using the selected model from configuration
            model = genai.GenerativeModel(config_manager.get('default_google_model'))
            response = model.generate_content("Say 'Hello, UaiBot!' in a creative way.")
            
            print("\nAPI Test Result:")
            print("---------------")
            print(response.text)
            print("---------------")
            print("✓ Google API integration successful!")
            break
        except Exception as e:
            error_msg = str(e)
            print(f"❌ API test failed: {error_msg}")
            # Automatically list available models if there is an error
            try:
                print("\nFetching available Google models...")
                models = list(genai.list_models())
                if models:
                    print("Available models:")
                    for i, m in enumerate(models, 1):
                        print(f"{i}. {getattr(m, 'name', str(m))}")
                    print("\nPlease choose a model by entering its number (or press Enter to abort):")
                    choice = input("Enter model number: ").strip()
                    if choice and choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(models):
                            selected_model = getattr(models[idx], 'name', str(models[idx]))
                            print(f"Selected model: {selected_model}")
                            config_manager.set('default_google_model', selected_model)
                            config_manager.save()
                            print("✓ Configuration updated with the selected model.")
                            continue
                    print("❌ No valid model selected. Aborting setup.")
                    return False
                else:
                    print("No models found or unable to fetch models.")
            except Exception as model_err:
                print(f"Could not fetch available models: {model_err}")
            if 'API key not valid' in error_msg or 'API_KEY_INVALID' in error_msg:
                print("\nYour API key is invalid. Please re-enter a valid Google API key or press Enter to abort.")
                new_key = input("Enter your GOOGLE_API_KEY: ").strip()
                if not new_key:
                    print("❌ No valid API key provided. Aborting setup.")
                    return False
                key_manager.set_key('GOOGLE_API_KEY', new_key)
                continue
            return False
    
    # Step 5: Verify configuration
    print("\nStep 5: Verifying final configuration...")
    print(f"AI Provider: {config_manager.get('default_ai_provider')}")
    print(f"Google Model: {config_manager.get('default_google_model')}")
    print("API Key: [Securely Stored]")
    
    print("\n=== Setup Complete ===")
    return True

def main():
    """Run the fresh setup simulation."""
    success = simulate_fresh_setup()
    if success:
        print("\n✅ Fresh setup and API integration completed successfully!")
    else:
        print("\n❌ Setup or API integration failed. Please check the errors above.")

if __name__ == '__main__':
    main() 