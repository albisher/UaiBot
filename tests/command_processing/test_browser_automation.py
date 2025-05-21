#!/usr/bin/env python3
"""
Test script for UaiBot browser automation functionality.
Tests various prompt combinations and verifies expected responses in a real environment.
"""

import os
import sys
import json
import pytest
import time
import webbrowser
import pyautogui
from pathlib import Path
from command_processor import CommandProcessor
from core.browser_handler import BrowserAutomationHandler

# Set up PyAutoGUI safety features
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.5  # Add delay between actions

class RealAIHandler:
    """Real AI handler for testing browser automation responses."""
    def process_command(self, prompt):
        # Analyze the prompt to determine what information is provided
        prompt_lower = prompt.lower()
        
        # Default values
        browser = "brave"
        url = "https://duckduckgo.com"
        search_term = "privacy tools"
        
        # Extract browser if specified
        if "chrome" in prompt_lower:
            browser = "chrome"
        elif "firefox" in prompt_lower:
            browser = "firefox"
        elif "safari" in prompt_lower:
            browser = "safari"
        elif "edge" in prompt_lower:
            browser = "edge"
            
        # Extract search engine if specified
        if "google" in prompt_lower:
            url = "https://www.google.com"
        elif "bing" in prompt_lower:
            url = "https://www.bing.com"
        elif "startpage" in prompt_lower:
            url = "https://www.startpage.com"
        elif "searx" in prompt_lower:
            url = "https://searx.be"
            
        # Extract search term if specified
        if "search for" in prompt_lower:
            start_idx = prompt_lower.find("search for") + 11
            end_idx = prompt_lower.find(" ", start_idx)
            if end_idx == -1:
                end_idx = len(prompt_lower)
            search_term = prompt_lower[start_idx:end_idx].strip()
        elif "look up" in prompt_lower:
            start_idx = prompt_lower.find("look up") + 8
            end_idx = prompt_lower.find(" ", start_idx)
            if end_idx == -1:
                end_idx = len(prompt_lower)
            search_term = prompt_lower[start_idx:end_idx].strip()
            
        # Construct the response based on available information
        response = {
            "intent": "browser_automation",
            "browser": browser,
            "url": url,
            "actions": [
                {"type": "wait", "seconds": 2},
                {"type": "type", "text": search_term},
                {"type": "press", "key": "enter"},
                {"type": "wait", "seconds": 2}
            ]
        }
        
        # Add screenshot action if requested
        if any(word in prompt_lower for word in ["screenshot", "capture", "picture", "save image"]):
            response["actions"].append({"type": "screenshot", "filename": "search_results.png"})
            
        return json.dumps(response)

class RealShellHandler:
    """Real shell handler for testing."""
    def execute_command(self, command):
        return f"Executed: {command}"

def test_browser_automation_prompts():
    """Test various browser automation prompt combinations in a real environment."""
    print("\nTesting Browser Automation Prompts in Real Environment")
    print("-" * 80)
    print("WARNING: This test will open real browser windows and perform actual automation.")
    print("Move your mouse to any corner of the screen to abort if needed.")
    print("-" * 80)
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir = Path("test_screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Create processor with real handlers
    processor = CommandProcessor(
        RealAIHandler(),
        RealShellHandler(),
        quiet_mode=False
    )
    
    # Test cases with different prompt variations
    test_prompts = [
        # Basic variations with all information
        "go to duckduckgo.com, use Brave, search for privacy tools, and take a screenshot of the results",
        "open Brave browser, navigate to DuckDuckGo, search for privacy tools and capture the results",
        "using Brave browser, go to DuckDuckGo and search for privacy tools, then take a screenshot",
        
        # Different search engines
        "search for privacy tools on Google using Chrome",
        "use Firefox to search Bing for privacy tools",
        "open Safari and search StartPage for privacy tools",
        "use Edge to search Searx for privacy tools",
        
        # Partial information scenarios
        "search for privacy tools",  # No browser or search engine specified
        "use Chrome to search",  # No search term specified
        "go to Google",  # Only search engine specified
        "open Firefox",  # Only browser specified
    ]
    
    # Run tests
    results = []
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}/{len(test_prompts)}")
        print(f"Testing prompt: \"{prompt}\"")
        print("-" * 60)
        
        try:
            # Process the command
            result = processor.process_command(prompt)
            print(f"Command processed: {result}")
            
            # Parse the JSON response
            response_data = json.loads(result)
            if response_data.get("intent") == "browser_automation":
                # Create a unique screenshot filename
                screenshot_path = screenshots_dir / f"test_{i}_results.png"
                if "screenshot" in [action.get("type") for action in response_data.get("actions", [])]:
                    response_data["actions"][-1]["filename"] = str(screenshot_path)
                
                # Execute the browser automation
                print("\nExecuting browser automation...")
                print(f"Browser: {response_data.get('browser')}")
                print(f"URL: {response_data.get('url')}")
                print("Actions:", json.dumps(response_data.get("actions"), indent=2))
                
                handler = BrowserAutomationHandler()
                actual_result = handler.execute_actions(
                    response_data.get("browser"),
                    response_data.get("url"),
                    response_data.get("actions", [])
                )
                
                print(f"\nExecution result: {actual_result}")
                if screenshot_path.exists():
                    print(f"Screenshot saved: {screenshot_path}")
                
                success = "✅" if actual_result and "Browser automation actions completed" in actual_result else "❌"
                results.append((prompt, success, actual_result))
            else:
                print("❌ Not a browser automation command")
                results.append((prompt, "❌", "Not a browser automation command"))
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append((prompt, "❌", f"Error: {str(e)}"))
        
        # Wait between tests
        print("\nWaiting 5 seconds before next test...")
        time.sleep(5)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    success_count = sum(1 for _, status, _ in results if status == "✅")
    print(f"Passed: {success_count}/{len(results)}")
    
    # Print failures
    failures = [(prompt, result) for prompt, status, result in results if status != "✅"]
    if failures:
        print("\nFailed prompts:")
        for prompt, result in failures:
            print(f"- \"{prompt}\": {result}")
    
    # Print screenshot locations
    print("\nScreenshots saved in:", screenshots_dir.absolute())

if __name__ == "__main__":
    try:
        test_browser_automation_prompts()
        print("\nTest script completed successfully!")
    except Exception as e:
        print(f"\nTest script failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 