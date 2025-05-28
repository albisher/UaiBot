# Labeeb Project TODO List

Last updated: 2025-05-28 12:06:47

## Project Audit Findings

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/tools/calculator_tools.py
  - Suggestion: Abstract OS-dependent logic from 'calculator_tools.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/tools/calculator_tools.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/tools/app_control_tool.py
  - Suggestion: Abstract OS-dependent logic from 'app_control_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/tools/app_control_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/ai/tools/calculator_tools.py
  - Suggestion: Abstract OS-dependent logic from 'calculator_tools.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/ai/tools/calculator_tools.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/app/core/ai/tools/system_tool.py
  - Suggestion: Abstract OS-dependent logic from 'system_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/app/core/ai/tools/system_tool.py' to 'allowed_platform_check_files' in project rules.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/file_tool.py
  - Suggestion: Review 'file_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/file_tool.py
  - Suggestion: Review 'file_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/file_tool.py
  - Suggestion: Review 'file_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/vision_tool.py
  - Suggestion: Review 'vision_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/vision_tool.py
  - Suggestion: Review 'vision_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/vision_tool.py
  - Suggestion: Review 'vision_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/tool_registry.py
  - Suggestion: Review 'tool_registry.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/tool_registry.py
  - Suggestion: Review 'tool_registry.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/tool_registry.py
  - Suggestion: Review 'tool_registry.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/calculator_tools.py
  - Suggestion: Review 'calculator_tools.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/calculator_tools.py
  - Suggestion: Review 'calculator_tools.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/calculator_tools.py
  - Suggestion: Review 'calculator_tools.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

### AGENT_COMPLIANCE
- Potential lack of A2A compliance.
  - File: src/app/core/ai/tools/system_tool.py
  - Suggestion: Review 'system_tool.py' for A2A patterns (e.g., method calls, class structures related to 'A2A|Agent2Agent|agent_to_agent'). Refer to A2A guidelines.

### AGENT_COMPLIANCE
- Potential lack of MCP compliance.
  - File: src/app/core/ai/tools/system_tool.py
  - Suggestion: Review 'system_tool.py' for MCP patterns (e.g., method calls, class structures related to 'MCP|ModelContextProtocol|multi_channel_protocol'). Refer to MCP guidelines.

### AGENT_COMPLIANCE
- Potential lack of SmolAgents compliance.
  - File: src/app/core/ai/tools/system_tool.py
  - Suggestion: Review 'system_tool.py' for SmolAgents patterns (e.g., method calls, class structures related to 'SmolAgent|smol_agent|minimal_agent'). Refer to SmolAgents guidelines.

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

### PROJECT_NAMING
- Found old project name reference (matching 'uai|Uai|UAIBOT|UaiBot') instead of 'Labeeb'.
  - File: README.md
  - Suggestion: Replace old project names with 'Labeeb' in 'README.md'.

### PROJECT_NAMING
- Found old project name reference (matching 'uai|Uai|UAIBOT|UaiBot') instead of 'Labeeb'.
  - File: review/cli_sequence_audit.md
  - Suggestion: Replace old project names with 'Labeeb' in 'cli_sequence_audit.md'.

