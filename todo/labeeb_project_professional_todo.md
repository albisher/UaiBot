# Labeeb Project TODO List

Last updated: 2025-05-27 09:48:16

## Project Audit Findings

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_commands.py
  - Suggestion: Abstract OS-dependent logic from 'platform_commands.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_commands.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/bot.py
  - Suggestion: Abstract OS-dependent logic from 'bot.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/bot.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/system_commands.py
  - Suggestion: Abstract OS-dependent logic from 'system_commands.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/system_commands.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/browser_controller.py
  - Suggestion: Abstract OS-dependent logic from 'browser_controller.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/browser_controller.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/utils/platform_utils.py
  - Suggestion: Abstract OS-dependent logic from 'platform_utils.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/utils/platform_utils.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/controller/execution_controller.py
  - Suggestion: Abstract OS-dependent logic from 'execution_controller.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/controller/execution_controller.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/audio_interface.py
  - Suggestion: Abstract OS-dependent logic from 'audio_interface.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/audio_interface.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/browser_handler.py
  - Suggestion: Abstract OS-dependent logic from 'browser_handler.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/browser_handler.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/shell_handler.py
  - Suggestion: Abstract OS-dependent logic from 'shell_handler.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/shell_handler.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/system_info_gatherer.py
  - Suggestion: Abstract OS-dependent logic from 'system_info_gatherer.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/system_info_gatherer.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/platform_manager.py
  - Suggestion: Abstract OS-dependent logic from 'platform_manager.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/platform_manager.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/ui_interface.py
  - Suggestion: Abstract OS-dependent logic from 'ui_interface.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/ui_interface.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/net_interface.py
  - Suggestion: Abstract OS-dependent logic from 'net_interface.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/net_interface.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/platform_utils.py
  - Suggestion: Abstract OS-dependent logic from 'platform_utils.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/platform_utils.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/fs_interface.py
  - Suggestion: Abstract OS-dependent logic from 'fs_interface.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/fs_interface.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/audio_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'audio_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/audio_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/app_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'app_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/app_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/terminal_tool.py
  - Suggestion: Abstract OS-dependent logic from 'terminal_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/terminal_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/network_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'network_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/network_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/system_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'system_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/system_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/speech_tool.py
  - Suggestion: Abstract OS-dependent logic from 'speech_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/speech_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/device_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'device_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/device_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/bluetooth_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'bluetooth_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/bluetooth_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/awareness/sensor_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'sensor_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/awareness/sensor_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/input/mouse.py
  - Suggestion: Abstract OS-dependent logic from 'mouse.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/input/mouse.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/screen_handler/screen_manager.py
  - Suggestion: Abstract OS-dependent logic from 'screen_manager.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/screen_handler/screen_manager.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/screen_handler/session_manager.py
  - Suggestion: Abstract OS-dependent logic from 'session_manager.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/screen_handler/session_manager.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/device_manager/usb_detector.py
  - Suggestion: Abstract OS-dependent logic from 'usb_detector.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/device_manager/usb_detector.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/tools/system_tools.py
  - Suggestion: Abstract OS-dependent logic from 'system_tools.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/tools/system_tools.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/ai/uaibot_agent.py
  - Suggestion: Abstract OS-dependent logic from 'uaibot_agent.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/ai/uaibot_agent.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/research/automation.py
  - Suggestion: Abstract OS-dependent logic from 'automation.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/research/automation.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/linux/platform.py
  - Suggestion: Abstract OS-dependent logic from 'platform.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/linux/platform.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/darwin/platform.py
  - Suggestion: Abstract OS-dependent logic from 'platform.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/darwin/platform.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform-specific named file 'initialize_mac.py' found outside designated platform directory 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/mac/initialize_mac.py
  - Suggestion: Move OS-specific file 'initialize_mac.py' into an appropriate subdirectory of 'src/app/core/platform_core/'. If it's not OS-specific, rename it.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/mac/initialize_mac.py
  - Suggestion: Abstract OS-dependent logic from 'initialize_mac.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/mac/initialize_mac.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/mac/calendar_controller.py
  - Suggestion: Abstract OS-dependent logic from 'calendar_controller.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/mac/calendar_controller.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/mac/apple_silicon.py
  - Suggestion: Abstract OS-dependent logic from 'apple_silicon.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/mac/apple_silicon.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform-specific named file 'setup_mac.py' found outside designated platform directory 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/mac/setup_mac.py
  - Suggestion: Move OS-specific file 'setup_mac.py' into an appropriate subdirectory of 'src/app/core/platform_core/'. If it's not OS-specific, rename it.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/mac/setup_mac.py
  - Suggestion: Abstract OS-dependent logic from 'setup_mac.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/mac/setup_mac.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/common/platform_factory.py
  - Suggestion: Abstract OS-dependent logic from 'platform_factory.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/common/platform_factory.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/common/system_info.py
  - Suggestion: Abstract OS-dependent logic from 'system_info.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/common/system_info.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform-specific named file 'macos_awareness.py' found outside designated platform directory 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/macos/awareness/macos_awareness.py
  - Suggestion: Move OS-specific file 'macos_awareness.py' into an appropriate subdirectory of 'src/app/core/platform_core/'. If it's not OS-specific, rename it.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/macos/awareness/macos_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'macos_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/macos/awareness/macos_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform-specific named file 'windows_awareness.py' found outside designated platform directory 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/windows/awareness/windows_awareness.py
  - Suggestion: Move OS-specific file 'windows_awareness.py' into an appropriate subdirectory of 'src/app/core/platform_core/'. If it's not OS-specific, rename it.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/windows/awareness/windows_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'windows_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/windows/awareness/windows_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/common/awareness/awareness_factory.py
  - Suggestion: Abstract OS-dependent logic from 'awareness_factory.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/common/awareness/awareness_factory.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform-specific named file 'ubuntu_awareness.py' found outside designated platform directory 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/ubuntu/awareness/ubuntu_awareness.py
  - Suggestion: Move OS-specific file 'ubuntu_awareness.py' into an appropriate subdirectory of 'src/app/core/platform_core/'. If it's not OS-specific, rename it.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/platform_core/ubuntu/awareness/ubuntu_awareness.py
  - Suggestion: Abstract OS-dependent logic from 'ubuntu_awareness.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/platform_core/ubuntu/awareness/ubuntu_awareness.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/ai/agent_tools/keyboard_control_tool.py
  - Suggestion: Abstract OS-dependent logic from 'keyboard_control_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/ai/agent_tools/keyboard_control_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/ai/agent_tools/system_awareness_tool.py
  - Suggestion: Abstract OS-dependent logic from 'system_awareness_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/ai/agent_tools/system_awareness_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/ai/agent_tools/mouse_control_tool.py
  - Suggestion: Abstract OS-dependent logic from 'mouse_control_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/ai/agent_tools/mouse_control_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/ai/agent_tools/window_control_tool.py
  - Suggestion: Abstract OS-dependent logic from 'window_control_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/ai/agent_tools/window_control_tool.py' to 'allowed_platform_check_files' in project rules.

### PLATFORM_ISOLATION
- Platform detection code (e.g., sys.platform) found in file not under 'src/app/core/platform_core'.
  - File: src/labeeb/core/ai/agent_tools/network_tool.py
  - Suggestion: Abstract OS-dependent logic from 'network_tool.py' into modules within 'src/app/core/platform_core'. If this file must check OS (e.g. main script), consider adding 'src/labeeb/core/ai/agent_tools/network_tool.py' to 'allowed_platform_check_files' in project rules.

### PROJECT_NAMING
- Found old project name reference (matching 'uai|Uai|UAIBOT|UaiBot') instead of 'Labeeb'.
  - File: docs/secret/prompt.md
  - Suggestion: Replace old project names with 'Labeeb' in 'prompt.md'.

