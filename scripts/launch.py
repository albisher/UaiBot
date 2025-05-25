#!/usr/bin/env python3
"""
UaiBot CLI Launcher

This script launches the UaiBot CLI application.
It handles command processing and model management.
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from uaibot.core.ai.uaibot_agent import UaiAgent
from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.cache import Cache
from uaibot.core.auth_manager import AuthManager
from uaibot.core.plugin_manager import PluginManager

def print_help():
    """Print help message with available commands."""
    print("\nAvailable commands:")
    print("  help              - Show this help message")
    print("  exit              - Exit the application")
    print("  models            - List available models")
    print("  switch-model <provider> <model> - Switch to a different model")
    print("\nExample commands:")
    print("  weather in London")
    print("  weather forecast Paris")
    print("  weather alert New York")
    print("  switch-model ollama gemma3:4b")
    print("  switch-model huggingface gpt2")

async def handle_model_command(command: str, model_manager: ModelManager) -> None:
    """Handle model-related commands."""
    parts = command.split()
    if len(parts) == 1 and parts[0] == "models":
        # List available models
        models = model_manager.list_available_models()
        print("\nAvailable models:")
        for provider, provider_models in models.items():
            print(f"\n{provider.upper()}:")
            for model in provider_models:
                print(f"  - {model}")
    elif len(parts) == 3 and parts[0] == "switch-model":
        # Switch model
        provider = parts[1]
        model = parts[2]
        try:
            model_manager.set_model(provider, model)
            print(f"Switched to {model} on {provider}")
        except Exception as e:
            print(f"Error switching model: {str(e)}")
    else:
        print("Invalid model command. Use 'help' for available commands.")

async def main():
    """Main entry point for CLI."""
    # Initialize components
    config = ConfigManager()
    model_manager = ModelManager(config)
    cache = Cache()
    auth_manager = AuthManager()
    plugin_manager = PluginManager()
    
    # Initialize agent
    agent = UaiAgent(
        config=config,
        model_manager=model_manager,
        cache=cache,
        auth_manager=auth_manager,
        plugin_manager=plugin_manager
    )
    
    print("Welcome to UaiBot CLI!")
    print("Type 'help' for available commands.")
    
    while True:
        try:
            # Get command
            command = input("\n> ").strip()
            
            # Handle special commands
            if command.lower() == "exit":
                break
            elif command.lower() == "help":
                print_help()
                continue
            elif command.lower() == "models" or command.lower().startswith("switch-model"):
                await handle_model_command(command, model_manager)
                continue
            
            # Process command
            result = await agent.plan_and_execute(command)
            
            # Display result
            if isinstance(result, dict) and "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Result: {result}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
