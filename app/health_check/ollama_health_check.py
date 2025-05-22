import requests
import sys
import os
import json

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "gemma:2b"  # Change as needed

def check_ollama_server():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        if response.status_code == 200:
            print("✅ Ollama server is running.")
            return True, response.json()
        else:
            print(f"❌ Ollama server responded with status code: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Could not connect to Ollama server: {e}")
        return False, None

def check_model_available(tags_json, model_name):
    if not tags_json or "models" not in tags_json:
        print("❌ Could not retrieve model list from Ollama.")
        return False, None
    available_models = [model["name"] for model in tags_json["models"]]
    if model_name in available_models:
        print(f"✅ Model '{model_name}' is available.")
        # Update config with the selected model
        update_config(model_name)
        return True, model_name
    else:
        print(f"❌ Model '{model_name}' is NOT available.")
        if available_models:
            print("Available models:")
            for idx, m in enumerate(available_models):
                print(f"  [{idx+1}] {m}")
            # Interactive selection if possible
            if sys.stdin.isatty():
                try:
                    choice = input("Pick a model to use by number (or press Enter to use the first): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(available_models):
                        selected = available_models[int(choice)-1]
                        print(f"You selected: {selected}")
                        # Update config with the selected model
                        update_config(selected)
                        return True, selected
                    else:
                        print(f"Defaulting to: {available_models[0]}")
                        # Update config with the default model
                        update_config(available_models[0])
                        return True, available_models[0]
                except Exception:
                    print(f"Defaulting to: {available_models[0]}")
                    # Update config with the default model
                    update_config(available_models[0])
                    return True, available_models[0]
            else:
                print(f"Non-interactive mode: defaulting to {available_models[0]}")
                # Update config with the default model
                update_config(available_models[0])
                return True, available_models[0]
        else:
            print("No models are available. Use 'ollama pull <model>' to download one.")
            return False, None

def update_config(model_name):
    """Update the configuration file with the selected model."""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_dir = os.path.join(project_root, 'config')
        config_path = os.path.join(config_dir, 'settings.json')
        
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Load existing config or create new one
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update the model setting
        config['default_ollama_model'] = model_name
        
        # Write the updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"✅ Updated configuration with model: {model_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def main():
    print("--- Ollama Health Check ---")
    ok, tags_json = check_ollama_server()
    if not ok:
        sys.exit(1)
    ok, selected_model = check_model_available(tags_json, MODEL_NAME)
    if ok:
        print(f"Proceeding with model: {selected_model}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 