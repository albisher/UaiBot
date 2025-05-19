#!/usr/bin/env python3
"""
Demo for the Enhanced Output Processor

This script demonstrates how the EnhancedOutputProcessor formats
various command outputs with consistent theming and styling.
"""

import os
import sys
import time

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.append(project_root)

from terminal_commands.enhanced_output_processor import EnhancedOutputProcessor

# Sample outputs from various commands
SAMPLE_OUTPUTS = {
    "uptime": "14:30  up 3 days, 2:14, 5 users, load averages: 1.20 1.33 1.42",
    
    "disk_space": """Filesystem     Size    Used   Avail Capacity    iused   ifree %iused  Mounted on
/dev/disk1s5s1  466Gi  15.1Gi  370Gi     4%     52110 4881892    1%   /
/dev/disk1s4    466Gi  80.1Gi  370Gi    18%    484008 4881892    9%   /System/Volumes/Data
/dev/disk1s3    466Gi   5.0Gi  370Gi     2%         5 4881892    0%   /private/var/vm
/dev/disk2s1    931Gi  780Gi   151Gi    84%     52110 4881892   45%   /Volumes/External""",
    
    "memory": """Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                              195298.
Pages active:                            711464.
Pages inactive:                          498402.
Pages speculative:                        28822.
Pages throttled:                              0.
Pages wired down:                        218535.
Pages purgeable:                          43781.
"Translation faults":                 339127381.
Pages copy-on-write:                   10452571.
Pages zero filled:                    134294544.
Pages reactivated:                     14292246.
Pages purged:                           3075465.
File-backed pages:                       584993.
Anonymous pages:                         653695.
Pages stored in compressor:              511485.
Pages occupied by compressor:            140491.
Decompressions:                         5160397.
Compressions:                           7904975.
Pageins:                               53336701.
Pageouts:                                946292.
Swapins:                                1343392.
Swapouts:                               1822608.""",
    
    "notes_topics": """{"Personal", "Work", "Shopping Lists", "Project Ideas", "Travel", "Recipes"}""",
    
    "processes": """  PID %CPU %MEM      VSZ    RSS   TT  STAT STARTED      TIME COMMAND
91769  5.7  0.8  5223044  64548   ??  S    10:23AM   0:18.23 /Applications/Visual Studio Code.app/Contents/MacOS/Electron
 1021  4.0  0.6  5918128  52204   ??  S     9:15AM   1:01.34 /Applications/Firefox.app/Contents/MacOS/firefox
 4125  3.5  1.2  6204124  98324   ??  S    10:45AM   0:22.55 /Applications/Slack.app/Contents/MacOS/Slack
   34  2.8  0.1  4334992   8744   ??  S    Fri09AM  28:11.61 /usr/libexec/airportd
  453  1.9  0.7  5740036  58280   ??  S    Fri09AM  19:41.83 /System/Library/CoreServices/Finder.app/Contents/MacOS/Finder""",
    
    "system_status": """{
    "hostname": "mac-pro",
    "uptime": "3 days, 2:14",
    "load_average": "1.20 1.33 1.42",
    "cpu_usage": "24%",
    "memory_available": "8.2 GB",
    "disk_space_free": "370GB",
    "network_status": "Connected",
    "warnings": ["Battery health is at 85%", "System update available"],
    "errors": []
}"""
}

def demo_processor_outputs(processor, theme_name):
    """Demonstrate all outputs with a specific theme"""
    divider = "=" * 80
    print(f"\n{divider}")
    print(f"Theme: {theme_name}")
    print(f"{divider}")
    
    # Process and print each output type
    print("\n" + processor.process_uptime(SAMPLE_OUTPUTS["uptime"]))
    print("\n" + processor.process_disk_space(SAMPLE_OUTPUTS["disk_space"]))
    print("\n" + processor.process_memory(SAMPLE_OUTPUTS["memory"]))
    print("\n" + processor.process_notes_topics(SAMPLE_OUTPUTS["notes_topics"]))
    print("\n" + processor.process_running_processes(SAMPLE_OUTPUTS["processes"]))
    print("\n" + processor.process_system_status(SAMPLE_OUTPUTS["system_status"]))

def main():
    """Main function to run the demo"""
    print("Enhanced Output Processor Demo")
    
    # Create a processor for each theme
    themes = ["default", "minimal", "professional"]
    
    for theme in themes:
        processor = EnhancedOutputProcessor(theme=theme)
        demo_processor_outputs(processor, theme)
        time.sleep(0.5)  # Pause briefly between themes
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main()
