import requests
import sys

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
                        return True, selected
                    else:
                        print(f"Defaulting to: {available_models[0]}")
                        return True, available_models[0]
                except Exception:
                    print(f"Defaulting to: {available_models[0]}")
                    return True, available_models[0]
            else:
                print(f"Non-interactive mode: defaulting to {available_models[0]}")
                return True, available_models[0]
        else:
            print("No models are available. Use 'ollama pull <model>' to download one.")
            return False, None

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