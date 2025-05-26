"""
Network tool with A2A, MCP, and SmolAgents compliance.

This tool provides network operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import socket
import aiohttp
import dns.resolver
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class NetworkTool(BaseTool):
    """Tool for performing network operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the network tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="network",
            description="Tool for performing network operations",
            config=config
        )
        self._timeout = config.get('timeout', 30)
        self._max_retries = config.get('max_retries', 3)
        self._max_redirects = config.get('max_redirects', 5)
        self._max_connections = config.get('max_connections', 100)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._session = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Create HTTP session
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._timeout),
                max_redirects=self._max_redirects,
                connector=aiohttp.TCPConnector(limit=self._max_connections)
            )
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize NetworkTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up NetworkTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'ping': True,
            'dns_lookup': True,
            'port_scan': True,
            'http_request': True,
            'history': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'timeout': self._timeout,
            'max_retries': self._max_retries,
            'max_redirects': self._max_redirects,
            'max_connections': self._max_connections,
            'history_size': len(self._operation_history),
            'max_history': self._max_history,
            'session_active': self._session is not None
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
        if command == 'ping':
            return await self._ping(args)
        elif command == 'dns_lookup':
            return await self._dns_lookup(args)
        elif command == 'port_scan':
            return await self._port_scan(args)
        elif command == 'http_request':
            return await self._http_request(args)
        elif command == 'get_history':
            return await self._get_history()
        elif command == 'clear_history':
            return await self._clear_history()
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _add_to_history(self, operation: str, details: Dict[str, Any]) -> None:
        """Add an operation to history.
        
        Args:
            operation: Operation performed
            details: Operation details
        """
        self._operation_history.append({
            'operation': operation,
            'details': details,
            'timestamp': time.time()
        })
        if len(self._operation_history) > self._max_history:
            self._operation_history.pop(0)
    
    async def _ping(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ping a host.
        
        Args:
            args: Ping arguments
            
        Returns:
            Dict[str, Any]: Ping result
        """
        try:
            if not args or 'host' not in args:
                return {'error': 'Missing required arguments'}
            
            host = args['host']
            count = args.get('count', 4)
            timeout = args.get('timeout', self._timeout)
            
            # Create ping command
            if os.name == 'nt':  # Windows
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
            else:  # Unix-like
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
            
            # Execute ping
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    'status': 'error',
                    'action': 'ping',
                    'error': f'Ping failed: {stderr.decode()}'
                }
            
            # Parse output
            output = stdout.decode()
            if os.name == 'nt':  # Windows
                # Extract statistics
                stats = {}
                for line in output.split('\n'):
                    if 'Packets:' in line:
                        parts = line.split(',')
                        for part in parts:
                            if ':' in part:
                                key, value = part.split(':')
                                stats[key.strip()] = value.strip()
            else:  # Unix-like
                # Extract statistics
                stats = {}
                for line in output.split('\n'):
                    if 'packets transmitted' in line:
                        parts = line.split(',')
                        for part in parts:
                            if ':' in part:
                                key, value = part.split(':')
                                stats[key.strip()] = value.strip()
            
            self._add_to_history('ping', {
                'host': host,
                'count': count,
                'timeout': timeout,
                'stats': stats
            })
            
            return {
                'status': 'success',
                'action': 'ping',
                'host': host,
                'stats': stats
            }
        except Exception as e:
            logger.error(f"Error pinging host: {e}")
            return {'error': str(e)}
    
    async def _dns_lookup(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform DNS lookup.
        
        Args:
            args: DNS lookup arguments
            
        Returns:
            Dict[str, Any]: DNS lookup result
        """
        try:
            if not args or 'host' not in args:
                return {'error': 'Missing required arguments'}
            
            host = args['host']
            record_type = args.get('record_type', 'A')
            
            # Configure resolver
            resolver = dns.resolver.Resolver()
            resolver.timeout = self._timeout
            resolver.lifetime = self._timeout
            
            # Perform lookup
            try:
                answers = resolver.resolve(host, record_type)
                records = [str(rdata) for rdata in answers]
            except dns.resolver.NXDOMAIN:
                return {
                    'status': 'error',
                    'action': 'dns_lookup',
                    'error': f'Domain does not exist: {host}'
                }
            except dns.resolver.NoAnswer:
                return {
                    'status': 'error',
                    'action': 'dns_lookup',
                    'error': f'No {record_type} records found for: {host}'
                }
            except dns.resolver.Timeout:
                return {
                    'status': 'error',
                    'action': 'dns_lookup',
                    'error': f'DNS lookup timed out for: {host}'
                }
            
            self._add_to_history('dns_lookup', {
                'host': host,
                'record_type': record_type,
                'records': records
            })
            
            return {
                'status': 'success',
                'action': 'dns_lookup',
                'host': host,
                'record_type': record_type,
                'records': records
            }
        except Exception as e:
            logger.error(f"Error performing DNS lookup: {e}")
            return {'error': str(e)}
    
    async def _port_scan(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scan ports on a host.
        
        Args:
            args: Port scan arguments
            
        Returns:
            Dict[str, Any]: Port scan result
        """
        try:
            if not args or 'host' not in args:
                return {'error': 'Missing required arguments'}
            
            host = args['host']
            ports = args.get('ports', range(1, 1025))
            timeout = args.get('timeout', 1)
            
            # Scan ports
            open_ports = []
            for port in ports:
                try:
                    # Create socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    
                    # Try to connect
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        open_ports.append(port)
                    
                    # Close socket
                    sock.close()
                except Exception:
                    continue
            
            self._add_to_history('port_scan', {
                'host': host,
                'ports': list(ports),
                'timeout': timeout,
                'open_ports': open_ports
            })
            
            return {
                'status': 'success',
                'action': 'port_scan',
                'host': host,
                'open_ports': open_ports
            }
        except Exception as e:
            logger.error(f"Error scanning ports: {e}")
            return {'error': str(e)}
    
    async def _http_request(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request.
        
        Args:
            args: HTTP request arguments
            
        Returns:
            Dict[str, Any]: HTTP request result
        """
        try:
            if not args or 'url' not in args:
                return {'error': 'Missing required arguments'}
            
            url = args['url']
            method = args.get('method', 'GET')
            headers = args.get('headers', {})
            data = args.get('data')
            timeout = args.get('timeout', self._timeout)
            
            # Check session
            if not self._session:
                return {
                    'status': 'error',
                    'action': 'http_request',
                    'error': 'HTTP session not initialized'
                }
            
            # Make request
            try:
                async with self._session.request(
                    method,
                    url,
                    headers=headers,
                    data=data,
                    timeout=timeout
                ) as response:
                    # Get response data
                    response_data = await response.read()
                    
                    # Get response headers
                    response_headers = dict(response.headers)
                    
                    self._add_to_history('http_request', {
                        'url': url,
                        'method': method,
                        'status': response.status,
                        'headers': response_headers,
                        'data_size': len(response_data)
                    })
                    
                    return {
                        'status': 'success',
                        'action': 'http_request',
                        'url': url,
                        'method': method,
                        'response': {
                            'status': response.status,
                            'headers': response_headers,
                            'data': response_data
                        }
                    }
            except aiohttp.ClientError as e:
                return {
                    'status': 'error',
                    'action': 'http_request',
                    'error': f'HTTP request failed: {str(e)}'
                }
        except Exception as e:
            logger.error(f"Error making HTTP request: {e}")
            return {'error': str(e)}
    
    async def _get_history(self) -> Dict[str, Any]:
        """Get operation history.
        
        Returns:
            Dict[str, Any]: Operation history
        """
        try:
            return {
                'status': 'success',
                'action': 'get_history',
                'history': self._operation_history
            }
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return {'error': str(e)}
    
    async def _clear_history(self) -> Dict[str, Any]:
        """Clear operation history.
        
        Returns:
            Dict[str, Any]: Result of clearing history
        """
        try:
            self._operation_history = []
            return {
                'status': 'success',
                'action': 'clear_history'
            }
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return {'error': str(e)} 