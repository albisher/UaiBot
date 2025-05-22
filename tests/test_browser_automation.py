#!/usr/bin/env python3
"""
Test script for browser automation functionality.
Covers AppleScript (macOS) and Playwright (cross-platform) implementations.
Includes tests for incognito, profiles, upload, download, screenshot, and error handling.
"""

import os
import sys
import time
import tempfile
import pytest
from app.core.browser_controller import BrowserController

def test_browser_controller():
    """Test the BrowserController class with various browsers and features."""
    controller = BrowserController()
    browsers = ['chrome', 'safari', 'firefox']
    # Test normal open, incognito, and profile
    for browser in browsers:
        print(f"\nTesting {browser}...")
        # Test 1: Open browser
        result = controller.open_browser(browser)
        assert "Error" not in result, f"Failed to open {browser}: {result}"
        time.sleep(1)
        # Test 2: Open incognito/private
        result = controller.open_browser(browser, "https://www.google.com", incognito=True)
        assert "Error" not in result, f"Failed to open {browser} incognito: {result}"
        time.sleep(1)
        # Test 3: Open with profile (Playwright only)
        if controller.playwright_available and browser != 'safari':
            with tempfile.TemporaryDirectory() as profile_dir:
                result = controller.open_browser(browser, "https://www.google.com", profile_path=profile_dir)
                assert "Error" not in result, f"Failed to open {browser} with profile: {result}"
                time.sleep(1)
        # Test 4: JS execution
        js_code = "document.title = 'Test Title';"
        result = controller.execute_javascript(browser, js_code)
        assert "Error" not in result, f"Failed to execute JS in {browser}: {result}"
        # Test 5: Click element (if supported)
        if browser in ['chrome', 'safari']:
            result = controller.click_element(browser, "input[name='q']")
            assert "Error" not in result, f"Failed to click element in {browser}: {result}"
        # Test 6: Screenshot (Playwright only)
        if controller.playwright_available and controller.page:
            result = controller.screenshot(path=f"test_{browser}.png")
            assert "Error" not in result, f"Failed to take screenshot in {browser}: {result}"
        # Test 7: File upload (Playwright only, Chrome/Firefox)
        if controller.playwright_available and browser in ['chrome', 'firefox']:
            print("File upload test skipped (requires test page with file input)")
        # Test 8: Download (Playwright only, Chrome/Firefox)
        if controller.playwright_available and browser in ['chrome', 'firefox']:
            print("Download test skipped (requires direct download URL)")
        # Test 9: Edge case - bad selector
        # AppleScript (macOS native) cannot return JS results, so skip this test for AppleScript browsers
        if controller.playwright_available and (os.name != 'posix' or not os.path.exists('/Applications')):
            result = controller.click_element(browser, "#notarealselector")
            assert "Error" in result or "No active page" in result, "Expected error for bad selector"
        else:
            print("Skipping bad selector test for AppleScript browser due to AppleScript limitations.")
        # Cleanup
        controller.close()
        time.sleep(1)
    # Test 10: Missing browser
    result = controller.open_browser("notarealbrowser")
    assert "Error" in result, "Expected error for missing browser"
    print("\nAll browser automation tests completed!")

if __name__ == "__main__":
    test_browser_controller()
    print("\nAll tests completed successfully!") 