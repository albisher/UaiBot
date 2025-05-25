# File Organization & Cleanup (Core Principle)

- All files must be placed in their correct directories immediately (see below).
- No files should be left in the root except LICENSE, README, and config files.
- Test artifacts: `tests/fixtures/` or `tests/outputs/`
- Logs: `log/`
- State/context: `src/uaibot/state/`
- Registry/config: `src/uaibot/core/`
- Scripts/entry-points: `scripts/`
- License: project root

## Checklist
- [x] No test or log files in root
- [x] All scripts in `scripts/`
- [x] All state/context in `src/uaibot/state/`
- [x] All registry/config in `src/uaibot/core/`
- [x] Regular file audits after major changes

---

# Agentic Refactor Plan (SmolAgents, A2A, MCP)

## Goal
Transform UaiBot into a local-first, agentic, modular, multi-language, multi-platform system using SmolAgents, with A2A and MCP as core features.

## Steps

1. **Introduce Agent Abstraction**
   - [x] Create a base `Agent` class (state, memory, planning, execution)
   - [x] Implement tool registry for agent tools
   - [x] Create a minimal tool and a test agent using the new base class
   - [x] Update requirements.txt and add grpcio troubleshooting to docs
   - [x] Document agent interface and lifecycle
   - [x] Refactor an existing handler as a real tool
   - [x] Integrate a more advanced planning/LLM step
   - [x] Implement agent memory/state improvements for multi-step workflows
   - [x] Workflow orchestration: break down commands into sub-tasks, support sequential/parallel/conditional execution
   - [ ] Implement A2A (Agent-to-Agent) protocol for agent collaboration and delegation

2. **Refactor Handlers as Tools**
   - Convert command handlers (file, device, etc.) into agent tools
   - Register tools for agent discovery and invocation
   - Ensure tools have clear, type-safe interfaces

3. **Implement Agent Memory/State**
   - Add memory/history to agents (minimal, efficient)
   - Support context retention for multi-step workflows

4. **Workflow Orchestration**
   - Enable agents to break down commands into sub-tasks (plan/execute)
   - Support sequential, parallel, and conditional workflows

5. **A2A (Agent-to-Agent) Protocol**
   - Implement agent collaboration and delegation
   - Allow agents to call/communicate with each other
   - Document A2A patterns and use cases

6. **MCP (Multi-Channel Protocol)**
   - Add support for CLI, GUI, web, and other channels
   - Maintain context/state across channels
   - Route commands/responses via MCP

7. **SmolAgents Integration**
   - Use SmolAgents as the core agent framework
   - Ensure compatibility with local-first, minimal resource goals

8. **Multi-Language & Multi-Platform**
   - Ensure all agent/tool interfaces are language-agnostic
   - Test and document on Linux, macOS, Windows
   - Expand language support as needed

9. **Documentation & Testing**
   - Update all docs to reflect agentic, tool-based, A2A/MCP architecture
   - Add tests for agent workflows, A2A, MCP, and tool integration

## GUI/CLI Integration

- [x] Both GUI and CLI use the agentic core (Agent, ToolRegistry, etc.)
- [x] All file outputs (logs, state, test artifacts) use safe_path or equivalent
- [x] No interface saves files in random or root locations
- [x] CLI: scripts/launch.py delegates to agentic core
- [x] GUI: scripts/launch_gui.py delegates to agentic core
- [x] Requirements and import fixes for agentic core and Ubuntu 24.04
- [ ] Add usage instructions for both interfaces
- [ ] Code review must enforce agentic core, safe_path, and PYTHONPATH/import hygiene for all new features

## Orchestration/Capabilities Test Results

- [x] Agent can execute single-step and multi-step (sequential) plans
- [x] Agent memory tracks each step with full context
- [x] FileTool and EchoTool work as agent tools
- [x] No errors or import issues in local execution
- [x] Output and memory match expected results

Next: Implement A2A (Agent-to-Agent) protocol for agent collaboration and delegation

## References
- [SmolAgents](https://github.com/smol-ai/agents)
- [Agent Frameworks Comparison](https://prassanna.io/blog/agent-frameworks/)
- [Langfuse AI Agent Comparison](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)
- [YouTube: Smol Agents](https://www.youtube.com/watch?v=QjJ2HrOa3J0&t=505s)
- [YouTube: Agent Frameworks](https://www.youtube.com/watch?v=z8rAXE8tysc)
- [Perplexity: Agent Dev Kits Comparison](https://www.perplexity.ai/search/comparing-all-agent-dev-kits-a-tfPNmxr.RGWAqJlOM.UqLQ)

## Install/Requirements Modernization

- [x] setup.py refactored for cross-platform, agentic, robust install
- [x] requirements.txt cleaned up (points to setup.py)
- [x] README documents pip install ., pip install .[dev], pip install .[test]
- [ ] Code review must enforce setup.py as the single source of truth for dependencies
