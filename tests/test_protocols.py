"""
Tests for A2A and MCP protocol implementations.
"""
import pytest
import asyncio
from datetime import datetime
from typing import Any, Dict
from src.labeeb.core.ai.smol_agent import SmolAgent, AgentResult
from src.labeeb.core.ai.a2a_protocol import (
    A2AProtocol, Message, TextContent, FileContent, StructuredContent,
    MessageRole, AgentCapability, AgentCard, A2AServer
)
from src.labeeb.core.ai.mcp_protocol import MCPProtocol, MCPRequest, MCPResponse, MCPTool
from src.labeeb.core.ai.channels.websocket_channel import WebSocketTool

class TestAgent(SmolAgent):
    """Test agent implementation."""
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.received_messages = []

    async def execute(self, task: str, params: dict = None) -> AgentResult:
        """Execute a test task."""
        return AgentResult(
            success=True,
            data={"task": task, "params": params}
        )

class TestA2AServer(A2AServer):
    """Test A2A server implementation."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.received_messages = []

    async def handle_message(self, message: Message) -> Message:
        """Handle incoming message and return response."""
        self.received_messages.append(message)
        return Message(
            content=TextContent(text=f"Echo: {message.content.text}"),
            role=MessageRole.AGENT,
            parent_message_id=message.message_id,
            conversation_id=message.conversation_id
        )

    def get_agent_card(self) -> AgentCard:
        """Get agent metadata and capabilities."""
        return AgentCard(
            agent_id=self.agent_id,
            name="Test Agent",
            description="Test A2A agent",
            capabilities=[
                AgentCapability(
                    name="echo",
                    description="Echo back messages",
                    parameters={"message": "string"},
                    required=True
                )
            ]
        )

class TestTool(MCPTool):
    """Test MCP tool implementation."""
    def __init__(self, tool_id: str):
        self.tool_id = tool_id

    async def execute(self, params: Dict[str, Any]) -> MCPResponse:
        """Execute the test tool."""
        return MCPResponse(
            result={"params": params},
            id=datetime.utcnow().isoformat()
        )

    def get_schema(self) -> Dict[str, Any]:
        """Get the test tool's schema."""
        return {
            "name": self.tool_id,
            "description": "Test tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_param": {
                        "type": "string",
                        "description": "Test parameter"
                    }
                },
                "required": ["test_param"]
            }
        }

@pytest.fixture
def test_agent():
    """Create a test agent."""
    return TestAgent("test_agent")

@pytest.fixture
def test_a2a_server():
    """Create a test A2A server."""
    return TestA2AServer("test_a2a_server")

@pytest.fixture
def a2a_protocol():
    """Create an A2A protocol instance."""
    return A2AProtocol()

@pytest.fixture
def mcp_protocol():
    """Create an MCP protocol instance."""
    return MCPProtocol()

@pytest.fixture
def test_tool():
    """Create a test MCP tool."""
    return TestTool("test_tool")

@pytest.mark.asyncio
async def test_a2a_protocol(test_a2a_server, a2a_protocol):
    """Test A2A protocol functionality."""
    # Register A2A server
    agent_card = test_a2a_server.get_agent_card()
    a2a_protocol.register_agent(test_a2a_server, agent_card)

    # Create test message
    message = Message(
        content=TextContent(text="Hello, A2A!"),
        role=MessageRole.USER,
        conversation_id="test_conversation",
        metadata={"agent_id": agent_card.agent_id}
    )

    # Send message and get response
    response = await a2a_protocol.send_message(message)

    # Verify response
    assert response.role == MessageRole.AGENT
    assert isinstance(response.content, TextContent)
    assert response.content.text == "Echo: Hello, A2A!"
    assert response.parent_message_id == message.message_id
    assert response.conversation_id == message.conversation_id

    # Verify message was received by server
    assert len(test_a2a_server.received_messages) == 1
    assert test_a2a_server.received_messages[0].message_id == message.message_id

    # Test agent card retrieval
    retrieved_card = a2a_protocol.get_agent_card(agent_card.agent_id)
    assert retrieved_card is not None
    assert retrieved_card.agent_id == agent_card.agent_id
    assert len(retrieved_card.capabilities) == 1
    assert retrieved_card.capabilities[0].name == "echo"

@pytest.mark.asyncio
async def test_mcp_protocol(mcp_protocol, test_tool):
    """Test MCP protocol functionality."""
    # Register test tool
    mcp_protocol.register_tool("test_tool", test_tool)

    # Register response handler
    received_responses = []
    async def response_handler(response: MCPResponse):
        received_responses.append(response)
    mcp_protocol.register_handler("test_tool", response_handler)

    # Start protocol
    await mcp_protocol.start()

    # Create and send test request
    request = MCPRequest(
        method="test_tool",
        params={"test_param": "test_value"}
    )
    response = await mcp_protocol.call_tool(request)

    # Verify response
    assert response.result is not None
    assert response.result["params"]["test_param"] == "test_value"
    assert response.error is None

    # Stop protocol
    await mcp_protocol.stop()

@pytest.mark.asyncio
async def test_websocket_tool():
    """Test WebSocket tool functionality."""
    # Create WebSocket tool
    tool = WebSocketTool("ws://localhost:8765", "test_tool")

    # Test connection
    connected = await tool.connect()
    assert connected

    # Test tool execution
    response = await tool.execute({"message": "test_message"})
    assert response.result is not None
    assert response.error is None

    # Test disconnection
    disconnected = await tool.disconnect()
    assert disconnected 