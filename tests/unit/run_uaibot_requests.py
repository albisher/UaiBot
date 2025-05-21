#!/usr/bin/env python3
# run_uaibot_requests.py

"""
This script demonstrates UaiBot's ability to generate and respond to 10 AI-driven
requests tailored to the user's specific system. The requests are dynamically 
generated based on the enhanced system information detection.

The script showcases how UaiBot can provide personalized assistance by:
1. Accurately detecting the user's operating system and environment
2. Generating relevant requests based on the detected system
3. Providing tailored responses that account for the specific system details

Usage: 
    ./run_uaibot_requests.py [--test] [--model local|google] [--delay SECONDS]
    
Examples:
    # Run with local model (Ollama)
    ./run_uaibot_requests.py
    
    # Run with Google AI model
    ./run_uaibot_requests.py --model google
    
    # Test mode (no actual AI queries)
    ./run_uaibot_requests.py --test
    
    # Custom delay between requests
    ./run_uaibot_requests.py --delay 1.5
"""

import sys
import os
import argparse
import random
import time
import platform

# Add the parent directory to the path so we can import UaiBot modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Run AI-generated requests through UaiBot."""
    parser = argparse.ArgumentParser(description='Run AI-generated requests through UaiBot')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no actual AI queries)')
    parser.add_argument('--model', choices=['local', 'google'], default='local', help='AI model to use')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests in seconds')
    args = parser.parse_args()

    # Import modules after adding the parent directory to sys.path
    try:
        from core.ai_handler import AIHandler, get_system_info
    except ImportError as e:
        print(f"Error importing UaiBot modules: {e}")
        sys.exit(1)

    # Get system information
    system_info = get_system_info()
    print(f"System detected: {system_info}\n")

    # Generate AI-driven requests based on system information
    def generate_ai_requests(system_info):
        """Generate 10 AI-driven requests based on system information."""
        system_lower = system_info.lower()
        
        # Detect operating system type from system_info
        if "darwin" in system_lower or "macos" in system_lower:
            os_type = "macos"
        elif "windows" in system_lower:
            os_type = "windows"
        elif "linux" in system_lower:
            if "raspberry" in system_lower:
                os_type = "raspberry_pi"
            else:
                os_type = "linux"
        elif "bsd" in system_lower:
            os_type = "bsd"
        elif "solaris" in system_lower or "sunos" in system_lower:
            os_type = "solaris"
        elif "aix" in system_lower:
            os_type = "aix"
        else:
            os_type = "generic"
            
        # OS-specific request templates
        os_specific_templates = {
            "macos": [
                "How do I use Spotlight search on my Mac?",
                "What's the best way to manage applications on macOS?",
                "Show me how to use Time Machine for backups.",
                "How do I access hidden files in Finder?",
                "What are essential keyboard shortcuts for macOS?",
                "How do I optimize battery life on my Mac?",
                "Show me how to use Homebrew package manager.",
                "How do I monitor system performance with Activity Monitor?",
                "What's the best way to clean up disk space on macOS?",
                "How do I set up multiple desktops on my Mac?"
            ],
            "windows": [
                "How do I use the Windows Task Manager effectively?",
                "What's the best way to manage startup programs in Windows?",
                "Show me how to use PowerShell for system administration.",
                "How do I troubleshoot slow performance in Windows?",
                "What are essential keyboard shortcuts for Windows?",
                "How do I configure Windows Defender for optimal security?",
                "Show me how to use the Registry Editor safely.",
                "How do I set up multiple user accounts in Windows?",
                "What's the best way to back up my Windows system?",
                "How do I manage Windows updates effectively?"
            ],
            "linux": [
                "How do I use package managers like apt, dnf or pacman?",
                "What's the best way to manage services using systemd?",
                "Show me essential bash commands and techniques.",
                "How do I configure SSH for secure remote access?",
                "What are the best terminal multiplexers for Linux?",
                "How do I set up and use cron jobs for automation?",
                "Show me how to manage users and permissions in Linux.",
                "How do I troubleshoot network connectivity issues?",
                "What's the best way to monitor system logs in Linux?",
                "How do I customize my Linux desktop environment?"
            ],
            "raspberry_pi": [
                "How do I set up headless operation on my Raspberry Pi?",
                "What's the best way to manage GPIO pins for projects?",
                "Show me how to optimize Raspberry Pi performance.",
                "How do I set up a media center on my Raspberry Pi?",
                "What are good Raspberry Pi projects for beginners?",
                "How do I configure the camera module on Raspberry Pi?",
                "Show me how to set up a web server on my Pi.",
                "How do I create a home automation system with my Pi?",
                "What's the best way to cool my Raspberry Pi?",
                "How do I use my Raspberry Pi as a retro gaming station?"
            ],
            "bsd": [
                "How do I use the ports collection and packages?",
                "What's the best way to manage services in BSD?",
                "Show me how to configure the pf firewall.",
                "How do I set up jails in FreeBSD?",
                "What are essential commands for BSD system administration?",
                "How do I configure ZFS for optimal performance?",
                "Show me how to upgrade FreeBSD safely.",
                "How do I troubleshoot boot issues in BSD?",
                "What's the best desktop environment for FreeBSD?",
                "How do I optimize network performance in BSD?"
            ],
            "solaris": [
                "How do I use Solaris Zones for virtualization?",
                "What's the best way to manage SMF services?",
                "Show me how to use DTrace for system analysis.",
                "How do I configure ZFS on Solaris?",
                "What are essential commands for Solaris administration?",
                "How do I use the Solaris package manager effectively?",
                "Show me how to configure network interfaces in Solaris.",
                "How do I set up secure remote access with Solaris?",
                "What's the best way to monitor system performance?",
                "How do I optimize disk I/O on Solaris?"
            ],
            "aix": [
                "How do I manage LPARs in AIX?",
                "What's the best way to use SMIT for system administration?",
                "Show me how to manage JFS2 filesystems.",
                "How do I configure network adapters in AIX?",
                "What are essential commands for AIX administration?",
                "How do I use the installp package manager?",
                "Show me how to monitor system resources in AIX.",
                "How do I set up workload partitioning in AIX?",
                "What's the best way to handle system dumps and logs?",
                "How do I optimize performance on my AIX system?"
            ],
            "generic": [
                "What's my operating system and version?",
                "How do I check disk space on this system?",
                "What are the best terminal commands to know?",
                "How can I monitor CPU and memory usage?",
                "What text editors are commonly used on this system?",
                "Show me how to update software on my system.",
                "What's my shell and how do I customize it?",
                "How do I automate tasks with scripts?",
                "What's the best way to manage files and directories?",
                "How can I improve system performance?"
            ]
        }
        
        # Get specific templates for the detected OS
        templates = os_specific_templates.get(os_type, os_specific_templates["generic"])
        
        # Personalize some templates with system info details
        os_name = system_info.split()[0]
        templates = [t.replace("this system", f"{os_name}") for t in templates]
        
        # Shuffle and return 10 requests
        random.shuffle(templates)
        return templates[:10]
        
    # Generate the requests based on detected system
    requests = generate_ai_requests(system_info)

    print("=" * 80)
    print(f"UaiBot AI-Generated Request Demo ({args.model.upper()} MODEL)")
    print("=" * 80)
    print(f"System Information: {system_info}")
    print("\nThe UaiBot AI has generated 10 requests tailored to your system:")
    for i, req in enumerate(requests):
        print(f"{i+1}. {req}")
    print("\n" + "=" * 80)

    if args.test:
        # Test mode - just print what would be sent
        print("\nTEST MODE: Simulating responses without actual AI queries")
        print("-" * 80)
        
        for i, request in enumerate(requests):
            print(f"\nREQUEST {i+1}: {request}")
            print("System context:", system_info)
            
            # Generate a mock response based on the request and system info
            system_type = system_info.split()[0].lower()
            
            if "operating system" in request.lower() or "version" in request.lower():
                mock_response = f"You are running {system_info}."
            elif "check disk" in request.lower() or "disk space" in request.lower():
                if "macos" in system_type or "darwin" in system_type:
                    mock_response = "To check disk space on macOS, use: `df -h`"
                elif "windows" in system_type:
                    mock_response = "To check disk space on Windows, use: `Get-PSDrive` in PowerShell"
                else:
                    mock_response = f"To check disk space on {system_type}, use the appropriate command for your system."
            else:
                mock_response = f"I would provide information about '{request}' specifically for your {system_info}."
                
            print("\nMOCK RESPONSE:")
            print(mock_response)
            print("-" * 60)
    else:
        # Initialize AI handler
        try:
            ai_handler = AIHandler(model_type=args.model)
            print(f"Successfully initialized {args.model.upper()} AI handler")
        except Exception as e:
            print(f"Error initializing AI handler: {e}")
            sys.exit(1)

        # Process each request
        for i, request in enumerate(requests):
            print(f"\nREQUEST {i+1}: {request}")
            print("-" * 60)

            try:
                # Prepare the prompt with system context
                prompt = f"The user is running on {system_info}. Please provide a helpful and specific response to their request taking into account their operating system: {request}"
                
                # Get AI response
                start_time = time.time()
                response = ai_handler.query_ai(prompt)
                elapsed = time.time() - start_time
                
                print(f"RESPONSE (took {elapsed:.2f}s):")
                print(response)
            except Exception as e:
                print(f"Error getting response: {e}")
            
            print("-" * 60)
            if i < len(requests) - 1:
                print(f"Waiting {args.delay} seconds before next request...")
                time.sleep(args.delay)  # Pause between requests

    print("\nCompleted sending requests!")

if __name__ == "__main__":
    main()
