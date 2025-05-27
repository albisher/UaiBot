"""
Web Tool Implementation

This module provides the WebTool for web-related operations,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, Optional
from .base_tool import BaseTool
from . import ToolRegistry

@ToolRegistry.register
class WebTool(BaseTool):
    """Tool for web-related operations."""
    
    def __init__(self):
        """Initialize the WebTool."""
        super().__init__(
            name="WebTool",
            description="Handles web-related operations including web scraping, content extraction, and URL validation"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a web-related operation.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        try:
            if not self.validate_input(action, **kwargs):
                return self.handle_error(ValueError("Invalid input"))
            
            if action == "fetch_url":
                return self._fetch_url(**kwargs)
            elif action == "extract_content":
                return self._extract_content(**kwargs)
            elif action == "validate_url":
                return self._validate_url(**kwargs)
            elif action == "search_web":
                return self._search_web(**kwargs)
            else:
                return self.handle_error(ValueError(f"Unknown action: {action}"))
                
        except Exception as e:
            return self.handle_error(e)
    
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available web-related operations.
        
        Returns:
            Dict[str, str]: Available operations and their descriptions
        """
        return {
            "fetch_url": "Fetch content from a URL",
            "extract_content": "Extract specific content from a web page",
            "validate_url": "Validate a URL format and accessibility",
            "search_web": "Search the web for specific content"
        }
    
    def _fetch_url(self, url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
                  params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Fetch content from a URL."""
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=kwargs.get("timeout", 30)
            )
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "url": response.url
            }
        except requests.RequestException as e:
            return self.handle_error(e)
    
    def _extract_content(self, html: str, selector: str, **kwargs) -> Dict[str, Any]:
        """Extract specific content from a web page."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.select(selector)
            
            results = []
            for element in elements:
                results.append({
                    "text": element.get_text(strip=True),
                    "html": str(element),
                    "attributes": dict(element.attrs)
                })
            
            return {
                "elements": results,
                "count": len(results)
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _validate_url(self, url: str, check_accessible: bool = True, **kwargs) -> Dict[str, Any]:
        """Validate a URL format and accessibility."""
        try:
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                return {
                    "valid": False,
                    "error": "URL must start with http:// or https://"
                }
            
            # Check accessibility if requested
            if check_accessible:
                response = requests.head(url, timeout=kwargs.get("timeout", 5))
                return {
                    "valid": True,
                    "accessible": True,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
            
            return {
                "valid": True,
                "accessible": None
            }
        except requests.RequestException as e:
            return {
                "valid": True,
                "accessible": False,
                "error": str(e)
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _search_web(self, query: str, engine: str = "google", **kwargs) -> Dict[str, Any]:
        """Search the web for specific content."""
        try:
            # This is a placeholder implementation
            # In a real implementation, you would integrate with search engine APIs
            return {
                "query": query,
                "engine": engine,
                "results": [],
                "error": "Search engine integration not implemented"
            }
        except Exception as e:
            return self.handle_error(e) 