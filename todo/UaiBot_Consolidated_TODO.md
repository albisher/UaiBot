# UaiBot Consolidated TODO

## Core Agentic & Architecture
- [ ] Refactor core pipeline to use Agent abstraction (SmolAgents)
- [ ] Convert command handlers/utilities to agent tools
- [ ] Implement agent memory/state (minimal, efficient)
- [ ] Add plan/execute loop for multi-step workflows
- [x] Scaffold UaiAgent class with multi-step/conditional orchestration
- [x] Update CLI to use UaiAgent as master agent
- [x] Integrate config and model management into UaiAgent
- [x] Activate and use agent-to-agent (A2A) protocol in UaiAgent
- [x] Test agent-to-agent workflows (e.g., research, evaluation) via CLI and document results
- [ ] Expand UaiAgent with robust planning, A2A, and MCP features
- [ ] Expand A2A protocol for custom sub-agents and advanced delegation
- [ ] Finalize MCP/multi-context support

## AI/Planning/Enhancements
- [ ] Integrate SmolAgents as the core agent framework
- [ ] Refactor AI command extraction to agent plan/execute loop
- [ ] Expose AI capabilities as agent tools
- [ ] Enable agent memory/state for context retention
- [ ] Support multi-agent collaboration (A2A)
- [ ] Add multi-channel (MCP) support for AI/agent interaction
- [ ] Ensure all AI features work local-first, minimal memory/storage
- [ ] Expand multi-language support for AI/agent workflows
- [ ] Document agentic AI patterns and interfaces
- [ ] Add tests for agentic AI workflows, A2A, MCP
- [ ] Implement model performance tracking (response time, success/failure, token usage)
- [ ] Enhance model configuration (parameters, version tracking)
- [ ] Improve caching mechanism (invalidation, size, hit/miss)
- [ ] Enhance command validation (syntax, safety, complexity)
- [ ] Implement command history analysis (success rates, patterns, suggestions)
- [ ] Add learning capabilities (learn from success, adapt to user)
- [ ] Expand test coverage (integration, performance, stress)
- [ ] Add quality metrics (response quality, accuracy, satisfaction)
- [ ] Enhance documentation (usage, troubleshooting, maintenance)
- [ ] Improve code organization (refactor, error handling, logging)
- [ ] Add monitoring and maintenance (health checks, performance)

## File Organization & Cleanup
- [x] No test or log files in root
- [x] All scripts in `scripts/`
- [x] All state/context in `src/uaibot/state/`
- [x] All registry/config in `src/uaibot/core/`
- [x] Regular file audits after major changes
- [ ] Code review must enforce agentic core, safe_path, and PYTHONPATH/import hygiene for all new features
- [ ] Code review must enforce setup.py as the single source of truth for dependencies

## Testing & Release
- [ ] Run all tests and fix failures
- [ ] Audit file/directory organization for compliance
- [ ] Update documentation and README for all new features
- [ ] Tag a release and update version numbers
- [ ] Expand test coverage (integration, performance, stress)
- [ ] Add/expand tests for agent workflows, A2A, MCP, and tool integration
- [ ] Test all tools in API-free mode and document results

## API-Free Operation
- [x] Refactor all tools to be API-free (weather, web search, etc.)
- [ ] Ensure all tools and code are API-free by default

## GUI/CLI Integration
- [x] Both GUI and CLI use the agentic core (Agent, ToolRegistry, etc.)
- [x] All file outputs (logs, state, test artifacts) use safe_path or equivalent
- [x] No interface saves files in random or root locations
- [x] CLI: scripts/launch.py delegates to agentic core
- [x] GUI: scripts/launch_gui.py delegates to agentic core
- [ ] Add usage instructions for both interfaces

## Documentation
- [ ] Update API documentation
- [ ] Add usage examples
- [ ] Create troubleshooting guide
- [ ] Document maintenance procedures
- [ ] Update README

## Features/Tools
- [x] Implement GraphMakerTool/Agent in agent_tools.py
    - [x] Generates graphs from folder data (e.g., file type distribution)
    - [x] Uses InformationCollectorAgent for data collection
    - [x] Outputs to dedicated work directory under Documents
    - [x] Registered in agent tool registry (agent.py)
    - [x] Documented in README
- [ ] Test GraphMakerTool via GUI (e.g., 'collect graph from folder ...')
- [x] Test CLI/GUI integration for all agentic tools, including GraphMakerTool (pending tests)
- [ ] Improve research and evaluation agent outputs; ensure sub-agent results are returned and displayed in CLI
- [ ] Refactor agent outputs for better CLI/GUI display

## Multilingual & Platform
- [ ] Expand and test multi-language and multi-platform support
- [ ] Update language detection
- [ ] Improve translation handling
- [ ] Add multilingual tests
- [ ] Document language support

## Miscellaneous
- [ ] Profile critical paths
- [ ] Optimize file operations
- [ ] Improve response times
- [ ] Add performance tests
- [ ] Review authentication
- [ ] Update key management
- [ ] Add security tests
- [ ] Document security features
- [ ] Update core module imports
- [ ] Update utility module imports
- [ ] Verify all imports work correctly
- [ ] Update CI/CD configurations
- [ ] Consolidate test files into appropriate directories
- [ ] Update test configuration files
- [ ] Verify test dependencies
- [ ] Add missing test coverage
- [ ] Refactor file operation APIs
- [ ] Update command processor interfaces
- [ ] Implement proper error handling
- [ ] Add comprehensive logging
- [ ] Standardize browser controller
- [ ] Improve cross-platform support
- [ ] Add error recovery
- [ ] Update documentation
- [ ] Update GUI components
- [ ] Improve error messages
- [ ] Add progress indicators
- [ ] Enhance user feedback
- [ ] Run code quality tools
- [ ] Fix linting issues
- [ ] Add type hints
- [ ] Improve code organization 