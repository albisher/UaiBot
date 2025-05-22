#!/usr/bin/env python3
# test_uaibot_requests.py

"""
This script tests UaiBot with 10 AI-generated requests that are tailored to
the user's specific system using the enhanced system information detection.

The AI generates different requests based on the detected operating system,
providing a more personalized and relevant experience.
"""

import sys
import os
import random
import time
import platform

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import required modules
try:
    from app.core.ai_handler import AIHandler, get_system_info
    from app.core.shell_handler import ShellHandler
except ImportError as e:
    print(f"Error importing UaiBot modules: {e}")
    print("Make sure you're running this script from the UaiBot directory")
    sys.exit(1)

def run_ai_generated_requests():
    """Run 10 AI-generated requests tailored to the detected system."""
    
    # Initialize components
    print("Initializing UaiBot components...")
    try:
        # Try to use local model first
        ai_handler = AIHandler(model_type="local", quiet_mode=False)
    except Exception as e:
        print(f"Failed to initialize local AI model: {e}")
        print("Falling back to Google AI (if API key is available)...")
        try:
            ai_handler = AIHandler(model_type="google", quiet_mode=False)
        except Exception as e2:
            print(f"Failed to initialize Google AI model: {e2}")
            print("Using mock AI handler for testing...")
            # Create a mock AI handler for testing
            class MockAIHandler:
                def query_ai(self, prompt):
                    return f"MockAI response to: {prompt[:50]}..."
            ai_handler = MockAIHandler()
    
    shell_handler = ShellHandler()
    
    # Get system information
    system_info = get_system_info()
    print(f"\nDetected system: {system_info}\n")
    
    # AI-driven request generation based on system information
    def generate_ai_requests(system_info):
        """Generate tailored requests based on detected system."""
        system_lower = system_info.lower()
        os_name = system_info.split()[0]
        
        # Base requests suitable for any system
        base_requests = [
            f"What operating system am I using? Give details about my environment.",
            f"How much disk space do I have available?",
            f"Show me information about my CPU and RAM.",
            f"What shell am I using and what are some useful shortcuts for it?",
            f"Show me a summary of my system's hardware specifications."
        ]
        
        # Specialized requests based on detected OS
        specialized_requests = []
        
        if "darwin" in system_lower or "macos" in system_lower:
            specialized_requests = [
                f"How do I use Spotlight search efficiently on my Mac?",
                f"What are the best Terminal commands specific to macOS?",
                f"How do I check battery health on my {system_info.split('on')[1].split('with')[0].strip()}?",
                f"What's the best way to manage applications on macOS?",
                f"How can I optimize performance on my Mac?"
            ]
        elif "windows" in system_lower:
            specialized_requests = [
                f"Show me how to use PowerShell effectively on {os_name}.",
                f"What are the best administrative tools in Windows?",
                f"How do I manage startup programs in {os_name}?",
                f"What's the best way to troubleshoot performance issues in Windows?",
                f"How can I optimize my Windows registry safely?"
            ]
        elif "linux" in system_lower:
            if "raspberry" in system_lower:
                specialized_requests = [
                    f"How do I configure GPIO pins on my Raspberry Pi?",
                    f"What are some interesting projects I can build with my Pi?",
                    f"How do I optimize performance on my Raspberry Pi?",
                    f"What's the best way to set up a headless Raspberry Pi?",
                    f"How can I use my Pi as a home automation controller?"
                ]
            else:
                dist_name = os_name
                specialized_requests = [
                    f"What are the best terminal utilities for {dist_name}?",
                    f"How do I manage services with systemd on {dist_name}?",
                    f"What's the most efficient way to update packages on {dist_name}?",
                    f"How can I monitor system performance on Linux?",
                    f"What are some useful bash scripts for automating tasks on {dist_name}?"
                ]
        elif "bsd" in system_lower:
            specialized_requests = [
                f"How do I use the ports collection on {os_name}?",
                f"What's the best way to manage jails on {os_name}?",
                f"How do I configure the pf firewall properly?",
                f"What's the recommended way to update {os_name}?",
                f"How can I optimize ZFS performance on {os_name}?"
            ]
        else:
            # For other operating systems, use more generic but still useful requests
            specialized_requests = [
                f"What are the most useful command line tools for {os_name}?",
                f"How do I check for and install software updates on {os_name}?",
                f"What's the best way to monitor system health on {os_name}?",
                f"How can I improve performance on my {os_name} system?",
                f"What are some common troubleshooting steps for {os_name}?"
            ]
        
        # Combine base and specialized requests
        all_requests = base_requests + specialized_requests
        
        # Ensure we have exactly 10 requests
        if len(all_requests) > 10:
            return random.sample(all_requests, 10)
        elif len(all_requests) < 10:
            # If somehow we have fewer than 10, add some generic ones
            generic_additions = [
                f"What's the current time and timezone on this system?",
                f"List all available network interfaces on my {os_name} system.",
                f"Show me how to check system logs on {os_name}.",
                f"What security best practices should I follow for {os_name}?",
                f"How do I set up multiple user accounts on {os_name}?"
            ]
            all_requests.extend(generic_additions[:10-len(all_requests)])
        
        # Shuffle the requests to mix base and specialized ones
        random.shuffle(all_requests)
        return all_requests
    
    # Generate AI-driven requests based on the detected system
    requests = generate_ai_requests(system_info)
    
    # Print information about what's happening
    print("\nAI has generated 10 tailored requests based on your system:")
    for i, req in enumerate(requests):
        print(f"{i+1}. {req}")
    
    print("=" * 80)
    print("PROCESSING 10 AI-GENERATED REQUESTS TAILORED TO YOUR SYSTEM")
    print("=" * 80)
    
    # Process each request
    for i, request in enumerate(requests):
        print(f"\nREQUEST {i+1}: {request}")
        print("-" * 60)
        
        try:
            # Add system context to the prompt
            prompt = f"You are UaiBot, a helpful AI assistant. The user is running on {system_info}.\n\nUser request: {request}"
            
            # Get AI response
            start_time = time.time()
            response = ai_handler.query_ai(prompt)
            end_time = time.time()
            
            print(f"RESPONSE (took {end_time - start_time:.2f}s):\n{response}\n")
            
        except Exception as e:
            print(f"Error processing request: {e}")
        
        print("-" * 60)
        time.sleep(1)  # Short pause between requests
    
    print("\nTest completed!")

if __name__ == "__main__":
    print("UaiBot AI-Generated Request Test")
    run_ai_generated_requests()
