# UaiBot

UaiBot is an AI agent framework that implements the SmolAgents pattern, A2A (Agent-to-Agent) protocol, and MCP (Model Context Protocol) for building intelligent, interoperable AI agents.

## Features

- **SmolAgents Pattern**: Minimal and efficient agent implementation with standardized interfaces
- **A2A Protocol**: Standardized communication between AI agents using JSON-RPC 2.0 over HTTP(S)
- **MCP Protocol**: Universal interface for AI agents to connect with external tools, data sources, and services
- **CLI Interface**: Command-line interface for interacting with UaiBot
- **GUI Interface**: Graphical user interface built with tkinter for a more user-friendly experience
- **Natural Language Processing**: Convert natural language to executable commands
- **File Operations**: Create, read, update, and delete files with natural language
- **System Information**: Get system resource usage, date/time, and more
- **Weather Information**: Get current weather conditions (requires API key)
- **Calculator**: Evaluate mathematical expressions
- **Graph Generation**: Create visualizations from folder data
- **Multi-language Support**: English and Arabic language support

## Architecture

UaiBot is built on three core components:

1. **SmolAgents**: A minimal agent implementation pattern that focuses on:
   - Minimal memory/state
   - Standardized interfaces
   - Efficient execution
   - Clear separation of concerns

2. **A2A Protocol**: A standardized protocol for agent communication that provides:
   - JSON-RPC 2.0 based communication
   - Agent discovery and capabilities
   - Message handling for various content types
   - State persistence

3. **MCP Protocol**: A universal interface for connecting AI agents with external tools that offers:
   - Tool registration and discovery
   - Schema validation
   - Standardized request/response handling
   - WebSocket support for real-time communication

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/UaiBot.git
   cd UaiBot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### CLI Mode

To start UaiBot in CLI mode:

```bash
./scripts/launch.py
```

The CLI provides a text-based interface for interacting with UaiBot. You can:
- Execute shell commands
- Send messages to other agents
- Process user input
- View command output and responses

### GUI Mode

To start UaiBot in GUI mode:

```bash
./scripts/launch_gui.py
```

The GUI provides a more user-friendly interface with:
- Text output area for displaying messages and responses
- Input field for entering commands and messages
- Status indicator
- Send button for submitting input

## Configuration

### Weather API

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Add to `config/settings.json`:
   ```json
   {
     "openweathermap_api_key": "YOUR_API_KEY_HERE"
   }
   ```

## Development

### Project Structure

```
UaiBot/
├── src/
│   └── uaibot/
│       └── core/
│           └── ai/
│               ├── smol_agent.py
│               ├── a2a_protocol.py
│               ├── mcp_protocol.py
│               └── channels/
│                   └── websocket_channel.py
├── scripts/
│   ├── launch.py
│   └── launch_gui.py
├── tests/
│   └── test_protocols.py
├── requirements.txt
└── README.md
```

### Running Tests

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Latest Changes
- Implemented SmolAgents core framework
- Added A2A protocol for agent collaboration
- Integrated MCP for multi-channel support
- Enhanced file operations with natural language
- Added graph generation capabilities
- Improved multi-language support

### Upcoming Features
- Enhanced agent memory and state management
- Advanced A2A collaboration patterns
- Extended MCP capabilities
- Improved performance and optimization
- Enhanced security features
- Comprehensive documentation updates

## Support

For issues and feature requests, please use the GitHub issue tracker.

## Agent-to-Agent (A2A) Protocol

The A2A protocol enables standardized communication and collaboration between agents. Key features include:

- Standardized message format for agent communication
- Capability negotiation between agents
- Task delegation and result aggregation
- Persistent state management

### Usage

```python
from src.uaibot.core.ai.a2a_protocol import A2AProtocol, A2AMessage, AgentCapability
from src.uaibot.core.ai.smol_agent import SmolAgent

# Create A2A protocol instance
a2a = A2AProtocol()

# Register agent with capabilities
capabilities = [
    AgentCapability(
        name="example_capability",
        description="Example capability",
        parameters={"param1": "string"},
        required=True
    )
]
a2a.register_agent(agent, capabilities)

# Send message to agent
message = A2AMessage(
    sender_id="sender",
    receiver_id="receiver",
    message_type="task_delegation",
    content={"task": "example_task", "params": {"param1": "value1"}}
)
result = a2a.send_message(message)
```

## Multi-Context Protocol (MCP)

The MCP enables communication across different contexts and protocols. Key features include:

- Abstract context interface for different communication protocols
- WebSocket context implementation
- Asynchronous message handling
- Context registration and management
- Message routing and processing

### Usage

```python
from src.uaibot.core.ai.mcp_protocol import MCPProtocol, ContextMessage
from src.uaibot.core.ai.channels.websocket_channel import WebSocketContext

# Create MCP protocol instance
mcp = MCPProtocol()

# Create and register WebSocket context
context = WebSocketContext("ws://localhost:8765", "example_context")
mcp.register_context("example_context", context)

# Register message handler
async def message_handler(message: ContextMessage):
    print(f"Received message: {message.content}")

mcp.register_handler("example_context", message_handler)

# Start protocol
await mcp.start()

# Send message
message = ContextMessage(
    context_id="example_context",
    sender_id="sender",
    content={"type": "example", "data": "example_data"}
)
await mcp.send_message(message)

# Stop protocol
await mcp.stop()
```
