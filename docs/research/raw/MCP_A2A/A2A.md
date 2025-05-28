## What is the A2A (Agent-to-Agent) Protocol?

The Agent2Agent (A2A) protocol is an open, vendor-neutral standard developed by Google to enable seamless communication and interoperability between AI agents, regardless of the platform or technology they use[1][3][5]. Its key goals are:

- **Standardizing agent collaboration:** Agents can discover, communicate, and delegate tasks to each other using a shared protocol.
- **Unified message transport:** Uses JSON-RPC 2.0 over HTTP(S) for structured, secure, and asynchronous message exchange[5].
- **Agent discovery:** Agents advertise their capabilities via "Agent Cards," making it easy for others to find and utilize their services[7].
- **Task management:** Supports multi-turn conversations, long-running tasks, and various data modalities (text, files, structured data)[5][7].

This protocol is designed to solve the integration and scaling challenges that arise when multiple specialized agents need to work together[5].

---

## How to Use A2A Protocol in Python

There are several Python implementations for A2A, such as `python-a2a` and `FastA2A`. Here’s a practical guide using the `python-a2a` library[8]:

### 1. Install the Library

```bash
pip install python-a2a
```

For optional integrations (e.g., OpenAI, Anthropic):

```bash
pip install "python-a2a[openai]"
pip install "python-a2a[all]"
```


---

### 2. Create a Simple A2A Agent

Below is an example of a basic echo agent:

```python
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server

class EchoAgent(A2AServer):
    def handle_message(self, message):
        if message.content.type == "text":
            return Message(
                content=TextContent(text=f"Echo: {message.content.text}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id,
            )

if __name__ == "__main__":
    agent = EchoAgent()
    run_server(agent, host="0.0.0.0", port=5000)
```


---

### 3. Communicate with the Agent (Client Example)

```python
from python_a2a import A2AClient, Message, TextContent, MessageRole

client = A2AClient("http://localhost:5000/a2a")
message = Message(
    content=TextContent(text="Hello, is this thing on?"),
    role=MessageRole.USER,
)
response = client.send_message(message)
print(f"Agent says: {response.content.text}")
```


---

### 4. Expose Advanced Agents (e.g., Calculator)

You can define agents that expose functions, handle multi-turn conversations, and return structured responses. The protocol supports function calling, error handling, and conversation threading out of the box[8].

---

### 5. Alternative: FastA2A (with PydanticAI)

If you use PydanticAI, you can expose agents as A2A servers with minimal code:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4.1', instructions='Be fun!')
app = agent.to_a2a()
```
Run with:
```bash
uvicorn agent_to_a2a:app --host 0.0.0.0 --port 8000
```


---

## Summary Table: Key Concepts

| Feature              | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| Message Format       | JSON-RPC 2.0 over HTTP(S)                                                   |
| Discovery            | Agent Cards (metadata about agent capabilities)                              |
| Task Management      | Multi-turn, long-running tasks, progress updates                            |
| Data Modalities      | Text, files, structured data, and more                                      |
| Python Libraries     | `python-a2a`, `FastA2A` (PydanticAI)                                        |

---

## Further Resources

- Official documentation: [A2A Protocol site][5]
- Python A2A guide and examples: [a2aprotocol.ai/docs/guide/python-a2a.html][8]
- FastA2A with PydanticAI: [PydanticAI A2A docs][6]

The A2A protocol is rapidly evolving, making it increasingly straightforward to build interoperable, multi-agent AI systems in Python.

Citations:
[1] https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
[2] https://github.com/google/A2A
[3] https://www.datacamp.com/blog/a2a-agent2agent
[4] https://a2aprotocol.ai
[5] https://google.github.io/A2A/topics/what-is-a2a/
[6] https://ai.pydantic.dev/a2a/
[7] https://dev.to/composiodev/a-practical-guide-to-agent-to-agent-a2a-protocol-31fd
[8] https://a2aprotocol.ai/docs/guide/python-a2a.html

---
Answer from Perplexity: pplx.ai/share