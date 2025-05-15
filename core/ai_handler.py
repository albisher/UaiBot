# core/ai_handler.py
import os
import json
try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai library not found. Please install it using: pip install google-generativeai")
    genai = None

try:
    import ollama
except ImportError:
    print("ollama library not found. Please install it using: pip install ollama")
    ollama = None

class AIHandler:
    def __init__(self, model_type="local", api_key=None, ollama_base_url="http://localhost:11434", google_model_name=None):
        self.model_type = model_type
        self.ollama_base_url = ollama_base_url
        self.google_model_name = google_model_name
        self.ollama_model_name = None  # Will be set later via set_ollama_model

        if self.model_type == "google":
            if not genai:
                raise ImportError("Google Generative AI SDK not installed.")
            
            # api_key is expected to be provided by the caller (e.g., main.py)
            # after being loaded from config.
            if not api_key:
                raise ValueError("Google API Key not provided to AIHandler. Ensure it is loaded from config and passed correctly.")
            
            # google_model_name is also expected to be provided by the caller.
            if not self.google_model_name:
                raise ValueError("Google model name not provided to AIHandler. Ensure it is loaded from config and passed correctly.")

            self.api_key = api_key # Store the provided API key
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.google_model_name)
            print(f"Google AI Handler initialized with model: {self.google_model_name}")

        elif self.model_type == "ollama" or self.model_type == "local":
            if not ollama:
                raise ImportError("Ollama SDK not installed.")
            try:
                # Fix the connection issue by explicitly using the URL format ollama expects
                if not self.ollama_base_url.startswith('http://') and not self.ollama_base_url.startswith('https://'):
                    self.ollama_base_url = 'http://' + self.ollama_base_url
                    
                # Ensure the URL doesn't have a trailing slash
                if self.ollama_base_url.endswith('/'):
                    self.ollama_base_url = self.ollama_base_url[:-1]
                
                print(f"Connecting to Ollama at: {self.ollama_base_url}")
                self.client = ollama.Client(host=self.ollama_base_url)
                
                # Test connection with a simple API call
                try:
                    models_list = self.client.list()
                    available_models = [m['name'] for m in models_list.get('models', [])]
                except Exception as conn_err:
                    print(f"Failed to list models: {conn_err}")
                    # Try an alternative approach by directly using httpx
                    import httpx
                    with httpx.Client() as client:
                        response = client.get(f"{self.ollama_base_url}/api/tags")
                        if response.status_code == 200:
                            models_data = response.json()
                            available_models = [m['name'] for m in models_data.get('models', [])]
                        else:
                            raise ConnectionError(f"Failed to connect to Ollama API: Status code {response.status_code}")
                
                if not available_models:
                    print(f"No Ollama models found at {self.ollama_base_url}. Please ensure Ollama is running and models are installed.")
                    # You might want to raise an error here or handle it differently
                elif self.ollama_model_name not in available_models and ":" not in self.ollama_model_name: # if model name doesn't specify version
                    # try to find a version of the model
                    found_model = next((m for m in available_models if m.startswith(self.ollama_model_name + ":")), None)
                    if found_model:
                        self.ollama_model_name = found_model
                    else:
                        print(f"Warning: Default Ollama model '{self.ollama_model_name}' not found. Using first available model: {available_models[0]}")
                        self.ollama_model_name = available_models[0]

                print(f"Ollama AI Handler initialized. Using model: {self.ollama_model_name} from {self.ollama_base_url}")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Ollama at {self.ollama_base_url}. Ensure Ollama is running. Error: {e} - {e.__class__.__name__}")
        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}. Choose 'google' or 'ollama'.")

    def query_ai(self, prompt):
        """
        Queries the configured AI model with the provided prompt.
        Returns the AI's response as a string.
        """
        try:
            if self.model_type == "google":
                if not self.model:
                    raise ValueError("Google AI model not initialized")
                
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text.strip()
                else:
                    return "Error: Google AI returned empty response"
                    
            elif self.model_type == "ollama" or self.model_type == "local":
                if not hasattr(self, 'client') or not self.client:
                    raise ValueError("Ollama client not initialized")
                
                response = self.client.generate(model=self.ollama_model_name, prompt=prompt)
                if response and "response" in response:
                    return response["response"].strip()
                else:
                    return "Error: Ollama returned invalid response format"
            else:
                return f"Error: Unsupported AI provider: {self.model_type}"
                
        except Exception as e:
            return f"Error: Failed to get AI response: {str(e)}"

    def set_ollama_model(self, model_name):
        if self.model_type == "ollama" or self.model_type == "local":
            self.ollama_model_name = model_name
            print(f"Ollama model set to: {self.ollama_model_name}")
            # Optionally, verify model exists with self.client.list()
        else:
            print("Warning: Cannot set Ollama model. Current model_type is not 'ollama' or 'local'.")

    def set_google_model(self, model_name):
        if self.model_type == "google":
            self.google_model_name = model_name
            try:
                self.model = genai.GenerativeModel(self.google_model_name)
                print(f"Google AI model set to: {self.google_model_name}")
            except Exception as e:
                print(f"Error setting Google AI model: {e}")
        else:
            print("Warning: Cannot set Google model. Current model_type is not 'google'.")

# Example usage (for testing purposes, remove or comment out for production):
# if __name__ == '__main__':
#     # Test Ollama
#     try:
#         ollama_handler = AIHandler(model_type="ollama")
#         ollama_response = ollama_handler.query_ai("Why is the sky blue?")
#         print(f"Ollama Response: {ollama_response}")
#     except Exception as e:
#         print(f"Ollama test failed: {e}")

    # Test Google AI (ensure GOOGLE_API_KEY is set or in config/settings.json)
    # try:
    #     google_handler = AIHandler(model_type="google") # api_key will be auto-loaded
    #     google_response = google_handler.query_ai("What is the capital of France?")
    #     print(f"Google Response: {google_response}")
    # except Exception as e:
    #     print(f"Google AI test failed: {e}")
