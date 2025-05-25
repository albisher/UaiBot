#!/usr/bin/env python3
"""
Labeeb (لبيب) CLI Launcher

This script launches the Labeeb CLI application.
It handles command processing, model management, and output formatting.
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
from uaibot.utils.output_style_manager import OutputStyleManager

style_mgr = OutputStyleManager()

# Professional, emoji-rich prompt
PROMPT = "🤖 Labeeb > "

# Welcome message
WELCOME = style_mgr.format_header("Welcome to Labeeb (لبيب) CLI!", emoji_key="robot")
HELP = style_mgr.format_box(
    "Available commands:\n  help              - Show this help message\n  exit              - Exit the application\n  models            - List available models\n  switch-model <provider> <model> - Switch to a different model\n\nExample commands:\n  weather in London\n  weather forecast Paris\n  weather alert New York\n  switch-model ollama gemma3:4b\n  switch-model huggingface gpt2",
    title="Help"
)

def print_help():
    print(HELP)

async def handle_model_command(command: str, model_manager: ModelManager) -> None:
    parts = command.split()
    if len(parts) == 1 and parts[0] == "models":
        models = model_manager.list_available_models()
        print(style_mgr.format_header("Available models:", emoji_key="robot"))
        for provider, provider_models in models.items():
            print(style_mgr.format_status_line(f"{provider.upper()}:", status_key="info"))
            for model in provider_models:
                print(style_mgr.format_status_line(f"  - {model}", status_key="info"))
    elif len(parts) == 3 and parts[0] == "switch-model":
        provider = parts[1]
        model = parts[2]
        try:
            model_manager.set_model(provider, model)
            print(style_mgr.format_status_line(f"Switched to {model} on {provider}", status_key="success"))
        except Exception as e:
            print(style_mgr.format_status_line(f"Error switching model: {str(e)}", status_key="error"))
    else:
        print(style_mgr.format_status_line("Invalid model command. Use 'help' for available commands.", status_key="warning"))

async def main():
    # Initialize components
    config = ConfigManager()
    model_manager = ModelManager(config)
    cache = Cache()
    auth_manager = AuthManager()
    plugin_manager = PluginManager()
    agent = UaiAgent(
        config=config,
        model_manager=model_manager,
        cache=cache,
        auth_manager=auth_manager,
        plugin_manager=plugin_manager
    )
    print(WELCOME)
    print(style_mgr.format_status_line("Type 'help' for available commands.", status_key="info"))
    while True:
        try:
            # Prefix user input with emoji
            command = input(f"\n🤔 You > ").strip()
            if command.lower() == "exit":
                print(style_mgr.format_status_line("Goodbye!", status_key="info"))
                break
            elif command.lower() == "help":
                print_help()
                continue
            elif command.lower() == "models" or command.lower().startswith("switch-model"):
                await handle_model_command(command, model_manager)
                continue
            result = await agent.plan_and_execute(command)
            # Output handling: always show something meaningful
            if isinstance(result, dict):
                if "error" in result and result["error"]:
                    print(style_mgr.format_status_line(result["error"], status_key="error"))
                elif "output" in result and result["output"]:
                    print(style_mgr.format_status_line(result["output"], status_key="success"))
                elif "raw" in result and result["raw"]:
                    print(style_mgr.format_status_line(result["raw"], status_key="warning"))
                else:
                    print(style_mgr.format_status_line(str(result), status_key="info"))
            elif isinstance(result, str):
                print(style_mgr.format_status_line(result, status_key="info"))
            elif result is not None:
                print(style_mgr.format_status_line(str(result), status_key="info"))
        except KeyboardInterrupt:
            print("\n" + style_mgr.format_status_line("Exiting...", status_key="info"))
            break
        except Exception as e:
            print(style_mgr.format_status_line(f"Error: {str(e)}", status_key="error"))

if __name__ == "__main__":
    asyncio.run(main())
