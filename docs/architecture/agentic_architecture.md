# Agentic Architecture: SmolAgents, A2A, MCP

## What is an Agent?
An agent is a software entity that can perceive, reason, and act to achieve goals or complete tasks. In Labeeb, agents:
- Encapsulate state, memory, and behavior
- Use tools to interact with the environment
- Orchestrate workflows (plan/execute loop)
- Can collaborate with other agents (A2A)

## SmolAgents
- Lightweight, modular agent framework
- Local-first, minimal memory/storage
- Model-agnostic, multi-language, multi-platform
- Agents and tools are first-class, composable components

## A2A (Agent-to-Agent Protocol)
- Enables agent collaboration and delegation
- Agents can call, communicate, and coordinate with each other
- Supports scalable, modular, and robust systems

## MCP (Multi-Channel Protocol)
- Unified support for CLI, GUI, web, and other channels
- Maintains context/state across channels
- Enables seamless user experience and extensibility

## Plan/Execute Loop
- Agents receive commands/goals
- Plan steps (break down into sub-tasks)
- Execute steps (sequential, parallel, conditional)
- Update state/memory after each step

## Planning/LLM Step

- The agent now includes a planning step using an `LLMPlanner` stub.
- If a command is not a direct tool invocation, the agent uses the planner to decompose the command into tool, action, and parameters.
- The current planner is a stub for future LLM integration (e.g., OpenAI, Gemini, local LLMs).
- This enables natural language commands to be mapped to agent workflows and tool invocations.
- Future work: Replace the stub with a real LLM call and support multi-step plans.

## Developer Guidance
- Refactor command handlers as tools
- Implement Agent classes with state, memory, and plan/execute methods
- Use A2A for agent collaboration and delegation
- Use MCP for multi-channel support
- Optimize for local-first, minimal resource usage
- Document and test all agent, tool, and workflow patterns

## Dependency Management & Troubleshooting

- For Python 3.12+, ensure `grpcio>=1.71.0` is used and install with binary wheels (`--only-binary=:all:`) to avoid build errors.
- Always upgrade pip, setuptools, and wheel before installing requirements.
- See README.md for troubleshooting steps if you encounter grpcio build issues.

## References
- [SmolAgents](https://github.com/smol-ai/agents)
- [Agent Frameworks Comparison](https://prassanna.io/blog/agent-frameworks/)
- [Langfuse AI Agent Comparison](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)
- [YouTube: Smol Agents](https://www.youtube.com/watch?v=QjJ2HrOa3J0&t=505s)
- [YouTube: Agent Frameworks](https://www.youtube.com/watch?v=z8rAXE8tysc)
- [Perplexity: Agent Dev Kits Comparison](https://www.perplexity.ai/search/comparing-all-agent-dev-kits-a-tfPNmxr.RGWAqJlOM.UqLQ) 