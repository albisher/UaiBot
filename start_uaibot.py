#!/usr/bin/env python3
"""
UaiBot Launcher Script
This script automatically chooses the best way to start UaiBot based on your environment.
"""
import os
import sys
import platform
import subprocess
import traceback
from pathlib import Path

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

try:
    from core.utils import load_config, get_platform_name
    from platform_uai.platform_manager import PlatformManager
except ImportError as e:
    print(f"Error importing UaiBot modules: {e}")
    print(f"Make sure you're running from the project root directory.")
    sys.exit(1)

def check_gui_available():
    """Check if GUI components are available"""
    try:
        import PyQt5
        return True
    except ImportError:
        return False

def main():
    """Main entry point for the launcher"""
    print("UaiBot Launcher")
    print("--------------")
    
    try:
        # Initialize platform manager for better platform detection
        platform_manager = PlatformManager()
        platform_info = platform_manager.get_platform_info()
        print(f"Detected platform: {platform_info['name']}")
        
        # Load configuration
        config = load_config()
        if not config:
            print("Warning: Failed to load configuration. Using default settings.")
            config = {"use_gui": False}
        
        # Check if GUI is available and preferred
        gui_available = check_gui_available()
        use_gui = False
        
        if gui_available:
            print("GUI components available.")
            # Check config setting
            if config and config.get("use_gui", False):
                print("GUI mode enabled in configuration.")
                use_gui = True
            
            # On macOS, always prefer GUI if available
            if platform.system() == "Darwin":
                print("macOS detected - preferring GUI mode.")
                use_gui = True
                
            # Check if we have a display server (Linux)
            if not os.environ.get('DISPLAY') and platform.system() != "Darwin":
                print("No display detected. Falling back to command-line mode.")
                use_gui = False
        else:
            print("GUI components not available. Running in command-line mode.")
            use_gui = False
        
        # Parse command-line arguments
        args = sys.argv[1:]
        
        # Override detection if specific flags are present
        if "--gui" in args or "-g" in args:
            if not gui_available:
                print("Error: GUI requested but PyQt5 is not installed.")
                print("Please install PyQt5: pip install PyQt5")
                return 1
            use_gui = True
            # Remove the GUI flag to avoid duplication
            if "--gui" in args:
                args.remove("--gui")
            if "-g" in args:
                args.remove("-g")
        
        if "--no-gui" in args:
            use_gui = False
            # Remove the no-GUI flag to avoid duplication
            if "--no-gui" in args:
                args.remove("--no-gui")
        
        # Build the command
        if use_gui:
            print("Starting in GUI mode...")
            cmd = [sys.executable, "gui/gui_launcher.py"]
            cmd.extend(args)
        else:
            print("Starting in command-line mode...")
            cmd = [sys.executable, "main.py"]
            cmd.extend(args)
        
        # Execute the command
        print(f"Executing: {' '.join(cmd)}")
        return subprocess.run(cmd).returncode
        
    except Exception as e:
        print(f"Error starting UaiBot: {e}")
        print(traceback.format_exc())
        return 1
    
if __name__ == "__main__":
    sys.exit(main())
