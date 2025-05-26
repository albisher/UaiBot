# Labeeb Project Professional TODO List

## Vision & Principles
- All core features must be cross-platform by default.
- Platform-specific code (Ubuntu, Windows, macOS, etc.) must be minimal and isolated.
- The master agent is named **Labeeb (لبيب)**, embodying intelligence, wisdom, and cross-cultural accessibility.
- All enhancements are based on industry best practices and research.

## Evaluation & Feedback
- [ ] Implement robust evaluation metrics for all major features/tools
- [ ] Add user/system feedback collection (thumbs up/down, error reporting, etc.)
- [ ] Cluster usage and error data for targeted improvements
- [ ] Regularly review and refine based on real-world usage and feedback

## Rapid Iteration & MVP
- [ ] Launch MVPs for new features/tools and iterate based on real usage
- [ ] Schedule regular review cycles for all major features
- [ ] Prioritize rapid prototyping and data-driven improvement

## Platform Isolation & Cross-Platform
- [ ] Audit all OS-specific code for strict isolation (Ubuntu, Windows, macOS)
- [ ] Add/expand tests to ensure no cross-OS regressions
- [ ] Document platform-specific limitations and error handling
- [ ] Ensure all new features are implemented cross-platform first, with minimal platform-specific code only where necessary

## Documentation & AI-Friendliness
- [ ] Ensure all code and docs are clear, up-to-date, and AI-friendly
- [ ] Link documentation to code files and keep examples current
- [ ] Maintain comprehensive, accessible documentation for all features and APIs

## Automated Testing
- [ ] Expand automated test coverage for all new and platform-specific code
- [ ] Add tests for evaluation metrics and feedback loops
- [ ] Ensure all new features and bug fixes include corresponding tests

## Core System
- [x] Implement base Agent class (now Labeeb) without smolagents dependency
- [x] Create InputHandler base class for platform-specific input handling
- [x] Implement model management with support for both Ollama and HuggingFace
- [x] Add model selection and switching functionality
- [x] Create modern PyQt5-based GUI implementation
- [x] Add settings tab for model and plugin configuration
- [x] Implement status updates and notifications
- [x] Add proper error handling and user feedback

## CLI
- [x] Fix command handling in CLI
- [x] Add model selection commands
- [x] Improve error handling and user feedback
- [x] Add help command with available commands list

## GUI
- [x] Create modern PyQt5-based GUI
- [x] Add model selection and configuration
- [x] Implement plugin management UI
- [x] Add status bar and notifications
- [x] Improve error handling and user feedback

## Performance
- [ ] Implement caching for model responses
- [ ] Add parallel execution for multi-step plans
- [ ] Optimize plugin loading and initialization
- [ ] Add model response streaming

## Security
- [ ] Add plugin sandboxing
- [ ] Implement permissions system
- [ ] Add model access control
- [ ] Secure configuration storage

## Features
- [ ] Add more plugins (system info, file operations, etc.)
- [ ] Create plugin marketplace
- [ ] Add model fine-tuning support
- [ ] Implement conversation history
- [ ] Add export/import functionality for settings

## Integration
- [ ] Add support for more model providers
- [ ] Implement WebSocket API for external tools
- [ ] Add REST API for remote control
- [ ] Create mobile app interface

## Known Issues
- [ ] Memory leaks in long-running sessions
- [ ] Connection drops with Ollama API
- [ ] Error handling in plugin system needs improvement
- [ ] GUI responsiveness during model loading
- [ ] Model switching can be slow with large models

## Documentation
- [ ] Add API documentation
- [ ] Create user guide
- [ ] Add developer documentation
- [ ] Create plugin development guide
- [ ] Add troubleshooting guide

## SystemAwareness
- [x] Refactor SystemAwarenessManager as SystemAwarenessTool and register with agent
- [x] Refactor UserRoutineAwarenessManager as UserRoutineAwarenessTool and register with agent
- [x] Refactor Device/USB/Screen/Audio handlers as DeviceAwarenessTool and register with agent
- [ ] Test CLI/GUI with new tools/agents
- [ ] Update documentation for each new tool/agent
- [ ] Add troubleshooting and cross-platform notes to README

## Model Management
- [x] Refactor ModelManager to use gemma3:1b as default
- [x] Add better error handling for model selection
- [x] Add model switching functionality
- [x] Add model availability checking
- [ ] Add model size checking before loading
- [ ] Add model quantization support
- [ ] Add model performance metrics
- [ ] Add model memory usage monitoring
- [ ] Add model response time tracking
- [ ] Add model quality assessment
- [ ] Add model fallback strategies
- [ ] Add model caching for faster responses
- [ ] Add support for specialized models (e.g., coding, embedding)
- [ ] Add model size recommendations based on system specs

## Testing
- [ ] Add model selection tests
- [ ] Add model switching tests
- [ ] Add model fallback tests
- [ ] Add model performance tests
- [ ] Add model memory tests
- [ ] Add model response time tests
- [ ] Add model quality tests
- [ ] Add model caching tests
- [ ] Add model security tests
- [ ] Add model maintenance tests

## Interaction Awareness
- [x] Create InteractionAwarenessTool for cross-platform UI interaction
- [x] Add mouse and keyboard monitoring
- [x] Add system resource monitoring
- [x] Add screenshot and image recognition
- [x] Add audio transcription support
- [ ] Add tests for all interaction features
- [ ] Add error handling for missing dependencies
- [ ] Add performance optimization for image recognition
- [ ] Add caching for system info
- [ ] Add rate limiting for resource-intensive operations

## Speech Tool (TTS/STT)
- [x] Create SpeechTool for cross-platform TTS and STT
- [x] Register SpeechTool with agent for A2A/MCP/SmolAgents
- [x] Add pyttsx3/system TTS fallback for TTS
- [x] Add Whisper support for STT
- [ ] Add tests for TTS and STT
- [ ] Add error handling for missing dependencies
- [ ] Add language/voice selection for TTS
- [ ] Add streaming STT support
- [ ] Add CLI/GUI integration examples

## Display Tool
- [x] Create DisplayTool for GUI output
- [x] Add emoji display support
- [x] Add text display with customization
- [x] Add image display support
- [x] Add window configuration
- [ ] Add tests for display features
- [ ] Add error handling for missing fonts
- [ ] Add support for custom fonts
- [ ] Add animation support
- [ ] Add layout customization
- [ ] Add widget positioning
- [ ] Add theme support

## Dependencies
- [x] Use PyAutoGUI for cross-platform GUI automation
- [x] Use psutil for system monitoring
- [x] Use pynput for input monitoring
- [x] Use Pillow for image processing
- [x] Use Whisper for audio transcription
- [x] Use pyttsx3 for TTS (offline, cross-platform)
- [x] Use system TTS fallback (say/espeak/SAPI)
- [x] Use Whisper for STT (offline, cross-platform)
- [x] Use PyQt5 for GUI output
- [ ] Add font fallback system
- [ ] Add image format validation
- [ ] Add dependency version checks
- [ ] Add dependency documentation
- [ ] Add dependency testing

## Dependency Management
- [ ] Create requirements.txt with all dependencies
- [ ] Create setup.py with proper dependency specifications
- [ ] Add dependency version constraints
- [ ] Add platform-specific dependency handling
- [ ] Add dependency conflict resolution
- [ ] Add automatic dependency installation script
- [ ] Add dependency verification script
- [ ] Add dependency documentation

## Installation Scripts
- [ ] Create install.sh for Unix systems
- [ ] Create install.bat for Windows
- [ ] Add virtual environment setup
- [ ] Add dependency verification
- [ ] Add platform detection
- [ ] Add error handling
- [ ] Add installation logging

## JSON Handling
- [x] Implement JSONTool using orjson for fast, correct JSON handling
- [x] Add orjson to requirements.txt and document in README
- [ ] Test JSONTool with various valid/invalid JSON inputs
- [ ] Integrate JSONTool with agent/plan execution for robust parsing

## CLI & Output System
- [x] Recreate CLI with emoji-rich, professional prompt and output
- [x] Remove GUI for now
- [x] Fix config path: always load config/output_styles.json from project root
- [x] Register DefaultTool for unknown/fallback actions
- [x] Improve fallback output: friendly message for unknown actions, greeting for 'hi', etc.
- [ ] Test fallback and greeting logic in CLI
- [ ] Test multi-language fallback and greeting
- [ ] Test all output types (success, error, info, warning) in CLI
- [ ] Test multi-language output and emoji support

## CLI/Output/Tool Routing Critical Fixes
- [ ] Audit and fix all config path references to ensure only config/output_styles.json in the project root is used
- [ ] Remove any fallback to src/config or code/config in all config loading logic
- [ ] Harden greeting/fallback logic so that 'hi', 'hello', etc. always return a friendly greeting and never 'True' or 'Done.'
- [ ] Explicitly map device/system commands (mouse, calculator, click, screen) to the correct tool in the agent's plan creation logic
- [ ] Test with commands: 'hi', 'hello', 'move mouse to 100,100', 'open calculator', 'click at 120,120', 'what is on my screen?'
- [ ] Confirm all output is emoji-rich, professional, and user-friendly
- [ ] Confirm A2A, MCP, SmolAgents principles are followed for all interactions
- [ ] Document and test all fixes

## Remaining Detailed Tasks (Compliance, Multi-Language, Multi-System, Testing, Platform Isolation)

### A2A, MCP, SmolAgents Compliance
- [ ] Review all agent, tool, and workflow classes for composability and minimalism
- [ ] Ensure all tools/agents support dynamic registration and discovery
- [ ] Add/verify docstrings for A2A, MCP, SmolAgents compliance in all agent/tool files
- [ ] Add tests for agent-to-agent (A2A) workflows and multi-agent planning
- [ ] Document agent-to-agent and multi-agent orchestration patterns

### Multi-Language & Multi-System
- [ ] Audit all user-facing strings for i18n readiness (wrap in translation functions)
- [ ] Add language selection and fallback logic in CLI/GUI
- [ ] Add multi-language support for greetings, errors, and help output
- [ ] Add tests for multi-language output (Arabic, English, etc.)
- [ ] Document how to add new languages and translation files
- [ ] Ensure all platform-specific code is isolated and does not affect other OSes
- [ ] Add/verify platform detection logic in PlatformManager only
- [ ] Add tests for platform isolation (Ubuntu, Windows, macOS)

### Testing and Validation
- [ ] Add/expand unit and integration tests for all refactored tools (ShellTool, FileTool, etc.)
- [ ] Add tests for platform-specific logic in PlatformManager
- [ ] Add tests for agent planning and execution (single and multi-step)
- [ ] Add tests for plugin loading and error handling
- [ ] Add tests for fallback and greeting logic in CLI/GUI
- [ ] Add tests for multi-language and multi-system scenarios
- [ ] Add CI job to run audit_project.py and fail on violations
- [ ] Add test coverage reporting to CI

### Documentation and TODOs
- [ ] Update README.md with new architecture, naming, and compliance notes
- [ ] Add install requirements for each OS and language (list dependencies per platform)
- [ ] Document audit script usage and enforcement process
- [ ] Add section on A2A, MCP, SmolAgents compliance in developer docs
- [ ] Add section on multi-language and multi-system support in user and dev docs
- [ ] Add troubleshooting for common platform/language issues
- [ ] Keep this TODO list up to date as tasks are completed

### OS Detection and Isolation
- [ ] Ensure all OS detection is handled in PlatformManager only
- [ ] Remove any direct platform/system checks from tools/agents
- [ ] Add/verify auto-detection of development OS in install scripts
- [ ] Add platform-specific install instructions to README and install scripts
- [ ] Add tests for OS detection and isolation logic
- [ ] Document platform isolation strategy in developer docs 