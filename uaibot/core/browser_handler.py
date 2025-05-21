import logging
import webbrowser
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class BrowserHandler:
    """Handles browser-related commands and operations."""
    
    def __init__(self):
        self.supported_browsers = {
            'chrome': 'google-chrome',
            'firefox': 'firefox',
            'safari': 'safari',
            'edge': 'microsoft-edge',
            'brave': 'brave-browser',
            'opera': 'opera'
        }
        
        self.search_engines = {
            'google': 'https://www.google.com/search?q=',
            'duckduckgo': 'https://duckduckgo.com/?q=',
            'bing': 'https://www.bing.com/search?q=',
            'yahoo': 'https://search.yahoo.com/search?p=',
            'duckduck': 'https://duckduckgo.com/?q=',
            'ddg': 'https://duckduckgo.com/?q='
        }
        
        # Common phrases that indicate a search intent
        self.search_indicators = [
            # Direct search commands
            "search for",
            "search",
            "look for",
            "find",
            "query",
            "look up",
            "google",
            
            # Question formats
            "what is",
            "who is",
            "where is",
            "how to",
            "what's",
            "what are",
            "when is",
            "why is",
            "which is",
            
            # Polite requests
            "can you find",
            "could you search",
            "please search",
            "would you search",
            "i want to know",
            "i need to know",
            "tell me about",
            "show me",
            "get information about",
            "find out about",
            
            # Time and weather related
            "what's the weather",
            "weather in",
            "current time in",
            "time in",
            "what time is it in",
            
            # General information requests
            "information about",
            "details about",
            "learn about",
            "read about",
            "know about",
            
            # Action requests
            "how do i",
            "how can i",
            "where can i",
            "what should i",
            "when should i",
            
            # Comparison requests
            "compare",
            "difference between",
            "versus",
            "vs",
            
            # Location based
            "near me",
            "around here",
            "in this area",
            "local",
            
            # News and updates
            "latest news about",
            "recent updates on",
            "what's new in",
            "what's happening with"
        ]
        
        # Common browser-related phrases
        self.browser_indicators = [
            "in",
            "using",
            "with",
            "open",
            "launch",
            "start",
            "run",
            "go to",
            "navigate to",
            "visit",
            "browse to"
        ]
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a browser command."""
        try:
            # Clean the command
            cleaned_command = self._clean_query(command, None)
            # Open the default browser with the cleaned command
            webbrowser.open(f"https://www.google.com/search?q={cleaned_command}")
            return {"status": "success", "message": f"Opened browser with search: {cleaned_command}"}
        except Exception as e:
            return {"status": "error", "message": f"Error executing browser command: {str(e)}"}
    
    def _clean_query(self, query: str, search_engine: Optional[str]) -> str:
        """Clean the search query."""
        # Remove common command words
        words_to_remove = ["search", "look for", "find", "query", "look up", "google"]
        cleaned_query = query.lower()
        for word in words_to_remove:
            cleaned_query = cleaned_query.replace(word, "")
        return cleaned_query.strip()
    
    def _parse_command(self, command: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Parse the command to extract browser, search engine, and query using natural language understanding."""
        command = command.lower()
        
        # Extract browser
        browser = self._extract_browser(command)
        
        # Extract search engine
        search_engine = self._extract_search_engine(command)
        
        # Extract query
        query = self._extract_query(command, search_engine)
        
        return browser, search_engine, query
    
    def _extract_browser(self, command: str) -> Optional[str]:
        """Extract browser name from command using various patterns."""
        # First check for explicit browser mentions
        for browser in self.supported_browsers:
            if browser in command:
                return browser
        
        # Check for browser-related phrases
        for indicator in self.browser_indicators:
            if indicator in command:
                # Look for browser name after the indicator
                parts = command.split(indicator)
                if len(parts) > 1:
                    for browser in self.supported_browsers:
                        if browser in parts[1]:
                            return browser
        
        return None
    
    def _extract_search_engine(self, command: str) -> Optional[str]:
        """Extract search engine from command."""
        # Check for explicit search engine mentions
        for engine in self.search_engines:
            if engine in command:
                return engine
        
        # Check for common variations
        if "duckduck" in command or "ddg" in command:
            return "duckduckgo"
        
        return None
    
    def _extract_query(self, command: str, search_engine: Optional[str]) -> Optional[str]:
        """Extract search query from command using natural language patterns."""
        # Try to find query after search indicators
        for indicator in self.search_indicators:
            if indicator in command:
                parts = command.split(indicator)
                if len(parts) > 1:
                    query = parts[-1].strip()
                    # Clean up the query
                    query = self._clean_query(query, search_engine)
                    if query:
                        return query
        
        # If no search indicator found, try to extract query after search engine
        if search_engine:
            parts = command.split(search_engine)
            if len(parts) > 1:
                query = parts[-1].strip()
                query = self._clean_query(query, search_engine)
                if query:
                    return query
        
        # If still no query found, try to extract meaningful content
        # by removing common words and phrases
        query = self._extract_meaningful_content(command)
        return query if query else None
    
    def _extract_meaningful_content(self, command: str) -> Optional[str]:
        """Extract meaningful content from command when no clear search pattern is found."""
        # Remove browser and search engine references
        cleaned = command
        for browser in self.supported_browsers:
            cleaned = cleaned.replace(browser, "")
        for engine in self.search_engines:
            cleaned = cleaned.replace(engine, "")
        
        # Remove common command words
        for indicator in self.browser_indicators + self.search_indicators:
            cleaned = cleaned.replace(indicator, "")
        
        # Clean up the result
        cleaned = self._clean_query(cleaned, None)
        
        # Only return if we have meaningful content
        return cleaned if len(cleaned.split()) > 0 else None
    
    def _construct_search_url(self, search_engine: str, query: str) -> str:
        """Construct the search URL for the given search engine and query."""
        if search_engine not in self.search_engines:
            raise ValueError(f"Unsupported search engine: {search_engine}")
        
        base_url = self.search_engines[search_engine]
        return f"{base_url}{query.replace(' ', '+')}"
    
    def _open_browser(self, browser: str, url: str) -> None:
        """Open the specified browser with the given URL."""
        try:
            if browser == "default":
                webbrowser.open(url)
                return
                
            if browser not in self.supported_browsers:
                raise ValueError(f"Unsupported browser: {browser}")
            
            browser_name = self.supported_browsers[browser]
            try:
                webbrowser.get(browser_name).open(url)
            except webbrowser.Error:
                # If specific browser not found, use default browser
                logger.warning(f"Could not find {browser}, using default browser")
                webbrowser.open(url)
        except Exception as e:
            logger.error(f"Error opening browser: {str(e)}")
            # Fallback to default browser
            webbrowser.open(url) 