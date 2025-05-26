"""
Multi-Channel Protocol (MCP) Implementation.

This module implements the MCP protocol for unified channel support, following the
SmolAgents pattern for minimal, efficient channel communication.

The MCP protocol enables:
- Unified interface for multiple communication channels
- Channel discovery and registration
- Message routing across channels
- Channel state management
- Error handling and recovery

Channel Types:
- HTTP: REST API endpoints
- WebSocket: Real-time bidirectional communication
- gRPC: High-performance RPC
- MQTT: Lightweight IoT messaging
- Redis: Pub/sub messaging
- File: File-based communication

Protocol Flow:
1. Channel registration and discovery
2. Message routing to appropriate channel
3. Channel-specific message handling
4. Response routing back to sender
5. Error handling and recovery

Error Handling:
- Channel connection failures
- Message delivery failures
- Timeout handling
- Retry logic
- Error propagation
"""

from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from enum import Enum
import asyncio
from .smol_agent import SmolAgent, AgentState, AgentResult

class ChannelType(Enum):
    """Types of communication channels."""
    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MQTT = "mqtt"
    REDIS = "redis"
    FILE = "file"

@dataclass
class ChannelConfig:
    """Configuration for a communication channel."""
    type: ChannelType
    name: str
    config: Dict[str, Any]
    enabled: bool = True
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0

@dataclass
class MCPRequest:
    """MCP request structure."""
    channel: str
    method: str
    params: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "channel": self.channel,
            "method": self.method,
            "params": self.params,
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPRequest':
        """Create request from dictionary."""
        return cls(
            channel=data["channel"],
            method=data["method"],
            params=data["params"],
            timestamp=data["timestamp"],
            request_id=data["request_id"],
            metadata=data.get("metadata", {})
        )

@dataclass
class MCPResponse:
    """MCP response structure."""
    request_id: str
    result: Any
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "request_id": self.request_id,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPResponse':
        """Create response from dictionary."""
        return cls(
            request_id=data["request_id"],
            result=data["result"],
            error=data.get("error"),
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {})
        )

class Channel(Protocol):
    """Protocol defining the interface for communication channels."""
    
    async def connect(self) -> None:
        """Connect to the channel."""
        ...
    
    async def disconnect(self) -> None:
        """Disconnect from the channel."""
        ...
    
    async def send(self, request: MCPRequest) -> MCPResponse:
        """Send a request through the channel."""
        ...
    
    async def receive(self) -> MCPRequest:
        """Receive a request from the channel."""
        ...

class MCPProtocol:
    """
    MCP protocol implementation for unified channel support.
    
    This class handles:
    - Channel registration and discovery
    - Message routing across channels
    - Channel state management
    - Error handling and recovery
    """
    
    def __init__(self):
        """Initialize MCP protocol."""
        self.logger = logging.getLogger("MCPProtocol")
        self._channels: Dict[str, Channel] = {}
        self._channel_configs: Dict[str, ChannelConfig] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}
    
    def register_channel(self, channel: Channel, config: ChannelConfig):
        """Register a new communication channel."""
        self._channels[config.name] = channel
        self._channel_configs[config.name] = config
        self.logger.info(f"Registered channel: {config.name} ({config.type.value})")
    
    def unregister_channel(self, channel_name: str):
        """Unregister a communication channel."""
        if channel_name in self._channels:
            del self._channels[channel_name]
            del self._channel_configs[channel_name]
            self.logger.info(f"Unregistered channel: {channel_name}")
    
    async def connect_all(self):
        """Connect to all registered channels."""
        for name, channel in self._channels.items():
            try:
                await channel.connect()
                self.logger.info(f"Connected to channel: {name}")
            except Exception as e:
                self.logger.error(f"Failed to connect to channel {name}: {str(e)}")
    
    async def disconnect_all(self):
        """Disconnect from all registered channels."""
        for name, channel in self._channels.items():
            try:
                await channel.disconnect()
                self.logger.info(f"Disconnected from channel: {name}")
            except Exception as e:
                self.logger.error(f"Failed to disconnect from channel {name}: {str(e)}")
    
    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """
        Send a request through the specified channel.
        
        Args:
            request: The request to send
            
        Returns:
            MCPResponse: The response from the channel
            
        Raises:
            ChannelNotFoundError: If channel not found
            ChannelError: If channel operation fails
        """
        if request.channel not in self._channels:
            raise ChannelNotFoundError(f"Channel not found: {request.channel}")
        
        channel = self._channels[request.channel]
        config = self._channel_configs[request.channel]
        
        try:
            # Create future for response
            future = asyncio.Future()
            self._pending_requests[request.request_id] = future
            
            # Send request
            response = await channel.send(request)
            
            # Set response in future
            future.set_result(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Error sending request: {str(e)}")
            raise ChannelError(f"Failed to send request: {str(e)}")
            
        finally:
            self._pending_requests.pop(request.request_id, None)
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle an incoming request.
        
        Args:
            request: The request to handle
            
        Returns:
            MCPResponse: The response to send back
        """
        try:
            # Get channel
            if request.channel not in self._channels:
                return MCPResponse(
                    request_id=request.request_id,
                    result=None,
                    error=f"Channel not found: {request.channel}"
                )
            
            channel = self._channels[request.channel]
            config = self._channel_configs[request.channel]
            
            # Handle request
            try:
                response = await channel.send(request)
                return response
            except Exception as e:
                return MCPResponse(
                    request_id=request.request_id,
                    result=None,
                    error=str(e)
                )
            
        except Exception as e:
            self.logger.error(f"Error handling request: {str(e)}")
            return MCPResponse(
                request_id=request.request_id,
                result=None,
                error=str(e)
            )
    
    def get_channel_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a channel."""
        if channel_name not in self._channels:
            return None
        
        config = self._channel_configs[channel_name]
        return {
            "name": config.name,
            "type": config.type.value,
            "enabled": config.enabled,
            "timeout": config.timeout,
            "retry_count": config.retry_count,
            "retry_delay": config.retry_delay
        }
    
    def list_channels(self) -> List[str]:
        """List all registered channel names."""
        return list(self._channels.keys())

class MCPError(Exception):
    """Base class for MCP protocol errors."""
    pass

class ChannelNotFoundError(MCPError):
    """Raised when a channel is not found."""
    pass

class ChannelError(MCPError):
    """Raised when a channel operation fails."""
    pass 