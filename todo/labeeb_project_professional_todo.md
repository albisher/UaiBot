# Labeeb Project TODO List

Last updated: 2025-05-27 11:04:15

## Project Audit Findings

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/bot.py
  - Suggestion: Abstract OS-dependent logic from 'bot.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/bot.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/utils/platform_utils.py
  - Suggestion: Abstract OS-dependent logic from 'platform_utils.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/utils/platform_utils.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/controller/execution_controller.py
  - Suggestion: Abstract OS-dependent logic from 'execution_controller.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/controller/execution_controller.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/audio_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'audio_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/audio_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/app_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'app_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/app_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/terminal_tool.py
  - Suggestion: Abstract OS-dependent logic from 'terminal_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/terminal_tool.py' to 'allowed_platform_check_files' in project rules.

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
  - File: src/app/core/awareness/device_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'device_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/device_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/bluetooth_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'bluetooth_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/bluetooth_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/awareness/sensor_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'sensor_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/awareness/sensor_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/input/mouse.py
  - Suggestion: Abstract OS-dependent logic from 'mouse.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/input/mouse.py' to 'allowed_platform_check_files' in project rules.

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

