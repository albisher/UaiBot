import json
import argparse
import os
import sys
from core.ai_handler import AIHandler
from core.shell_handler import ShellHandler
from core.utils import load_config, get_project_root
from platform.platform_manager import PlatformManager

def process_command(user_input, ai_handler, shell_handler): # Added function to handle single command
    """Processes a single user command."""
    if not user_input.strip():
        print("Please enter a command.")
        return

    prompt_for_ai = (
        f"User request: '{user_input}'. "
        "Based on this request, suggest a single, common, and safe Linux shell command. "
        "Avoid generating complex command chains (e.g., using ';', '&&', '||') unless the user's request explicitly implies it and it's a very common pattern. "
        "Do not provide explanations, only the command itself. "
        "If the request is ambiguous or potentially unsafe to translate into a shell command, respond with 'Error: Cannot fulfill request safely.'"
    )

    ai_response_command = ai_handler.query_ai(prompt_for_ai)
    print(f"AI Suggested Command: {ai_response_command}")

    if ai_response_command and not ai_response_command.startswith("Error:"):
        safety_level = shell_handler.check_command_safety_level(ai_response_command)
        print(f"Command safety level: {safety_level}")

        execute_command = False
        force_shell_execution = False

        if safety_level == 'POTENTIALLY_DANGEROUS':
            print(f"WARNING: The AI suggested a potentially dangerous command: {ai_response_command}")
            if shell_handler.safe_mode:
                print("Execution blocked by safe_mode. To execute, disable 'shell_safe_mode' in config/settings.json and restart.")
            else: # Not safe_mode
                user_confirm = input("This command is potentially dangerous. Execute? (yes/no): ").strip().lower()
                if user_confirm == 'yes':
                    execute_command = True
                    # If shell=True is also needed, it should be caught by REQUIRES_SHELL_TRUE_ASSESSMENT
                    # or the user should be aware that dangerous commands might run with shell if necessary
                    # when safe_mode is off.
                else:
                    print("Execution cancelled by user.")
        elif safety_level == 'NOT_IN_WHITELIST':
            print(f"WARNING: The AI suggested command '{ai_response_command}' is not in the whitelist.")
            if shell_handler.safe_mode:
                print("Safe_mode is ON.")
                user_confirm = input("Try executing with shell=True (requires careful review; shell_handler might still block it if safe_mode is ON)? (yes/no): ").strip().lower()
                if user_confirm == 'yes':
                    execute_command = True
                    force_shell_execution = True
                    print("Note: shell_safe_mode is ON. The shell handler may still prevent execution with shell=True.")
                else:
                    print("Execution cancelled by user.")
            else: # Not safe_mode
                user_confirm = input("Execute with shell=True? (yes/no): ").strip().lower()
                if user_confirm == 'yes':
                    execute_command = True
                    force_shell_execution = True
                else:
                    print("Execution cancelled by user.")
        elif safety_level == 'REQUIRES_SHELL_TRUE_ASSESSMENT':
            print(f"WARNING: Command '{ai_response_command}' may require shell=True due to its structure.")
            if shell_handler.safe_mode:
                print("Safe_mode is ON.")
                user_confirm = input("Try executing with shell=True (requires careful review; shell_handler might still block it if safe_mode is ON)? (yes/no): ").strip().lower()
                if user_confirm == 'yes':
                    execute_command = True
                    force_shell_execution = True
                    print("Note: shell_safe_mode is ON. The shell handler may still prevent execution with shell=True.")
                else:
                    print("Execution cancelled by user.")
            else: # Not safe_mode
                user_confirm = input("Execute with shell=True? (yes/no): ").strip().lower()
                if user_confirm == 'yes':
                    execute_command = True
                    force_shell_execution = True
                else:
                    print("Execution cancelled by user.")
        elif safety_level == 'EMPTY':
            print("AI did not return a command.")
        else: # SAFE
            execute_command = True

        if execute_command:
            print(f"Executing command: {ai_response_command}")
            command_output = shell_handler.execute_command(ai_response_command, force_shell=force_shell_execution)
            print(f"Command Output:\n{command_output}")
        
    elif ai_response_command.startswith("Error:"):
        print(f"AI Error: {ai_response_command}")
        print("Skipping execution due to AI error.")
    else:
        print("AI did not return a valid command string.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UaiBot: AI-powered shell assistant.") # Added argument parser
    parser.add_argument("-c", "--command", type=str, help="Execute a single command and exit.")
    args = parser.parse_args()

    config_data = load_config() # Renamed to avoid conflict with 'config' module if ever imported
    if not config_data:
        exit(1)

    # --- Configuration Loading with Environment Variable Fallbacks ---
    ai_provider = config_data.get("default_ai_provider")
    if not ai_provider:
        print("Error: No default_ai_provider specified in config/settings.json.")
        print("Please set 'default_ai_provider' to either 'ollama' or 'google'.")
        exit(1)
        
    google_api_key = config_data.get("google_api_key")
    if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
        print("Google API key not in config or is placeholder, checking GOOGLE_API_KEY env var...")
        env_key = os.getenv("GOOGLE_API_KEY")
        if env_key:
            google_api_key = env_key
            print("Using Google API key from GOOGLE_API_KEY environment variable.")
        # If still not found or placeholder, it will be checked later if provider is 'google' or for fallback

    ollama_base_url = config_data.get("ollama_base_url")
    if not ollama_base_url:
        print("Ollama base URL not in config, checking OLLAMA_BASE_URL env var...")
        env_ollama_url = os.getenv("OLLAMA_BASE_URL")
        if env_ollama_url:
            ollama_base_url = env_ollama_url
            print("Using Ollama base URL from OLLAMA_BASE_URL environment variable.")
        else:
            ollama_base_url = "http://localhost:11434" # Default
            print(f"Warning: No ollama_base_url specified in config or OLLAMA_BASE_URL env var. Using default: {ollama_base_url}")
    
    default_ollama_model = config_data.get("default_ollama_model")
    if not default_ollama_model:
        print("Default Ollama model not in config, checking DEFAULT_OLLAMA_MODEL env var...")
        env_ollama_model = os.getenv("DEFAULT_OLLAMA_MODEL")
        if env_ollama_model:
            default_ollama_model = env_ollama_model
            print("Using default Ollama model from DEFAULT_OLLAMA_MODEL environment variable.")
        
    default_google_model = config_data.get("default_google_model")
    if not default_google_model:
        print("Default Google model not in config, checking DEFAULT_GOOGLE_MODEL env var...")
        env_google_model = os.getenv("DEFAULT_GOOGLE_MODEL")
        if env_google_model:
            default_google_model = env_google_model
            print("Using default Google model from DEFAULT_GOOGLE_MODEL environment variable.")
        
    shell_safe_mode = config_data.get("shell_safe_mode", True)
    shell_dangerous_check = config_data.get("shell_dangerous_check", True)

    print(f"Using AI provider: {ai_provider}")
    print(f"Shell safe_mode: {shell_safe_mode}, dangerous_command_check: {shell_dangerous_check}")

    # Initialize AI handler with error handling and fallback
    ai_handler = None
    try:
        if ai_provider == "google":
            if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
                print("Error: Google API key not configured. Please set it in config/settings.json or as GOOGLE_API_KEY environment variable.")
                exit(1)
            if not default_google_model:
                print("Error: No default_google_model specified. Please set it in config/settings.json or as DEFAULT_GOOGLE_MODEL environment variable.")
                exit(1)
            ai_handler = AIHandler(model_type="google", api_key=google_api_key, google_model_name=default_google_model)
        elif ai_provider == "ollama":
            if not default_ollama_model: # Check if model name is available
                print("Error: No default_ollama_model specified. Please set it in config/settings.json or as DEFAULT_OLLAMA_MODEL environment variable.")
                exit(1)
            try:
                ai_handler = AIHandler(model_type="ollama", ollama_base_url=ollama_base_url)
                ai_handler.set_ollama_model(default_ollama_model) 
            except ConnectionError as e:
                print(f"Error connecting to Ollama (URL: {ollama_base_url}): {e}")
                print("Ollama connection failed. Is Ollama installed and running?")
                
                if google_api_key and google_api_key != "YOUR_GOOGLE_API_KEY" and default_google_model:
                    print("Attempting to fall back to Google AI provider...")
                    try:
                        ai_handler = AIHandler(model_type="google", api_key=google_api_key, google_model_name=default_google_model)
                        print(f"Successfully connected to Google AI with model: {default_google_model} as fallback.")
                        ai_provider = "google" # Update the effective AI provider
                    except Exception as google_fallback_e:
                        print(f"Error initializing Google AI as fallback: {google_fallback_e}")
                        # ai_handler remains None or as it was, will be caught by the final check
                else:
                    print("Google API key and/or default Google model not configured for fallback.")
                
                if not ai_handler: # If fallback failed or wasn't attempted/configured
                    print("ERROR: Could not connect to Ollama, and fallback to Google AI was not successful or not configured.")
                    print("Please either:")
                    print(f"1. Start Ollama (expected at {ollama_base_url}) by running 'ollama serve' in another terminal, OR")
                    print("2. Configure a valid Google API key and model in config/settings.json or environment variables.")
                    exit(1)
        else:
            print(f"Error: Unknown AI provider '{ai_provider}' in config/settings.json.")
            print("Please set 'default_ai_provider' to either 'ollama' or 'google'.")
            exit(1)

    except ImportError as e:
        print(f"Error initializing AI Handler: {e} - {e.__class__.__name__}")
        print("Please ensure the required libraries (google-generativeai or ollama) are installed.")
        print("Run: pip install google-generativeai ollama")
        exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e} - {e.__class__.__name__}")
        exit(1)
    except ConnectionError as e: # This specific catch might be less relevant now or could be for other components
        print(f"Connection Error: {e} - {e.__class__.__name__}")
        print("Please ensure Ollama is running. Try starting it with 'ollama serve' in another terminal.")
        exit(1)

    if not ai_handler: # Final check to ensure AI Handler is initialized
        print("Fatal: AI Handler could not be initialized. Please check your configuration, AI provider status, and previous error messages.")
        exit(1)

    shell_handler = ShellHandler(safe_mode=shell_safe_mode, enable_dangerous_command_check=shell_dangerous_check)

    if args.command: # If command is provided via CLI
        process_command(args.command, ai_handler, shell_handler)
        print("UaiBot single command execution finished.")
    else: # Original interactive loop
        try:
            while True:
                user_input = input("Enter your command (or type 'exit' to quit): ")
                if user_input.lower() == 'exit':
                    break
                process_command(user_input, ai_handler, shell_handler) # Use the new function

        except KeyboardInterrupt:
            print("\nExiting UaiBot.")
        finally:
            print("UaiBot session ended.")