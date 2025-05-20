#!/usr/bin/env python3
"""
Multilingual test suite for UaiBot.
Tests UaiBot's ability to handle both Arabic and English language requests.
"""

import os
import sys
import subprocess
import json
import platform
from datetime import datetime
import argparse

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import utility functions
from utils import get_platform_name, load_config, get_project_root

# Define test cases for both English and Arabic
ENGLISH_TEST_CASES = [
    {"name": "Create file", "command": "Create a new file called test_output.txt and write 'This is a test file' in it"},
    {"name": "Read file", "command": "Show the content of the file test_output.txt"},
    {"name": "List files", "command": "Display all files in the current directory"},
    {"name": "System info", "command": "What operating system am I using?"},
    {"name": "Disk space", "command": "Show available disk space"},
    {"name": "Delete file", "command": "Delete the file test_output.txt"}
]

ARABIC_TEST_CASES = [
    {"name": "Create file (AR)", "command": "أنشئ ملف جديد باسم test_output_ar.txt واكتب فيه 'هذا ملف اختبار'"},
    {"name": "Read file (AR)", "command": "اعرض محتوى الملف test_output_ar.txt"},
    {"name": "List files (AR)", "command": "اعرض جميع الملفات في المجلد الحالي"},
    {"name": "System info (AR)", "command": "ما هو نظام التشغيل الذي أستخدمه؟"},
    {"name": "Disk space (AR)", "command": "أظهر المساحة المتاحة على القرص"},
    {"name": "Delete file (AR)", "command": "احذف الملف test_output_ar.txt"}
]

def run_uaibot_command(command, no_safe_mode=False, debug=False):
    """
    Run a UaiBot command and return its output.
    
    Args:
        command: Command to run
        no_safe_mode: Whether to run with --no-safe-mode flag
        debug: Whether to run in debug mode
        
    Returns:
        tuple: (stdout, stderr, returncode)
    """
    cmd = [sys.executable, os.path.join(project_root, "main.py")]
    
    # Add flags
    if no_safe_mode:
        cmd.append("--no-safe-mode")
    if debug:
        cmd.append("--debug")
        
    # Add command
    cmd.extend(["-c", command])
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)
        return stdout, stderr, process.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out after 30 seconds", 1
    except Exception as e:
        return "", f"Error executing command: {e}", 1

def validate_output(output, command, language="English"):
    """
    Validate if the output seems appropriate for the given command.
    
    Args:
        output: Command output to validate
        command: Original command that was run
        language: Language of the command
        
    Returns:
        tuple: (is_valid, reason)
    """
    # Basic validation - check if we got any output
    if not output.strip():
        return False, "Empty output"
    
    # Check for common error indicators
    if "error" in output.lower() or "خطأ" in output:
        return False, "Error found in output"
    
    # Look for specific expected content based on command
    if "create" in command.lower() or "أنشئ" in command:
        if "created" in output.lower() or "تم إنشاء" in output or "test_output" in output:
            return True, "File creation confirmed"
        return False, "No confirmation of file creation"
        
    elif "show" in command.lower() or "اعرض" in command.lower() or "read" in command.lower():
        if "this is a test file" in output.lower() or "هذا ملف اختبار" in output:
            return True, "File content found"
        if "content" in output.lower() or "محتوى" in output:
            return True, "Content reference found"
        return False, "No file content found"
        
    elif "list" in command.lower() or "display" in command.lower() or "اعرض جميع" in command:
        if "test_output" in output.lower():
            return True, "File listing includes test files"
        if "directory" in output.lower() or "files" in output.lower() or "ملفات" in output:
            return True, "Directory content mentioned"
        return False, "No directory listing found"
        
    elif "system" in command.lower() or "نظام التشغيل" في command:
        platforms = ["windows", "mac", "linux", "ubuntu", "darwin", "ويندوز", "لينكس", "ماك"]
        if any(platform in output.lower() for platform in platforms):
            return True, "OS information found"
        return False, "No OS information found"
        
    elif "disk" in command.lower() or "المساحة" في command:
        if "gb" in output.lower() or "mb" in output.lower() or "جيجا" in output or "ميجا" in output:
            return True, "Disk space information found"
        if "available" in output.lower() or "free" in output.lower() or "متاحة" in output:
            return True, "Available space mentioned"
        return False, "No disk space information found"
        
    elif "delete" in command.lower() or "احذف" في command:
        if "deleted" in output.lower() or "removed" in output.lower() or "تم حذف" in output:
            return True, "File deletion confirmed"
        if "test_output" in output.lower():
            return True, "Target file mentioned"
        return False, "No confirmation of file deletion"
    
    # Generic validation for unknown command types
    # Consider basic length as a fallback validation
    if len(output) > 10:
        return True, "Output appears to have content"
        
    return False, "Failed generic validation"

def run_tests(language="both", debug=False, verbose=True):
    """
    Run tests in the specified language.
    
    Args:
        language: Language to test ("english", "arabic", or "both")
        debug: Whether to run commands in debug mode
        verbose: Whether to print detailed output
        
    Returns:
        dict: Results of the test run
    """
    results = {
        "english": {"passed": 0, "failed": 0, "details": []},
        "arabic": {"passed": 0, "failed": 0, "details": []}
    }
    
    test_cases = []
    if language.lower() == "english" or language.lower() == "both":
        test_cases.extend([(case, "english") for case in ENGLISH_TEST_CASES])
    if language.lower() == "arabic" or language.lower() == "both":
        test_cases.extend([(case, "arabic") for case in ARABIC_TEST_CASES])
    
    # Print header
    if verbose:
        platform_name = get_platform_name()
        print(f"\n===== UaiBot Multilingual Test Suite =====")
        print(f"Platform: {platform_name}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Languages: {language.title()}")
        print("=" * 45 + "\n")
    
    # Run each test case
    for case, lang in test_cases:
        if verbose:
            print(f"[{lang.upper()}] Running test: {case['name']}")
            print(f"Command: {case['command']}")
            
        # Special handling for potentially dangerous commands
        no_safe_mode = False
        if "delete" in case['command'].lower() or "احذف" في case['command']:
            no_safe_mode = True
        
        # Run the command
        stdout, stderr, returncode = run_uaibot_command(case['command'], no_safe_mode, debug)
        
        # Validate the output
        is_valid, reason = validate_output(stdout, case['command'], lang)
        
        # Store result
        test_result = {
            "name": case['name'],
            "command": case['command'],
            "returncode": returncode,
            "succeeded": is_valid,
            "reason": reason,
            "stdout": stdout.strip(),
            "stderr": stderr.strip() if stderr else ""
        }
        
        results[lang.lower()]["details"].append(test_result)
        if is_valid:
            results[lang.lower()]["passed"] += 1
        else:
            results[lang.lower()]["failed"] += 1
            
        # Print result
        if verbose:
            status = "✅ Passed" if is_valid else "❌ Failed"
            print(f"Result: {status} - {reason}")
            
            # If requested or if test failed, show output
            if verbose and not is_valid:
                print("\nOutput:")
                print("-" * 40)
                print(stdout)
                if stderr:
                    print("\nErrors:")
                    print(stderr)
                print("-" * 40)
            print("")
    
    # Print summary
    if verbose:
        print("\n===== Test Summary =====")
        for lang in ['english', 'arabic']:
            if lang in results and (results[lang]["passed"] > 0 or results[lang]["failed"] > 0):
                total = results[lang]["passed"] + results[lang]["failed"]
                print(f"{lang.title()}: {results[lang]['passed']}/{total} passed" + 
                    f" ({results[lang]['passed']/total*100:.1f}%)" if total > 0 else "")
    
    return results

def save_results(results, output_dir=None):
    """Save test results to a JSON file."""
    if output_dir is None:
        output_dir = os.path.join(project_root, "tests", "results")
        
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"multilingual_test_results_{timestamp}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    return filename

def generate_report(results, output_file=None):
    """Generate a markdown report from test results."""
    if output_file is None:
        output_dir = os.path.join(project_root, "tests", "reports")
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"multilingual_test_report_{timestamp}.md")
    
    platform_name = get_platform_name()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Initialize the report content
    report = f"""# UaiBot Multilingual Test Report

**Platform:** {platform_name}  
**Date:** {timestamp}  

## Summary

"""

    # Add summary information
    for lang in ['english', 'arabic']:
        if lang in results and (results[lang]["passed"] > 0 or results[lang]["failed"] > 0):
            total = results[lang]["passed"] + results[lang]["failed"]
            percentage = (results[lang]['passed']/total*100) if total > 0 else 0
            report += f"### {lang.title()}\n"
            report += f"- **Passed:** {results[lang]['passed']}/{total} ({percentage:.1f}%)\n"
            report += f"- **Failed:** {results[lang]['failed']}/{total} ({100-percentage:.1f}%)\n\n"

    # Add detailed results
    for lang in ['english', 'arabic']:
        if lang in results and results[lang]["details"]:
            report += f"## Detailed {lang.title()} Results\n\n"
            
            for test in results[lang]["details"]:
                status = "✅ Passed" if test["succeeded"] else "❌ Failed"
                report += f"### {test['name']}: {status}\n\n"
                report += f"**Command:** `{test['command']}`\n\n"
                report += f"**Reason:** {test['reason']}\n\n"
                
                # Include output for failed tests
                if not test["succeeded"]:
                    report += "**Output:**\n\n```\n"
                    report += test["stdout"] if test["stdout"] else "(No output)"
                    report += "\n```\n\n"
                    
                    if test["stderr"]:
                        report += "**Errors:**\n\n```\n"
                        report += test["stderr"]
                        report += "\n```\n\n"
                        
                report += "---\n\n"

    # Write the report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
        
    return output_file

def main():
    """Main entry point for multilingual testing."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Test UaiBot's multilingual capabilities")
    parser.add_argument("--language", "-l", choices=["english", "arabic", "both"], 
                      default="both", help="Language to test")
    parser.add_argument("--debug", "-d", action="store_true", help="Run in debug mode")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (minimal output)")
    parser.add_argument("--output", "-o", help="Output directory for results")
    args = parser.parse_args()
    
    # Run tests
    results = run_tests(language=args.language, debug=args.debug, verbose=not args.quiet)
    
    # Save results
    results_file = save_results(results, args.output)
    if not args.quiet:
        print(f"\nResults saved to: {results_file}")
    
    # Generate report
    report_file = generate_report(results)
    if not args.quiet:
        print(f"Report saved to: {report_file}")
    
    # Calculate overall success
    total_passed = sum(results[lang]["passed"] for lang in results)
    total_tests = sum(results[lang]["passed"] + results[lang]["failed"] for lang in results)
    return 0 if total_passed == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
