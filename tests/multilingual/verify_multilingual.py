#!/usr/bin/env python3
"""
Verification script for UaiBot's multilingual capabilities.
Performs focused tests on specific language features in Arabic and English.
"""

import os
import sys
import json
from uaibot.datetime import datetime

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import utility functions
from uaibot.utils import get_platform_name
from tests.test_multilingual import run_uaibot_command

# Define verification test cases
VERIFICATION_TESTS = {
    "file_operations": {
        "english": [
            "Create a new file called test_verify.txt with content 'Verification test'",
            "Read the contents of test_verify.txt",
            "Delete the file test_verify.txt"
        ],
        "arabic": [
            "أنشئ ملف جديد باسم test_verify_ar.txt واكتب فيه 'اختبار التحقق'",
            "اقرأ محتويات الملف test_verify_ar.txt",
            "احذف الملف test_verify_ar.txt"
        ]
    },
    "system_info": {
        "english": [
            "What is my operating system?",
            "Show system information",
            "How much memory is available?"
        ],
        "arabic": [
            "ما هو نظام التشغيل الخاص بي؟",
            "أظهر معلومات النظام",
            "كم هي الذاكرة المتاحة؟"
        ]
    },
    "command_execution": {
        "english": [
            "List all files in the current directory",
            "Show the current date and time",
            "Display the current working directory"
        ],
        "arabic": [
            "اعرض جميع الملفات في المجلد الحالي",
            "أظهر التاريخ والوقت الحاليين",
            "اعرض مسار المجلد الحالي"
        ]
    }
}

def verify_language_support(language, category=None, verbose=True):
    """
    Verify language support for specific categories.
    
    Args:
        language: Language to test ("english", "arabic")
        category: Specific category to test, or None for all
        verbose: Whether to print detailed output
        
    Returns:
        dict: Results of the verification
    """
    results = {
        "language": language,
        "categories": {},
        "overall_success": True
    }
    
    categories = [category] if category else VERIFICATION_TESTS.keys()
    
    for cat in categories:
        if cat not in VERIFICATION_TESTS:
            print(f"Error: Category '{cat}' not found")
            continue
            
        if verbose:
            print(f"\n=== Testing {language} {cat} ===")
            
        category_results = []
        all_succeeded = True
        
        for command in VERIFICATION_TESTS[cat][language]:
            if verbose:
                print(f"\nCommand: {command}")
                
            # Run the command, use no_safe_mode for delete commands
            no_safe_mode = "delete" in command.lower() or "احذف" in command
            stdout, stderr, returncode = run_uaibot_command(command, no_safe_mode)
            
            # Check if successful (simple validation - non-zero return code or error message)
            succeeded = returncode == 0 and "error" not in stdout.lower() and "خطأ" not in stdout
            all_succeeded = all_succeeded and succeeded
            
            # Store result
            command_result = {
                "command": command,
                "succeeded": succeeded,
                "returncode": returncode,
                "stdout": stdout.strip(),
                "stderr": stderr.strip() if stderr else ""
            }
            category_results.append(command_result)
            
            # Print result if verbose
            if verbose:
                status = "✅ Passed" if succeeded else "❌ Failed"
                print(f"Result: {status}")
                print(f"Output:")
                print("-" * 40)
                print(stdout)
                if stderr:
                    print("\nErrors:")
                    print(stderr)
                print("-" * 40)
        
        # Store category results
        results["categories"][cat] = {
            "succeeded": all_succeeded,
            "commands": category_results
        }
        
        # Update overall success
        results["overall_success"] = results["overall_success"] and all_succeeded
    
    return results

def run_verification(languages=None, categories=None, verbose=True):
    """
    Run verification tests for the specified languages and categories.
    
    Args:
        languages: List of languages to test, or None for all
        categories: List of categories to test, or None for all
        verbose: Whether to print detailed output
        
    Returns:
        dict: Verification results
    """
    if languages is None:
        languages = ["english", "arabic"]
    elif isinstance(languages, str):
        languages = [languages]
        
    verification_results = {}
    
    for language in languages:
        if verbose:
            platform_name = get_platform_name()
            print(f"\n===== UaiBot {language.title()} Verification =====")
            print(f"Platform: {platform_name}")
            print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 45)
        
        results = verify_language_support(language, categories, verbose)
        verification_results[language] = results
        
        if verbose:
            print(f"\n=== {language.title()} Verification Summary ===")
            for cat, result in results["categories"].items():
                status = "✅ Passed" if result["succeeded"] else "❌ Failed"
                print(f"{cat}: {status}")
            
            overall = "✅ Passed" if results["overall_success"] else "❌ Failed"
            print(f"\nOverall: {overall}")
    
    return verification_results

def save_verification_results(results, output_file=None):
    """Save verification results to a JSON file."""
    if output_file is None:
        output_dir = os.path.join(project_root, "tests", "results")
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"verification_results_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    return output_file

def main():
    """Main entry point for the verification script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify UaiBot's multilingual capabilities")
    parser.add_argument("--language", "-l", choices=["english", "arabic", "both"], 
                      default="both", help="Language to test")
    parser.add_argument("--category", "-c", 
                      choices=list(VERIFICATION_TESTS.keys()),
                      help="Specific category to test")
    parser.add_argument("--quiet", "-q", action="store_true", 
                      help="Quiet mode (minimal output)")
    parser.add_argument("--output", "-o", 
                      help="Output file for results")
    args = parser.parse_args()
    
    # Set up languages to test
    if args.language == "both":
        languages = ["english", "arabic"]
    else:
        languages = [args.language]
    
    # Run verification
    results = run_verification(
        languages=languages, 
        categories=args.category,
        verbose=not args.quiet
    )
    
    # Save results
    output_file = save_verification_results(results, args.output)
    if not args.quiet:
        print(f"\nResults saved to: {output_file}")
    
    # Return success/failure status
    all_passed = all(lang_result["overall_success"] for lang_result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
