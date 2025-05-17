#!/usr/bin/env python3
"""
UaiBot Launcher Script
This script automatically chooses the best way to start UaiBot based on your environment.
"""
import os
import sys
import platform
import subprocess
from core.utils import load_config

def check_gui_available():
    """Check if GUI components are available"""
    try:
        import PyQt5
        return True
    except ImportError:
        return False

def main():
    """Main entry point for the launcher"""
    # Load configuration
    config = load_config()
    
    # Check if GUI is available and preferred
    gui_available = check_gui_available()
    use_gui = False
    
    # Determine whether to use GUI
    if gui_available:
        # Check config setting
        if config and config.get("use_gui", False):
            use_gui = True
        
        # On macOS, always prefer GUI if available
        if platform.system() == "Darwin":
            use_gui = True
            
        # Check if we have a display server (Linux)
        if not os.environ.get('DISPLAY') and platform.system() != "Darwin":
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
    cmd = [sys.executable, "main.py"]
    
    # Add GUI flag if needed
    if use_gui:
        cmd.append("--gui")
    
    # Add any remaining arguments
    cmd.extend(args)
    
    print(f"Starting UaiBot in {'GUI' if use_gui else 'command-line'} mode...")
    
    # Execute the command
    subprocess.run(cmd)
    
if __name__ == "__main__":
    sys.exit(main())
