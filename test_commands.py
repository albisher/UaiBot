#!/usr/bin/env python3
from uaibot.main import UaiBot

def test_commands():
    # Initialize UaiBot in debug mode
    bot = UaiBot(debug=True, mode='command', fast_mode=True)
    
    # First 10 commands from patch1_shuf.txt
    commands = [
        "check development health",
        "show me testing statistics",
        "list all connected displays",
        "check configuration status",
        "show me the test coverage",
        "show me the user preferences",
        "show me security logs",
        "verify code quality",
        "show me the keyboard layout",
        "find duplicate files in my Pictures folder"
    ]
    
    print("Testing UaiBot commands...")
    print("-" * 50)
    
    for cmd in commands:
        print(f"\nTesting command: {cmd}")
        print("-" * 30)
        try:
            response = bot.process_single_command(cmd)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 30)

if __name__ == "__main__":
    test_commands() 