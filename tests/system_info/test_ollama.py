#!/usr/bin/env python3

import sys
import os
import json
from app.core.ai_handler import AIHandler

def main():
    print("Testing Ollama connection...")
    
    try:
        # Load config
        try:
            with open('config/settings.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print("Error: config/settings.json not found.")
            return 1
            
        # Get Ollama settings
        ollama_base_url = config.get("ollama_base_url", "http://127.0.0.1:11434")
        default_ollama_model = config.get("default_ollama_model", "gemma3:4b")
        
        print(f"Using Ollama base URL: {ollama_base_url}")
        print(f"Using Ollama model: {default_ollama_model}")
        
        # Initialize Ollama AI handler
        try:
            ai_handler = AIHandler(model_type="ollama", ollama_base_url=ollama_base_url)
            ai_handler.set_ollama_model(default_ollama_model)
        except Exception as e:
            print(f"Error initializing Ollama AI Handler: {str(e)}")
            return 1
            
        # Test with a simple query
        print("Testing AI query...")
        response = ai_handler.query_ai("Say hello in 5 words or less")
        print(f"Ollama Response: {response}")
        
        print("Ollama test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())