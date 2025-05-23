#!/usr/bin/env python3
import os
import sys
import subprocess
import re
from uaibot.output_formatter import formatter

def run_test_command(command, use_no_safe_mode=True):
    """
    Run a test command with UaiBot and capture its output using the formatter.
    
    Args:
        command: The command to execute
        use_no_safe_mode: Whether to use the --no-safe-mode flag
        
    Returns:
        Tuple of (stdout, stderr, return_code)
    """
    # Get the project directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    
    # Build the command with appropriate flags
    cmd = ["python", os.path.join(project_dir, "main.py"), "-f"]
    if use_no_safe_mode:
        cmd.append("--no-safe-mode")
    cmd.extend(["-c", command])
    
    print("\n" + "="*80)
    print(f"Testing command: {command}")
    print("="*80)
    
    # Execute the command and capture output
    process = subprocess.run(cmd, text=True, capture_output=True)
    
    # Use the formatter to print the output once
    formatted_output = formatter.format_command_output(
        " ".join(cmd), 
        process.stdout, 
        process.stderr, 
        process.returncode
    )
    
    print(formatted_output)
    return process.stdout, process.stderr, process.returncode

def analyze_output_duplicates(stdout):
    """
    Analyze the output for duplications and inconsistent formatting.
    
    Args:
        stdout: The standard output to analyze
        
    Returns:
        A dictionary with analysis results
    """
    # Look for thinking boxes
    thinking_boxes = re.findall(r"🤔 Thinking\.\.\..*?└.*?┘", stdout, re.DOTALL)
    
    # Look for duplicate command executions
    command_outputs = re.findall(r"📌 I'll execute this command: .*?(?=(\n\n|$))", stdout, re.DOTALL)
    
    # Look for multiple result outputs
    result_outputs = re.findall(r"(✅|❌|ℹ️) .*?(?=(\n\n|$))", stdout, re.DOTALL)

    return {
        "thinking_boxes": len(thinking_boxes),
        "command_outputs": len(command_outputs),
        "result_outputs": len(result_outputs),
        "total_output_blocks": len(thinking_boxes) + len(command_outputs) + len(result_outputs)
    }

def main():
    """Main function to test and fix output duplication."""
    # Test cases that demonstrated output duplication issue
    test_cases = [
        "Display all files in test_files",
        "in new firefox page goto google.com , in search barwrite: Kuwait",
        "Create an image file test_files/drawing.png and draw a red circle in it."
    ]
    
    for command in test_cases:
        # Run the command and get output
        stdout, stderr, return_code = run_test_command(command)
        
        # Analyze for duplicates
        analysis = analyze_output_duplicates(stdout)
        
        print("\n" + "-"*80)
        print("Output Analysis:")
        print(f"  Thinking boxes: {analysis['thinking_boxes']}")
        print(f"  Command outputs: {analysis['command_outputs']}")
        print(f"  Result outputs: {analysis['result_outputs']}")
        print(f"  Total output blocks: {analysis['total_output_blocks']}")
        
        if analysis["total_output_blocks"] > 3:  # More than expected (thinking, command, result)
            print(f"❌ Detected duplicate outputs: {analysis['total_output_blocks']} blocks")
        else:
            print(f"✅ Output format appears correct: {analysis['total_output_blocks']} blocks")
        print("-"*80)

if __name__ == "__main__":
    main()
