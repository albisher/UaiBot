#!/usr/bin/env python3
"""
Script to process patch1.txt and generate a readable report.
"""
import os
import sys
import argparse
from datetime import datetime
from app.core.ai_handler import AIHandler
from tests.test_patch_processor import PatchProcessor, verify_file_organization

def ensure_directory_structure():
    """Ensure all required directories exist."""
    required_dirs = [
        'app',
        'tests',
        'scripts',
        'config',
        'docs',
        'reports'
    ]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main function to process patch file and generate report."""
    parser = argparse.ArgumentParser(description='Process patch file and generate report')
    parser.add_argument('--patch-file', default='master/patch1.txt',
                      help='Path to the patch file (default: master/patch1.txt)')
    parser.add_argument('--output-dir', default='reports',
                      help='Directory to save the report (default: reports)')
    parser.add_argument('--model-type', default='ollama',
                      choices=['ollama', 'google'],
                      help='Type of AI model to use (default: ollama)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Ensure directory structure exists
    ensure_directory_structure()
    
    # Verify file organization
    try:
        verify_file_organization(args.patch_file)
        verify_file_organization(args.output_dir)
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize AI handler
    ai_handler = AIHandler(
        model_type=args.model_type,
        debug=args.debug
    )
    
    # Initialize patch processor
    processor = PatchProcessor(ai_handler)
    
    # Process patch file
    print(f"Processing patch file: {args.patch_file}")
    try:
        results = processor.process_patch_file(args.patch_file)
    except ValueError as e:
        print(f"Error processing patch file: {str(e)}")
        sys.exit(1)
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(args.output_dir, f'patch_report_{timestamp}.txt')
    
    try:
        processor.generate_report(report_file)
    except ValueError as e:
        print(f"Error generating report: {str(e)}")
        sys.exit(1)
    
    print(f"\nReport generated: {report_file}")
    print(f"Processed {sum(len(cmds) for cmds in results.values())} commands across {len(results)} categories")

if __name__ == '__main__':
    main() 