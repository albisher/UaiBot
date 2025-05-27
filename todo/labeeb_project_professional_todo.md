# Labeeb Project TODO List

Last updated: 2025-05-27 12:00:04

## Project Audit Findings

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/controller/execution_controller.py
  - Suggestion: Abstract OS-dependent logic from 'execution_controller.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/controller/execution_controller.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/network_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'network_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/network_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/system_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'system_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/system_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/speech_tool.py
  - Suggestion: Abstract OS-dependent logic from 'speech_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/speech_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/screen_handler/screen_manager.py
  - Suggestion: Abstract OS-dependent logic from 'screen_manager.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/screen_handler/screen_manager.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/screen_handler/session_manager.py
  - Suggestion: Abstract OS-dependent logic from 'session_manager.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/screen_handler/session_manager.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/device_manager/usb_detector.py
  - Suggestion: Abstract OS-dependent logic from 'usb_detector.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/device_manager/usb_detector.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/tools/system_tools.py
  - Suggestion: Abstract OS-dependent logic from 'system_tools.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/tools/system_tools.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/ai/uaibot_agent.py
  - Suggestion: Abstract OS-dependent logic from 'uaibot_agent.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/ai/uaibot_agent.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/research/automation.py
  - Suggestion: Abstract OS-dependent logic from 'automation.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/research/automation.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/controller/execution_controller.py
  - Suggestion: Abstract OS-dependent logic from 'execution_controller.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/controller/execution_controller.py' to 'allowed_platform_check_files' in project rules.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/graph_maker_tool.py
  - Suggestion: Review 'graph_maker_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/graph_maker_tool.py
  - Suggestion: Review 'graph_maker_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/graph_maker_tool.py
  - Suggestion: Review 'graph_maker_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/base_tool.py
  - Suggestion: Review 'base_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/base_tool.py
  - Suggestion: Review 'base_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/base_tool.py
  - Suggestion: Review 'base_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/system_resource_tool.py
  - Suggestion: Review 'system_resource_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/system_resource_tool.py
  - Suggestion: Review 'system_resource_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/system_resource_tool.py
  - Suggestion: Review 'system_resource_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/screen_control_tool.py
  - Suggestion: Review 'screen_control_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/screen_control_tool.py
  - Suggestion: Review 'screen_control_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/screen_control_tool.py
  - Suggestion: Review 'screen_control_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/file_and_document_organizer_tool.py
  - Suggestion: Review 'file_and_document_organizer_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/file_and_document_organizer_tool.py
  - Suggestion: Review 'file_and_document_organizer_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/file_and_document_organizer_tool.py
  - Suggestion: Review 'file_and_document_organizer_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/datetime_tool.py
  - Suggestion: Review 'datetime_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/datetime_tool.py
  - Suggestion: Review 'datetime_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/datetime_tool.py
  - Suggestion: Review 'datetime_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/code_path_updater_tool.py
  - Suggestion: Review 'code_path_updater_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/code_path_updater_tool.py
  - Suggestion: Review 'code_path_updater_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/code_path_updater_tool.py
  - Suggestion: Review 'code_path_updater_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/clipboard_tool.py
  - Suggestion: Review 'clipboard_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/clipboard_tool.py
  - Suggestion: Review 'clipboard_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/clipboard_tool.py
  - Suggestion: Review 'clipboard_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/__init__.py
  - Suggestion: Review '__init__.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/__init__.py
  - Suggestion: Review '__init__.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/__init__.py
  - Suggestion: Review '__init__.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/agents/information_collector.py
  - Suggestion: Review 'information_collector.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/agents/information_collector.py
  - Suggestion: Review 'information_collector.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/agents/information_collector.py
  - Suggestion: Review 'information_collector.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/agents/planner.py
  - Suggestion: Review 'planner.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/agents/planner.py
  - Suggestion: Review 'planner.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/agents/planner.py
  - Suggestion: Review 'planner.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/agents/researcher.py
  - Suggestion: Review 'researcher.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/agents/researcher.py
  - Suggestion: Review 'researcher.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/agents/researcher.py
  - Suggestion: Review 'researcher.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/agents/research_evaluator.py
  - Suggestion: Review 'research_evaluator.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/agents/research_evaluator.py
  - Suggestion: Review 'research_evaluator.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/agents/research_evaluator.py
  - Suggestion: Review 'research_evaluator.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/agents/uaibot_agent.py
  - Suggestion: Review 'uaibot_agent.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/agents/uaibot_agent.py
  - Suggestion: Review 'uaibot_agent.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/agents/uaibot_agent.py
  - Suggestion: Review 'uaibot_agent.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### PROJECT_NAMING
- Found old project name reference (matching 'uai|Uai|UAIBOT|UaiBot') instead of 'Labeeb'.
  - File: README.md
  - Suggestion: Replace old project names with 'Labeeb' in 'README.md'.

## Audit Findings (2024-06-11)

- [ ] The planner always maps commands to the 'echo' tool, never to MouseTool or other specialized tools.
- [ ] The plan_dict for 'move mouse', 'click mouse', etc. is always {'tool': 'echo', ...}.
- [ ] The CLI debug output confirms only EchoTool is used, regardless of input.
- [ ] The planner logic must be improved to map natural language commands to the correct tool (e.g., MouseTool for mouse commands).
- [ ] Refactor planner logic to support tool/action mapping for all registered tools, including mouse, file, datetime, calculator, etc.
- [ ] Add/expand tests for planner-tool mapping.
- [ ] Document audit results and planner limitations in README and review/cli_sequence_audit.md.
- [ ] Ensure all tool tests in tools_audit.py check for correct tool usage in CLI and --fast mode.
- [ ] Continue platform/OS isolation and i18n/RTL/Arabic support as previously planned.

## Remaining Actions

- [ ] Refactor planner to support multi-tool, multi-language, and multi-system mapping.
- [ ] Expand tool registration and ensure all tools are discoverable by the planner.
- [ ] Add/expand CLI and tool tests for all supported commands.
- [ ] Update README and review/cli_sequence_audit.md with audit results and next steps.
- [ ] Continue enforcing file organization, naming, and platform isolation rules.

