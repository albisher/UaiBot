"""
BrowserAutomationTool: Automates browser actions such as navigation, clicking, and form filling for Labeeb agent. Used for web automation tasks.

This tool provides browser automation functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
from typing import Dict, Any, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from src.app.core.ai.tool_base import BaseTool
import tempfile
import os
import sys

logger = logging.getLogger(__name__)

class BrowserAutomationTool(BaseTool):
    """Tool for automating browser actions with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the browser automation tool.
        
        Args:
            config: Optional configuration dictionary
        """
        if config is None:
            config = {}
        super().__init__(
            name="browser_automation",
            description="Tool for automating browser actions with platform-specific optimizations",
            config=config
        )
        self._browser_type = config.get('browser_type', 'chrome')
        self._headless = config.get('headless', False)
        self._timeout = config.get('timeout', 10)  # seconds
        self._driver = None
        self._wait = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize browser driver
            if self._browser_type.lower() == 'chrome':
                options = webdriver.ChromeOptions()
                if self._headless:
                    options.add_argument('--headless')
                self._driver = webdriver.Chrome(options=options)
            elif self._browser_type.lower() == 'brave':
                options = webdriver.ChromeOptions()
                brave_path = self.config.get('brave_path', '/snap/bin/brave')
                options.binary_location = brave_path
                if self._headless:
                    options.add_argument('--headless')
                # Add unique user data dir in /tmp
                user_data_dir = f"/tmp/labeeb_brave_profile_{os.getpid()}"
                options.add_argument(f'--user-data-dir={user_data_dir}')
                # Add flags for Snap/containers compatibility
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                # Advise: User must close all Brave windows before running automation
                self._driver = webdriver.Chrome(options=options)
            elif self._browser_type.lower() == 'firefox':
                options = webdriver.FirefoxOptions()
                if self._headless:
                    options.add_argument('--headless')
                self._driver = webdriver.Firefox(options=options)
            else:
                logger.error(f"Unsupported browser type: {self._browser_type}")
                return False
            
            # Configure wait
            self._wait = WebDriverWait(self._driver, self._timeout)
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize BrowserAutomationTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._driver:
                self._driver.quit()
                self._driver = None
            self._wait = None
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up BrowserAutomationTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'navigate': True,
            'click': True,
            'type': True,
            'get_text': True,
            'get_attribute': True,
            'execute_script': True,
            'screenshot': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'browser_type': self._browser_type,
            'headless': self._headless,
            'timeout': self._timeout,
            'current_url': self._driver.current_url if self._driver else None
        }
        return {**base_status, **tool_status}
    
    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific command.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if not self._driver:
            return {'error': 'Browser not initialized'}
        
        if command == 'navigate':
            return await self._navigate(args)
        elif command == 'click':
            return await self._click_element(args)
        elif command == 'type':
            return await self._type_text(args)
        elif command == 'get_text':
            return await self._get_element_text(args)
        elif command == 'get_attribute':
            return await self._get_element_attribute(args)
        elif command == 'execute_script':
            return await self._execute_javascript(args)
        elif command == 'screenshot':
            return await self._take_screenshot(args)
        else:
            return {'error': f'Unknown command: {command}'}
    
    async def _navigate(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Navigate to a URL.
        
        Args:
            args: Navigation arguments
            
        Returns:
            Dict[str, Any]: Result of navigation
        """
        try:
            if not args or 'url' not in args:
                return {'error': 'Missing url parameter'}
            
            url = args['url']
            self._driver.get(url)
            
            return {
                'status': 'success',
                'action': 'navigate',
                'url': url
            }
        except Exception as e:
            logger.error(f"Error navigating to URL: {e}")
            return {'error': str(e)}
    
    async def _click_element(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Click an element on the page.
        
        Args:
            args: Click arguments
            
        Returns:
            Dict[str, Any]: Result of click
        """
        try:
            if not args or 'selector' not in args:
                return {'error': 'Missing selector parameter'}
            
            selector = args['selector']
            by = args.get('by', By.CSS_SELECTOR)
            
            element = self._wait.until(EC.element_to_be_clickable((by, selector)))
            element.click()
            
            return {
                'status': 'success',
                'action': 'click',
                'selector': selector
            }
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {args.get('selector')}")
            return {'error': 'Element not found or not clickable'}
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return {'error': str(e)}
    
    async def _type_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Type text into an element.
        
        Args:
            args: Text typing arguments
            
        Returns:
            Dict[str, Any]: Result of text typing
        """
        try:
            if not args or 'selector' not in args or 'text' not in args:
                return {'error': 'Missing selector or text parameter'}
            
            selector = args['selector']
            text = args['text']
            by = args.get('by', By.CSS_SELECTOR)
            clear = args.get('clear', True)
            
            element = self._wait.until(EC.presence_of_element_located((by, selector)))
            if clear:
                element.clear()
            element.send_keys(text)
            
            return {
                'status': 'success',
                'action': 'type',
                'selector': selector,
                'text': text
            }
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {args.get('selector')}")
            return {'error': 'Element not found'}
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return {'error': str(e)}
    
    async def _get_element_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get text from an element.
        
        Args:
            args: Element text arguments
            
        Returns:
            Dict[str, Any]: Element text
        """
        try:
            if not args or 'selector' not in args:
                return {'error': 'Missing selector parameter'}
            
            selector = args['selector']
            by = args.get('by', By.CSS_SELECTOR)
            
            element = self._wait.until(EC.presence_of_element_located((by, selector)))
            text = element.text
            
            return {
                'status': 'success',
                'action': 'get_text',
                'selector': selector,
                'text': text
            }
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {args.get('selector')}")
            return {'error': 'Element not found'}
        except Exception as e:
            logger.error(f"Error getting element text: {e}")
            return {'error': str(e)}
    
    async def _get_element_attribute(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get an attribute from an element.
        
        Args:
            args: Element attribute arguments
            
        Returns:
            Dict[str, Any]: Element attribute
        """
        try:
            if not args or 'selector' not in args or 'attribute' not in args:
                return {'error': 'Missing selector or attribute parameter'}
            
            selector = args['selector']
            attribute = args['attribute']
            by = args.get('by', By.CSS_SELECTOR)
            
            element = self._wait.until(EC.presence_of_element_located((by, selector)))
            value = element.get_attribute(attribute)
            
            return {
                'status': 'success',
                'action': 'get_attribute',
                'selector': selector,
                'attribute': attribute,
                'value': value
            }
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {args.get('selector')}")
            return {'error': 'Element not found'}
        except Exception as e:
            logger.error(f"Error getting element attribute: {e}")
            return {'error': str(e)}
    
    async def _execute_javascript(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute JavaScript code.
        
        Args:
            args: JavaScript execution arguments
            
        Returns:
            Dict[str, Any]: Result of JavaScript execution
        """
        try:
            if not args or 'script' not in args:
                return {'error': 'Missing script parameter'}
            
            script = args['script']
            args_list = args.get('args', [])
            
            result = self._driver.execute_script(script, *args_list)
            
            return {
                'status': 'success',
                'action': 'execute_script',
                'result': result
            }
        except Exception as e:
            logger.error(f"Error executing JavaScript: {e}")
            return {'error': str(e)}
    
    async def _take_screenshot(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Take a screenshot of the current page.
        
        Args:
            args: Screenshot arguments
            
        Returns:
            Dict[str, Any]: Screenshot data
        """
        try:
            filename = args.get('filename', 'screenshot.png')
            
            self._driver.save_screenshot(filename)
            
            return {
                'status': 'success',
                'action': 'screenshot',
                'filename': filename
            }
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return {'error': str(e)} 