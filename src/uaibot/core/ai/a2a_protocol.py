"""
Agent-to-Agent (A2A) Protocol implementation.
Based on the open, vendor-neutral standard developed by Google for agent interoperability.
"""
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import asyncio
from enum import Enum
from abc import ABC, abstractmethod
from .smol_agent import SmolAgent, AgentResult

class MessageRole(Enum):
    """Message roles in A2A protocol."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class ContentType(Enum):
    """Content types supported by A2A protocol."""
    TEXT = "text"
    FILE = "file"
    STRUCTURED = "structured"

@dataclass
class Content:
    """Base class for message content."""
    pass

@dataclass
class TextContent(Content):
    """Text content for messages."""
    text: str
    content_type: ContentType = ContentType.TEXT

@dataclass
class FileContent(Content):
    """File content for messages."""
    file_path: str
    content_type: ContentType = ContentType.FILE

@dataclass
class StructuredContent(Content):
    """Structured content for messages."""
    data: dict
    content_type: ContentType = ContentType.STRUCTURED

@dataclass
class Message:
    """A2A protocol message format."""
    content: Content
    role: MessageRole
    message_id: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    conversation_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "content": {
                "type": self.content.type.value,
                **self._get_content_dict()
            },
            "role": self.role.value,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_message_id,
            "metadata": self.metadata
        }

    def _get_content_dict(self) -> Dict[str, Any]:
        """Get content-specific dictionary."""
        if isinstance(self.content, TextContent):
            return {"text": self.content.text}
        elif isinstance(self.content, FileContent):
            return {
                "file_path": self.content.file_path,
                "mime_type": self.content.mime_type
            }
        elif isinstance(self.content, StructuredContent):
            return {"data": self.content.data}
        return {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        content_type = ContentType(data["content"]["type"])
        if content_type == ContentType.TEXT:
            content = TextContent(text=data["content"]["text"])
        elif content_type == ContentType.FILE:
            content = FileContent(
                file_path=data["content"]["file_path"],
                mime_type=data["content"]["mime_type"]
            )
        elif content_type == ContentType.STRUCTURED:
            content = StructuredContent(data=data["content"]["data"])
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

        return cls(
            content=content,
            role=MessageRole(data["role"]),
            message_id=data["message_id"],
            conversation_id=data.get("conversation_id"),
            parent_message_id=data.get("parent_message_id"),
            metadata=data.get("metadata", {})
        )

@dataclass
class AgentCapability:
    """Agent capability description."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: bool = False
    version: str = "1.0"

@dataclass
class AgentCard:
    """Agent metadata and capabilities."""
    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

class A2AServer(ABC):
    """Abstract base class for A2A servers."""
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Message:
        """Handle incoming message and return response."""
        pass

    @abstractmethod
    def get_agent_card(self) -> AgentCard:
        """Get agent metadata and capabilities."""
        pass

class A2AProtocol:
    """
    A2A Protocol implementation.
    Handles communication between agents using JSON-RPC 2.0 over HTTP(S).
    """
    def __init__(self, state_dir: Optional[str] = None):
        self.state_dir = state_dir or os.path.expanduser("~/Documents/uaibot/a2a")
        os.makedirs(self.state_dir, exist_ok=True)
        self.agents: Dict[str, A2AServer] = {}
        self.agent_cards: Dict[str, AgentCard] = {}
        self.conversations: Dict[str, List[Message]] = {}
        self._load_state()

    def register_agent(self, agent: A2AServer, agent_card: AgentCard):
        """Register a new agent with its capabilities."""
        self.agents[agent_card.agent_id] = agent
        self.agent_cards[agent_card.agent_id] = agent_card
        self._save_state()

    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_cards[agent_id]
            self._save_state()

    async def send_message(self, message: Message) -> Message:
        """Send a message to an agent and get response."""
        if message.role == MessageRole.USER:
            # Store message in conversation history
            if message.conversation_id not in self.conversations:
                self.conversations[message.conversation_id] = []
            self.conversations[message.conversation_id].append(message)

            # Get agent and handle message
            agent = self.agents.get(message.metadata.get("agent_id"))
            if not agent:
                raise ValueError(f"Agent not found: {message.metadata.get('agent_id')}")

            response = await agent.handle_message(message)
            
            # Store response in conversation history
            self.conversations[message.conversation_id].append(response)
            self._save_state()
            
            return response
        else:
            raise ValueError("Only user messages can be sent through the protocol")

    def get_agent_card(self, agent_id: str) -> Optional[AgentCard]:
        """Get agent metadata and capabilities."""
        return self.agent_cards.get(agent_id)

    def _save_state(self):
        """Save A2A protocol state to disk."""
        state = {
            "agent_cards": {
                agent_id: {
                    "agent_id": card.agent_id,
                    "name": card.name,
                    "description": card.description,
                    "capabilities": [
                        {
                            "name": cap.name,
                            "description": cap.description,
                            "parameters": cap.parameters,
                            "required": cap.required,
                            "version": cap.version
                        }
                        for cap in card.capabilities
                    ],
                    "version": card.version,
                    "metadata": card.metadata
                }
                for agent_id, card in self.agent_cards.items()
            },
            "conversations": {
                conv_id: [msg.to_dict() for msg in messages]
                for conv_id, messages in self.conversations.items()
            }
        }
        
        with open(os.path.join(self.state_dir, "a2a_state.json"), 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        """Load A2A protocol state from disk."""
        state_path = os.path.join(self.state_dir, "a2a_state.json")
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                state = json.load(f)
                # Note: Agents need to be re-registered as they can't be serialized
                self.conversations = {
                    conv_id: [Message.from_dict(msg) for msg in messages]
                    for conv_id, messages in state.get("conversations", {}).items()
                } 