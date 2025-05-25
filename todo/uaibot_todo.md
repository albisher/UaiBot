# UaiBot Project Todo

## Completed

- Implemented `MemoryHandler` class to manage UaiBot's state and memory.
- Updated `CommandProcessor` to handle sequential actions and utilize the new handlers.
- Fixed the call to `update_browser_state` in `CommandProcessor` to pass both browser and state arguments.
- Installed required dependencies in a virtual environment.

## Pending

- Test the sequential command functionality with the updated `CommandProcessor`.
- Implement additional features for browser interaction, such as clicking links and focusing the browser.
- Enhance error handling and logging throughout the application.
- Update documentation to reflect recent changes and new features.
- Conduct thorough testing of all implemented features to ensure stability and reliability.
- Update the `BrowserHandler` to include a 'browser_state' key in the result dictionary, even if it's an empty dictionary or a default state.
- Update the `BrowserInteractionHandler` to handle the 'default' browser case, similar to the `BrowserHandler`.
- Enhance the `click_middle_link` method to take a screenshot of the page and visually determine the middle link based on the screenshot.
- Add additional logging in the `CommandProcessor` to capture the exact result returned by the browser handlers.

# UaiBot Agentic TODO

- [ ] Refactor core pipeline to use Agent abstraction (SmolAgents)
- [ ] Convert command handlers to agent tools
- [ ] Implement agent memory/state (minimal, efficient)
- [ ] Add plan/execute loop for multi-step workflows
- [ ] Integrate A2A (Agent-to-Agent) protocol for agent collaboration
- [ ] Integrate MCP (Multi-Context Protocol) for CLI, GUI, web, etc.
- [ ] Ensure local-first, minimal memory/storage operation
- [ ] Expand multi-language and multi-platform support
- [ ] Update documentation for agentic, tool-based, A2A/MCP architecture
- [ ] Add tests for agent workflows, A2A, MCP, and tool integration
