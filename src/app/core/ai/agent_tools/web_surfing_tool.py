"""
Web surfing tool with A2A, MCP, and SmolAgents compliance.

This tool provides web surfing functionality while following:
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
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class WebSurfingTool(BaseTool):
    """Tool for automated web surfing with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the web surfing tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="web_surfing",
            description="Tool for automated web surfing with platform-specific optimizations",
            config=config
        )
        self._browser_type = config.get('browser_type', 'chrome')
        self._headless = config.get('headless', False)
        self._timeout = config.get('timeout', 10)  # seconds
        self._max_depth = config.get('max_depth', 3)  # maximum depth for surfing
        self._driver = None
        self._wait = None
        self._visited_urls = set()
    
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
            logger.error(f"Failed to initialize WebSurfingTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._driver:
                self._driver.quit()
                self._driver = None
            self._wait = None
            self._visited_urls.clear()
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up WebSurfingTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'surf': True,
            'extract_links': True,
            'extract_content': True,
            'follow_link': True,
            'back': True,
            'forward': True,
            'refresh': True
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
            'max_depth': self._max_depth,
            'current_url': self._driver.current_url if self._driver else None,
            'visited_urls_count': len(self._visited_urls)
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
        
        if command == 'surf':
            return await self._surf_website(args)
        elif command == 'extract_links':
            return await self._extract_links(args)
        elif command == 'extract_content':
            return await self._extract_content(args)
        elif command == 'follow_link':
            return await self._follow_link(args)
        elif command == 'back':
            return await self._navigate_back()
        elif command == 'forward':
            return await self._navigate_forward()
        elif command == 'refresh':
            return await self._refresh_page()
        else:
            return {'error': f'Unknown command: {command}'}
    
    async def _surf_website(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Surf a website starting from a given URL.
        
        Args:
            args: Surfing arguments
            
        Returns:
            Dict[str, Any]: Result of surfing
        """
        try:
            if not args or 'url' not in args:
                return {'error': 'Missing url parameter'}
            
            url = args['url']
            depth = args.get('depth', 1)
            max_links = args.get('max_links', 10)
            
            if depth > self._max_depth:
                return {'error': f'Depth {depth} exceeds maximum allowed depth {self._max_depth}'}
            
            # Navigate to initial URL
            self._driver.get(url)
            self._visited_urls.add(url)
            
            # Extract and follow links
            links = await self._extract_links({'max_links': max_links})
            if 'error' in links:
                return links
            
            results = {
                'status': 'success',
                'action': 'surf',
                'url': url,
                'depth': depth,
                'visited': [url],
                'links_found': len(links.get('links', [])),
                'links': links.get('links', [])
            }
            
            # Recursively follow links if depth > 1
            if depth > 1:
                for link in links.get('links', [])[:max_links]:
                    if link not in self._visited_urls:
                        sub_results = await self._surf_website({
                            'url': link,
                            'depth': depth - 1,
                            'max_links': max_links
                        })
                        if 'error' not in sub_results:
                            results['visited'].extend(sub_results.get('visited', []))
            
            return results
        except Exception as e:
            logger.error(f"Error surfing website: {e}")
            return {'error': str(e)}
    
    async def _extract_links(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract links from the current page.
        
        Args:
            args: Link extraction arguments
            
        Returns:
            Dict[str, Any]: Extracted links
        """
        try:
            max_links = args.get('max_links', 10) if args else 10
            
            # Find all links
            elements = self._driver.find_elements(By.TAG_NAME, 'a')
            links = []
            
            for element in elements[:max_links]:
                href = element.get_attribute('href')
                if href and href.startswith('http'):
                    links.append(href)
            
            return {
                'status': 'success',
                'action': 'extract_links',
                'links': links
            }
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return {'error': str(e)}
    
    async def _extract_content(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract content from the current page.
        
        Args:
            args: Content extraction arguments
            
        Returns:
            Dict[str, Any]: Extracted content
        """
        try:
            selector = args.get('selector', 'body') if args else 'body'
            by = args.get('by', By.CSS_SELECTOR) if args else By.CSS_SELECTOR
            
            element = self._wait.until(EC.presence_of_element_located((by, selector)))
            content = element.text
            
            return {
                'status': 'success',
                'action': 'extract_content',
                'selector': selector,
                'content': content
            }
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {args.get('selector') if args else 'body'}")
            return {'error': 'Element not found'}
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return {'error': str(e)}
    
    async def _follow_link(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Follow a link on the current page.
        
        Args:
            args: Link following arguments
            
        Returns:
            Dict[str, Any]: Result of following link
        """
        try:
            if not args or 'selector' not in args:
                return {'error': 'Missing selector parameter'}
            
            selector = args['selector']
            by = args.get('by', By.CSS_SELECTOR)
            
            element = self._wait.until(EC.element_to_be_clickable((by, selector)))
            href = element.get_attribute('href')
            
            if not href:
                return {'error': 'Element has no href attribute'}
            
            element.click()
            self._visited_urls.add(href)
            
            return {
                'status': 'success',
                'action': 'follow_link',
                'selector': selector,
                'url': href
            }
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {args.get('selector')}")
            return {'error': 'Element not found or not clickable'}
        except Exception as e:
            logger.error(f"Error following link: {e}")
            return {'error': str(e)}
    
    async def _navigate_back(self) -> Dict[str, Any]:
        """Navigate back in browser history.
        
        Returns:
            Dict[str, Any]: Result of navigation
        """
        try:
            self._driver.back()
            
            return {
                'status': 'success',
                'action': 'back',
                'url': self._driver.current_url
            }
        except Exception as e:
            logger.error(f"Error navigating back: {e}")
            return {'error': str(e)}
    
    async def _navigate_forward(self) -> Dict[str, Any]:
        """Navigate forward in browser history.
        
        Returns:
            Dict[str, Any]: Result of navigation
        """
        try:
            self._driver.forward()
            
            return {
                'status': 'success',
                'action': 'forward',
                'url': self._driver.current_url
            }
        except Exception as e:
            logger.error(f"Error navigating forward: {e}")
            return {'error': str(e)}
    
    async def _refresh_page(self) -> Dict[str, Any]:
        """Refresh the current page.
        
        Returns:
            Dict[str, Any]: Result of refresh
        """
        try:
            self._driver.refresh()
            
            return {
                'status': 'success',
                'action': 'refresh',
                'url': self._driver.current_url
            }
        except Exception as e:
            logger.error(f"Error refreshing page: {e}")
            return {'error': str(e)} 