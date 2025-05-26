"""
Browser integration for Labeeb.
This version uses the platform-specific browser handler from platform_core.
"""
from labeeb.platform_core.platform_manager import PlatformManager

class BrowserHandler:
    """Handler for browser interactions."""
    
    def __init__(self, shell_handler=None):
        """Initialize the browser handler.
        
        Args:
            shell_handler: Optional shell handler instance for executing commands
        """
        # Get platform-specific browser handler
        platform_manager = PlatformManager()
        self._platform_handler = platform_manager.get_handler('browser')
        
        if self._platform_handler is None:
            raise NotImplementedError(f"No browser handler available for platform {platform_manager.get_platform()}")
            
        # Initialize platform handler with our settings
        self._platform_handler.shell_handler = shell_handler
        
    def get_content(self, browser_name=None):
        """Get content from browser tabs (titles and URLs).
        
        Args:
            browser_name: Specific browser to target ("chrome", "firefox", "safari", "edge")
            
        Returns:
            Formatted browser content or error message
        """
        return self._platform_handler.get_content(browser_name)
        
    def perform_search(self, url, query, wait_time=2.0):
        """Open the default browser, navigate to a URL, and perform a search.
        
        Args:
            url: The URL to open (e.g., 'https://www.google.com')
            query: The search query to type
            wait_time: Seconds to wait for the browser to load
            
        Returns:
            Status message
        """
        return self._platform_handler.perform_search(url, query, wait_time)
        
    def execute_actions(self, browser, url, actions):
        """Execute a series of browser automation actions.
        
        Args:
            browser: Browser to use
            url: URL to navigate to
            actions: List of actions to perform
            
        Returns:
            Status message
        """
        return self._platform_handler.execute_actions(browser, url, actions)
