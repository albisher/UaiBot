#!/usr/bin/env python3
"""
Comprehensive multilingual test runner for UaiBot.
This script runs tests for all supported languages in UaiBot.
"""

import os
import sys
import argparse
import subprocess
import platform
from src.datetime import datetime
import json
from src.pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def get_platform_info():
    """Get information about the current platform."""
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    
    if system == "Linux":
        try:
            # Try to get Linux distribution info
            with open("/etc/os-release") as f:
                lines = f.readlines()
                distro_info = {}
                for line in lines:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        distro_info[key] = value.strip('"')
                distro_name = distro_info.get("NAME", "")
                distro_version = distro_info.get("VERSION_ID", "")
                return f"{system} {release} {distro_name} {distro_version}"
        except:
            pass
    
    return f"{system} {release} {version}"

def run_test_for_language(language):
    """Run tests for a specific language."""
    print(f"\n=== Running tests for {language.capitalize()} ===")
    
    # Prepare the command
    test_script = os.path.join(project_root, "tests", "run_multilingual_tests.py")
    cmd = [sys.executable, test_script, "--language", language]
    
    # Run the command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Tests for {language.capitalize()} completed successfully")
            print("\nOutput:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
            return True
        else:
            print(f"❌ Tests for {language.capitalize()} failed with return code {result.returncode}")
            print("\nOutput:")
            print("-" * 40)
            print(result.stdout)
            print("\nError:")
            print("-" * 40)
            print(result.stderr)
            print("-" * 40)
            return False
    except Exception as e:
        print(f"❌ Error running tests for {language.capitalize()}: {e}")
        return False

def verify_multilingual_fix():
    """Verify that the multilingual fix is working correctly."""
    verification_script = os.path.join(project_root, "fix", "verify_arabic_commands.py")
    try:
        result = subprocess.run([sys.executable, verification_script], capture_output=True, text=True)
        if result.returncode == 0:
            print("\n=== Multilingual Fix Verification ===")
            print("✅ Fix verification successful")
            print("\nOutput:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
            return True
        else:
            print("\n=== Multilingual Fix Verification ===")
            print("❌ Fix verification failed")
            print("\nOutput:")
            print("-" * 40)
            print(result.stdout)
            print("\nError:")
            print("-" * 40)
            print(result.stderr)
            print("-" * 40)
            return False
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")
        return False

def main():
    """Main function to run multilingual tests."""
    parser = argparse.ArgumentParser(description="Run multilingual tests for UaiBot")
    parser.add_argument("--languages", nargs="+", default=["english", "arabic"],
                      help="Languages to test")
    parser.add_argument("--verify-fix", action="store_true",
                      help="Verify that the multilingual fix is working")
    parser.add_argument("--output", default="json",
                      choices=["json", "text"], help="Output format")
    args = parser.parse_args()
    
    results = {}
    
    print("UaiBot Multilingual Test Runner")
    print("=" * 40)
    print(f"Platform: {get_platform_info()}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Languages: {', '.join(lang.capitalize() for lang in args.languages)}")
    print("=" * 40)
    
    # Verify fix if requested
    if args.verify_fix:
        fix_result = verify_multilingual_fix()
        results["fix_verification"] = fix_result
    
    # Run tests for each language
    for language in args.languages:
        results[language] = run_test_for_language(language)
    
    # Print summary
    print("\n=== Test Summary ===")
    if args.verify_fix:
        print(f"Fix verification: {'✅ Success' if results['fix_verification'] else '❌ Failed'}")
    
    for language in args.languages:
        print(f"{language.capitalize()}: {'✅ Success' if results[language] else '❌ Failed'}")
    
    # Output results in requested format
    if args.output == "json":
        output_file = os.path.join(project_root, "tests", "results", f"multilingual_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "platform": get_platform_info(),
                "languages": args.languages,
                "results": results
            }, f, indent=2)
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
