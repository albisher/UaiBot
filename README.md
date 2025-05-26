# Labeeb

Labeeb is a powerful AI agent framework that implements the SmolAgents pattern, A2A (Agent-to-Agent) protocol, and MCP (Multi-Channel Protocol) for efficient and scalable agent-based systems.

## Features

- **SmolAgents Pattern**: Minimal, efficient agent implementation with clear state management and tool integration
- **A2A Protocol**: Robust agent-to-agent communication with message passing, tool sharing, and state synchronization
- **MCP Protocol**: Unified interface for multiple communication channels (HTTP, WebSocket, gRPC, MQTT, Redis, File)
- **Multi-Language Support**: Comprehensive internationalization with special focus on Arabic and RTL languages
- **Cross-Platform**: Support for macOS, Windows, and Ubuntu with platform-specific optimizations
- **Extensible**: Easy to add new agents, tools, and channels
- **Testable**: Built-in testing support with clear interfaces and state management

## Architecture

### Core Components

1. **SmolAgent**
   - Minimal, efficient agent implementation
   - Clear state management
   - Tool integration
   - Error handling
   - Testing support

2. **A2A Protocol**
   - Direct agent-to-agent communication
   - Message passing
   - Tool sharing and discovery
   - State synchronization
   - Error handling and recovery

3. **MCP Protocol**
   - Unified channel interface
   - Channel discovery and registration
   - Message routing
   - Channel state management
   - Error handling and recovery

4. **Internationalization**
   - Multi-language support
   - RTL language handling
   - Regional variants
   - Translation management
   - Fallback mechanisms

### Directory Structure

```
labeeb/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── ai/
│   │   │   │   ├── agent.py
│   │   │   │   ├── a2a_protocol.py
│   │   │   │   ├── mcp_protocol.py
│   │   │   │   └── smol_agent.py
│   │   │   └── i18n/
│   │   │       ├── i18n.py
│   │   │       └── translations/
│   │   └── platform_core/
│   │       ├── platform_manager.py
│   │       └── system_info.py
│   └── tests/
│       └── unit/
│           ├── core/
│           │   └── ai/
│           │       ├── test_agent.py
│           │       ├── test_a2a_protocol.py
│           │       ├── test_mcp_protocol.py
│           │       └── test_smol_agent.py
│           └── platform_core/
│               ├── test_platform_manager.py
│               └── test_system_info.py
├── docs/
│   ├── architecture.md
│   ├── i18n.md
│   └── platform_core.md
├── setup.py
├── requirements.txt
└── README.md
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/labeeb.git
cd labeeb

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Usage

### Basic Agent Usage

```python
from labeeb.core.ai import SmolAgent, Tool

# Create a tool
class EchoTool(Tool):
    name = "echo"
    description = "Echoes the input text"
    
    async def execute(self, text: str) -> str:
        return text

# Create an agent
agent = SmolAgent("test_agent")

# Register the tool
agent.register_tool(EchoTool())

# Execute the tool
result = await agent.execute_tool("echo", text="Hello, World!")
print(result.data)  # Output: Hello, World!
```

### A2A Communication

```python
from labeeb.core.ai import A2AProtocol, Message, MessageType

# Create A2A protocol
a2a = A2AProtocol()

# Create a message
message = Message(
    type=MessageType.REQUEST,
    sender="agent1",
    receiver="agent2",
    content={"text": "Hello!"}
)

# Send message and get response
response = await a2a.send_message(message)
print(response.content)  # Output: {"text": "Hello!"}
```

### MCP Channel Usage

```python
from labeeb.core.ai import MCPProtocol, MCPRequest, ChannelConfig, ChannelType

# Create MCP protocol
mcp = MCPProtocol()

# Create channel config
config = ChannelConfig(
    type=ChannelType.HTTP,
    name="api",
    config={"url": "http://api.example.com"}
)

# Register channel
mcp.register_channel(channel, config)

# Create request
request = MCPRequest(
    channel="api",
    method="GET",
    params={"path": "/users"}
)

# Send request
response = await mcp.send_request(request)
print(response.result)  # Output: {"users": [...]}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/core/ai/test_agent.py

# Run with coverage
pytest --cov=src
```

### Adding New Features

1. Create a new branch
2. Add your changes
3. Add tests
4. Update documentation
5. Submit a pull request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests
- Update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- SmolAgents pattern for minimal, efficient agent implementation
- A2A protocol for agent-to-agent communication
- MCP protocol for unified channel support
- All contributors and users of the project
