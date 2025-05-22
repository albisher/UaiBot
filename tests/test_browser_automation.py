#!/usr/bin/env python3
"""
Test script for browser automation functionality.
Tests opening browsers, executing JavaScript, and clicking elements.
"""

import os
import sys
import time
import pytest
from app.core.browser_controller import BrowserController

def test_browser_controller():
    """Test the BrowserController class."""
    controller = BrowserController()
    
    # Test opening browsers
    browsers = ['chrome', 'safari', 'firefox']
    for browser in browsers:
        print(f"\nTesting {browser}...")
        
        # Test 1: Open browser
        result = controller.open_browser(browser)
        print(f"Open browser result: {result}")
        assert "Error" not in result
        time.sleep(2)  # Wait for browser to open
        
        # Test 2: Open browser with URL
        result = controller.open_browser(browser, "https://www.google.com")
        print(f"Open browser with URL result: {result}")
        assert "Error" not in result
        time.sleep(2)  # Wait for navigation
        
        # Test 3: Execute JavaScript
        js_code = "document.title = 'Test Title';"
        result = controller.execute_javascript(browser, js_code)
        print(f"Execute JavaScript result: {result}")
        if browser in ['chrome', 'safari']:
            assert "Error" not in result
        time.sleep(1)
        
        # Test 4: Click element
        if browser in ['chrome', 'safari']:
            result = controller.click_element(browser, "input[name='q']")
            print(f"Click element result: {result}")
            assert "Error" not in result
            time.sleep(1)
    
    # Cleanup
    controller.close()

if __name__ == "__main__":
    try:
        test_browser_controller()
        print("\n✅ All browser automation tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc() 