#!/usr/bin/env python3
"""
Runner script for multilingual tests of UaiBot.
Provides a convenient interface for running tests in both Arabic and English.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import utility functions
try:
    from uaibot.utils.output_formatter import format_header, format_box, format_status_line
    formatter_available = True
except ImportError:
    formatter_available = False

def format_with_emoji(text, status=None):
    """Format text with emoji based on status."""
    if not status:
        return text
        
    emoji_map = {
        'success': '✅ ',
        'error': '❌ ',
        'warning': '⚠️ ',
        'info': 'ℹ️ ',
        'running': '🔄 '
    }
    
    prefix = emoji_map.get(status.lower(), '')
    return f"{prefix}{text}"

def print_header(text):
    """Print a header with formatting if available."""
    if formatter_available:
        print(format_header(text))
    else:
        print("\n" + "=" * 60)
        print(text)
        print("=" * 60)

def print_status(text, status=None):
    """Print status message with formatting if available."""
    if formatter_available:
        print(format_status_line(text, status))
    else:
        print(format_with_emoji(text, status))

def run_multilingual_test(language="both", debug=False, quiet=False, ai_provider=None, output_dir=None):
    """
    Run multilingual tests using the test_multilingual.py script.
    
    Args:
        language: Language to test ("english", "arabic", or "both")
        debug: Whether to run in debug mode
        quiet: Whether to run in quiet mode
        ai_provider: AI provider to use (ollama or google)
        output_dir: Directory to save results and reports
        
    Returns:
        int: Return code from the test process
    """
    test_script = os.path.join(project_root, "tests", "test_multilingual.py")
    
    # Build command
    cmd = [sys.executable, test_script, "--language", language]
    
    if debug:
        cmd.append("--debug")
    if quiet:
        cmd.append("--quiet")
    if output_dir:
        cmd.extend(["--output", output_dir])
        
    # If AI provider is specified, set environment variable
    env = os.environ.copy()
    if ai_provider:
        env["DEFAULT_AI_PROVIDER"] = ai_provider
        
    # Print command info
    if not quiet:
        print_status(f"Running: {' '.join(cmd)}", "info")
        print_status(f"AI Provider: {ai_provider if ai_provider else 'Default'}", "info")
    
    # Run the command
    try:
        # If not quiet, we want to show output in real-time
        if not quiet:
            return subprocess.call(cmd, env=env)
        else:
            # In quiet mode, capture output and only show summary
            process = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return process.returncode
    except Exception as e:
        print_status(f"Error running tests: {e}", "error")
        return 1
        
def run_multiple_providers(languages, providers, debug=False):
    """
    Run tests with multiple AI providers for comparison.
    
    Args:
        languages: Languages to test ("english", "arabic", or "both")
        providers: List of AI providers to test with
        debug: Whether to run in debug mode
        
    Returns:
        dict: Results keyed by provider
    """
    results = {}
    
    for provider in providers:
        print_header(f"Running tests with {provider} AI provider")
        
        # Create output directory for this provider
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(project_root, "tests", "results", f"{provider}_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Run tests with this provider
        returncode = run_multilingual_test(
            language=languages,
            debug=debug,
            quiet=False,
            ai_provider=provider,
            output_dir=output_dir
        )
        
        results[provider] = {
            "returncode": returncode,
            "output_dir": output_dir,
            "success": returncode == 0
        }
        
        # Show separator between providers
        print("\n" + "-" * 60 + "\n")
        
    return results
        
def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run UaiBot multilingual tests")
    parser.add_argument("--language", "-l", choices=["english", "arabic", "both"], 
                      default="both", help="Language to test")
    parser.add_argument("--debug", "-d", action="store_true", help="Run in debug mode")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (minimal output)")
    parser.add_argument("--ai-provider", "-a", choices=["ollama", "google"], 
                      help="AI provider to use for tests")
    parser.add_argument("--compare-providers", "-c", action="store_true", 
                      help="Compare results between different AI providers")
    parser.add_argument("--output", "-o", help="Directory to save results")
    args = parser.parse_args()
    
    print_header("UaiBot Multilingual Test Runner")
    
    # Compare providers if requested
    if args.compare_providers:
        providers = ["ollama", "google"]
        print_status("Running comparison tests with multiple AI providers", "info")
        results = run_multiple_providers(args.language, providers, args.debug)
        
        # Print comparison summary
        print_header("Test Comparison Summary")
        for provider, result in results.items():
            status = "success" if result["success"] else "error"
            print_status(f"{provider}: {'Passed' if result['success'] else 'Failed'}", status)
            print(f"  Results saved to: {result['output_dir']}")
            
        return 0
    else:
        # Run with single provider
        return run_multilingual_test(
            language=args.language,
            debug=args.debug, 
            quiet=args.quiet,
            ai_provider=args.ai_provider,
            output_dir=args.output
        )

if __name__ == "__main__":
    sys.exit(main())
