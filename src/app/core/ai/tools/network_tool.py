"""
Network Tool Implementation

This module provides the NetworkTool for network operations,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""
import socket
import requests
import urllib.parse
from typing import Any, Dict, Optional
from .base_tool import BaseTool
from . import ToolRegistry

@ToolRegistry.register
class NetworkTool(BaseTool):
    """Tool for network operations."""
    
    def __init__(self):
        """Initialize the NetworkTool."""
        super().__init__(
            name="NetworkTool",
            description="Handles network operations including HTTP requests, DNS lookups, and connectivity checks"
        )
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a network operation.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        try:
            if not self.validate_input(action, **kwargs):
                return self.handle_error(ValueError("Invalid input"))
            
            if action == "http_request":
                return self._http_request(**kwargs)
            elif action == "dns_lookup":
                return self._dns_lookup(**kwargs)
            elif action == "check_connectivity":
                return self._check_connectivity(**kwargs)
            elif action == "url_parse":
                return self._url_parse(**kwargs)
            else:
                return self.handle_error(ValueError(f"Unknown action: {action}"))
                
        except Exception as e:
            return self.handle_error(e)
    
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available network operations.
        
        Returns:
            Dict[str, str]: Available operations and their descriptions
        """
        return {
            "http_request": "Make an HTTP request",
            "dns_lookup": "Perform DNS lookup",
            "check_connectivity": "Check network connectivity",
            "url_parse": "Parse and analyze URLs"
        }
    
    def _http_request(self, url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, 
                     data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request."""
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
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
    
    def _dns_lookup(self, hostname: str, record_type: str = "A", **kwargs) -> Dict[str, Any]:
        """Perform DNS lookup."""
        try:
            if record_type == "A":
                addresses = socket.gethostbyname_ex(hostname)
                return {
                    "hostname": hostname,
                    "aliases": addresses[1],
                    "addresses": addresses[2]
                }
            else:
                return self.handle_error(ValueError(f"Unsupported record type: {record_type}"))
        except socket.gaierror as e:
            return self.handle_error(e)
    
    def _check_connectivity(self, host: str = "8.8.8.8", port: int = 53, timeout: int = 3, **kwargs) -> Dict[str, Any]:
        """Check network connectivity."""
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return {
                "connected": True,
                "host": host,
                "port": port
            }
        except socket.error as e:
            return {
                "connected": False,
                "host": host,
                "port": port,
                "error": str(e)
            }
    
    def _url_parse(self, url: str, **kwargs) -> Dict[str, Any]:
        """Parse and analyze URLs."""
        try:
            parsed = urllib.parse.urlparse(url)
            return {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "path": parsed.path,
                "params": parsed.params,
                "query": parsed.query,
                "fragment": parsed.fragment,
                "username": parsed.username,
                "password": parsed.password,
                "hostname": parsed.hostname,
                "port": parsed.port
            }
        except Exception as e:
            return self.handle_error(e) 