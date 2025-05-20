import os
import re
import json
import datetime
from pathlib import Path

def update_command_patterns(add_patterns=True):
    """
    Update the command_patterns.json file with enhanced patterns for better intent recognition.
    If add_patterns=True, it will add new patterns without removing existing ones.
    If add_patterns=False, it will replace the file with a comprehensive set of new patterns.
    """
    # Path to the command_patterns.json file
    patterns_file = Path(os.path.expanduser("~/Documents/code/UaiBot/config/command_patterns.json"))
    
    # Create the directory if it doesn't exist
    os.makedirs(patterns_file.parent, exist_ok=True)
    
    # Define enhanced patterns with more comprehensive matching for user intent
    enhanced_patterns = {
        "system_info": {
            "uptime": [
                r"(how\s+long|since|uptime|duration|running\s+time|system\s+on\s+time|time\s+running)",
                r"(when\s+(was|did)\s+(system|computer|pc|mac|it)\s+(start|boot|turn\s+on))",
                r"(system\s+uptime|boot\s+time|last\s+reboot)"
            ],
            "memory": [
                r"(memory|ram|available\s+memory|free\s+memory|memory\s+usage)",
                r"(how\s+much\s+(memory|ram)\s+(do\s+i\s+have|is\s+available|is\s+free|is\s+used))",
                r"(system\s+memory|ram\s+status|memory\s+status)"
            ],
            "disk_space": [
                r"(disk|space|storage|free\s+space|available\s+space|disk\s+usage)",
                r"(how\s+much\s+(disk|space|storage)\s+(do\s+i\s+have|is\s+available|is\s+free|is\s+used))",
                r"(hard\s+drive|ssd|drive\s+capacity|storage\s+capacity)"
            ],
            "system_load": [
                r"(load|system\s+load|cpu\s+load|processor\s+load)",
                r"(how\s+(busy|loaded)\s+is\s+(my\s+system|computer|cpu|processor))"
            ]
        },
        "search_queries": {
            "general_search": [
                r"(search\s+for|find|look\s+for|locate|where\s+is|where\s+are)",
                r"(can\s+you\s+(search|find|locate)|help\s+me\s+(search|find|locate))"
            ],
            "file_search": [
                r"(find|search\s+for|locate)\s+(file|files|document|documents)\s+(named|called|about|containing|with|related\s+to)",
                r"(where\s+(is|are)\s+(my|the)\s+(file|files|document|documents))",
                r"(show\s+me|list)\s+(file|files|document|documents)\s+(about|containing|with|related\s+to)"
            ],
            "folder_search": [
                r"(find|search\s+for|locate)\s+(folder|folders|directory|directories)\s+(named|called|about|containing|with|related\s+to)",
                r"(where\s+(is|are)\s+(my|the)\s+(folder|folders|directory|directories))",
                r"(show\s+me|list)\s+(folder|folders|directory|directories)\s+(about|containing|with|related\s+to)"
            ],
            "content_search": [
                r"(search|find|look)\s+(in|inside|within)\s+(file|files|document|documents|content|text)\s+for",
                r"(find|search\s+for|locate)\s+(text|string|word|phrase|pattern)\s+(in|inside|within)"
            ]
        }
    }
    
    # Additional patterns to handle more specific types of queries
    additional_patterns = {
        "application_control": {
            "open_app": [
                r"(open|launch|start|run)\s+(app|application|program|software|tool)",
                r"(open|launch|start|run)\s+([a-zA-Z0-9]+)"
            ],
            "close_app": [
                r"(close|quit|exit|stop|end)\s+(app|application|program|software|tool)",
                r"(close|quit|exit|stop|end)\s+([a-zA-Z0-9]+)"
            ]
        },
        "network_tools": {
            "ping": [
                r"(ping|check\s+connection\s+to|test\s+connection\s+to|can\s+i\s+reach)",
                r"(is\s+([a-zA-Z0-9.-]+)\s+up|is\s+([a-zA-Z0-9.-]+)\s+reachable)"
            ],
            "dns_lookup": [
                r"(lookup|resolve|get\s+ip\s+for|dns\s+for|what\s+is\s+the\s+ip\s+of)",
                r"(what\s+ip\s+does\s+([a-zA-Z0-9.-]+)\s+have|ip\s+address\s+for)"
            ]
        },
        "file_operations": {
            "create": [
                r"(create|make|new)\s+(file|directory|folder)",
                r"(create|make|new)\s+(file|directory|folder)\s+called\s+([a-zA-Z0-9_.-]+)"
            ],
            "delete": [
                r"(delete|remove|erase)\s+(file|directory|folder)",
                r"(delete|remove|erase)\s+(file|directory|folder)\s+called\s+([a-zA-Z0-9_.-]+)"
            ],
            "copy": [
                r"(copy|duplicate)\s+(file|directory|folder)",
                r"(copy|duplicate)\s+(file|directory|folder)\s+([a-zA-Z0-9_.-]+)\s+to\s+([a-zA-Z0-9_.-]+)"
            ],
            "move": [
                r"(move|rename)\s+(file|directory|folder)",
                r"(move|rename)\s+(file|directory|folder)\s+([a-zA-Z0-9_.-]+)\s+to\s+([a-zA-Z0-9_.-]+)"
            ],
            "read": [
                r"(read|show|display|cat|view|output)\s+(file|content\s+of|contents\s+of)",
                r"(what('s|\s+is)\s+(in|inside)\s+(file|the\s+file))"
            ]
        },
        "process_management": {
            "list_processes": [
                r"(show|list|see|display)\s+(processes|running\s+processes|running\s+programs)",
                r"(what('s|\s+is)\s+running|what\s+processes\s+are\s+running)"
            ],
            "kill_process": [
                r"(kill|terminate|stop|end)\s+(process|program|application)",
                r"(kill|terminate|stop|end)\s+process\s+([0-9]+)"
            ]
        },
        "general_commands": {
            "help": [
                r"(help|how\s+do\s+i|how\s+to|tutorial|guide|instruction)",
                r"(can\s+you\s+help|help\s+me|show\s+me\s+how)"
            ],
            "current_directory": [
                r"(where\s+am\s+i|current\s+directory|present\s+working\s+directory|pwd)",
                r"(what\s+directory|which\s+directory|what\s+folder|which\s+folder)"
            ]
        },
        # Arabic language patterns - new section
        "arabic_commands": {
            "file_operations": [
                r"(انشاء|انشئ|جديد|اعمل)\s+(ملف|مجلد)",
                r"(احذف|امسح|ازل)\s+(ملف|مجلد)",
                r"(اقرأ|اعرض|اظهر)\s+(ملف|محتوى)",
                r"(انسخ|انقل|غير اسم)\s+(ملف|مجلد)"
            ],
            "system_info": [
                r"(كم|ما هو|اظهر)\s+(الذاكرة|المساحة|التخزين)",
                r"(ما هو|اظهر)\s+(النظام|الجهاز)"
            ],
            "search": [
                r"(ابحث|جد|أين)\s+(ملف|مجلد|عن)",
                r"(اين|وين)\s+(الملفات|المجلدات)"
            ]
        }
    }
    
    # Combine the patterns
    if not add_patterns:
        # Complete replacement
        enhanced_patterns.update(additional_patterns)
        final_patterns = enhanced_patterns
    else:
        # Add to existing patterns
        try:
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    existing_patterns = json.load(f)
                
                # Merge existing patterns with new ones
                for category, subcategories in enhanced_patterns.items():
                    if category not in existing_patterns:
                        existing_patterns[category] = {}
                    
                    for subcategory, patterns in subcategories.items():
                        if subcategory not in existing_patterns[category]:
                            existing_patterns[category][subcategory] = patterns
                        else:
                            # Add only patterns that don't exist
                            existing_patterns[category][subcategory].extend(
                                pattern for pattern in patterns 
                                if pattern not in existing_patterns[category][subcategory]
                            )
                
                # Add additional pattern categories
                for category, subcategories in additional_patterns.items():
                    if category not in existing_patterns:
                        existing_patterns[category] = {}
                    
                    for subcategory, patterns in subcategories.items():
                        if subcategory not in existing_patterns[category]:
                            existing_patterns[category][subcategory] = patterns
                        else:
                            existing_patterns[category][subcategory].extend(
                                pattern for pattern in patterns 
                                if pattern not in existing_patterns[category][subcategory]
                            )
                
                final_patterns = existing_patterns
            else:
                # If file doesn't exist, use the complete set of new patterns
                enhanced_patterns.update(additional_patterns)
                final_patterns = enhanced_patterns
        except Exception as e:
            print(f"Error reading existing patterns: {e}")
            enhanced_patterns.update(additional_patterns)
            final_patterns = enhanced_patterns
    
    # Write the updated patterns to the file
    with open(patterns_file, 'w') as f:
        json.dump(final_patterns, f, indent=2)
    
    print(f"Command patterns updated at {patterns_file}")
    # Add a timestamp metadata entry
    final_patterns["_metadata"] = {
        "last_updated": datetime.datetime.now().isoformat(),
        "pattern_count": sum(len(patterns) for category in final_patterns.values() 
                            if isinstance(category, dict) for subcategory, patterns in category.items())
    }
    
    # Write the updated patterns with metadata to the file
    with open(patterns_file, 'w') as f:
        json.dump(final_patterns, f, indent=2)
    
    print(f"Command patterns updated at {patterns_file}")

if __name__ == "__main__":
    update_command_patterns(add_patterns=True)
    print("Pattern update complete. This will improve UaiBot's intent recognition capability.")
