import requests
import sys
import os
import json
from typing import Tuple, Optional, List, Dict, Any

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma:2b"

def check_ollama_server() -> Tuple[bool, Optional[List[Dict[str, Any]]]]:
    """
    Check if Ollama server is running and return available models.
    
    Returns:
        Tuple[bool, Optional[List[Dict[str, Any]]]]: A tuple containing:
            - bool: Whether the server is running and accessible
            - Optional[List[Dict[str, Any]]]: List of available models if server is running, None otherwise
    """
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "models" in data and isinstance(data["models"], list):
                print("✅ Ollama server is running.")
                return True, data["models"]
            else:
                print("❌ Invalid response format from Ollama server.")
                return False, None
        else:
            print(f"❌ Ollama server responded with status code: {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama server. Please ensure it's running.")
        return False, None
    except requests.exceptions.Timeout:
        print("❌ Connection to Ollama server timed out.")
        return False, None
    except Exception as e:
        print(f"❌ Error checking Ollama server: {str(e)}")
        return False, None

def check_model_available(tags_json: List[Dict[str, Any]], model_name: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a specific model is available in Ollama.
    
    Args:
        tags_json: List of model information from Ollama server
        model_name: Name of the model to check
        
    Returns:
        Tuple[bool, Optional[str]]: A tuple containing:
            - bool: Whether the model is available
            - Optional[str]: Selected model name if available, None otherwise
    """
    if not tags_json:
        print("❌ Could not retrieve model list from Ollama.")
        return False, None
        
    available_models = [model["name"] for model in tags_json]
    if model_name in available_models:
        print(f"✅ Model '{model_name}' is available.")
        update_config(model_name)
        return True, model_name
    else:
        print(f"❌ Model '{model_name}' is NOT available.")
        if available_models:
            print("\nAvailable models:")
            for idx, m in enumerate(available_models):
                print(f"  [{idx+1}] {m}")
                
            # Interactive selection if possible
            if sys.stdin.isatty():
                try:
                    choice = input("\nPick a model to use by number (or press Enter to use the first): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(available_models):
                        selected = available_models[int(choice)-1]
                        print(f"You selected: {selected}")
                        update_config(selected)
                        return True, selected
                    else:
                        print(f"Defaulting to: {available_models[0]}")
                        update_config(available_models[0])
                        return True, available_models[0]
                except Exception as e:
                    print(f"Error during model selection: {e}")
                    print(f"Defaulting to: {available_models[0]}")
                    update_config(available_models[0])
                    return True, available_models[0]
        return False, None

def update_config(model_name: str) -> None:
    """
    Update the configuration file with the selected model.
    
    Args:
        model_name: Name of the model to set as default
    """
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'settings.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
            
        config['default_ollama_model'] = model_name
        config['default_ai_provider'] = 'ollama'
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"✅ Configuration updated with model: {model_name}")
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")

def main():
    print("--- Ollama Health Check ---")
    ok, tags_json = check_ollama_server()
    if not ok:
        sys.exit(1)
    ok, selected_model = check_model_available(tags_json, DEFAULT_MODEL)
    if ok:
        print(f"Proceeding with model: {selected_model}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 