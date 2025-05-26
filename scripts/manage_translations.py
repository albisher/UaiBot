#!/usr/bin/env python3
"""Script to manage translations for the Labeeb platform.

This script provides a command-line interface for:
- Adding new languages
- Updating translations
- Compiling translations
- Checking translation status
- Managing translation files
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

def add_language(language: str) -> None:
    """Add a new language.
    
    Args:
        language: Language code (e.g., 'en', 'es', 'fr')
    """
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    # Create language directory
    lang_dir = locales_dir / language
    lc_messages_dir = lang_dir / "LC_MESSAGES"
    lc_messages_dir.mkdir(parents=True, exist_ok=True)

    # Copy template file
    template_file = locales_dir / "labeeb.pot"
    if not template_file.exists():
        print("No template file found")
        return

    po_file = lc_messages_dir / "labeeb.po"
    try:
        subprocess.run(
            ["msginit", "--input", str(template_file), "--locale", language, "--output", str(po_file)],
            check=True
        )
        print(f"Successfully added language: {language}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add language {language}: {e}")
    except FileNotFoundError:
        print("msginit not found. Please install gettext tools.")

def update_translations() -> None:
    """Update all translation files."""
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    # Extract strings
    try:
        subprocess.run(["./scripts/extract_strings.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract strings: {e}")
        return

    # Update each language's .po file
    for lang_dir in locales_dir.iterdir():
        if not lang_dir.is_dir():
            continue

        lc_messages_dir = lang_dir / "LC_MESSAGES"
        if not lc_messages_dir.exists():
            continue

        po_file = lc_messages_dir / "labeeb.po"
        if not po_file.exists():
            continue

        print(f"Updating translations for {lang_dir.name}...")
        try:
            subprocess.run(
                ["msgmerge", "--update", str(po_file), "locales/labeeb.pot"],
                check=True
            )
            print(f"Successfully updated translations for {lang_dir.name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to update translations for {lang_dir.name}: {e}")
        except FileNotFoundError:
            print("msgmerge not found. Please install gettext tools.")

def compile_translations() -> None:
    """Compile all translation files."""
    try:
        subprocess.run(["./scripts/compile_translations.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to compile translations: {e}")

def check_translations() -> None:
    """Check translation status."""
    try:
        subprocess.run(["./scripts/check_translations.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to check translations: {e}")

def list_languages() -> None:
    """List all available languages."""
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    print("\nAvailable Languages:")
    print("-" * 20)
    for lang_dir in locales_dir.iterdir():
        if not lang_dir.is_dir():
            continue

        lc_messages_dir = lang_dir / "LC_MESSAGES"
        if not lc_messages_dir.exists():
            continue

        po_file = lc_messages_dir / "labeeb.po"
        if not po_file.exists():
            continue

        try:
            result = subprocess.run(
                ["msgfmt", "--statistics", str(po_file)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"{lang_dir.name}: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"{lang_dir.name}: Error getting statistics")
        except FileNotFoundError:
            print("msgfmt not found. Please install gettext tools.")

def remove_language(language: str) -> None:
    """Remove a language.
    
    Args:
        language: Language code to remove
    """
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    lang_dir = locales_dir / language
    if not lang_dir.exists():
        print(f"Language {language} not found")
        return

    try:
        import shutil
        shutil.rmtree(lang_dir)
        print(f"Successfully removed language: {language}")
    except Exception as e:
        print(f"Failed to remove language {language}: {e}")

def main() -> None:
    """Main function to manage translations."""
    parser = argparse.ArgumentParser(description="Manage translations for the Labeeb platform")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add language command
    add_parser = subparsers.add_parser("add", help="Add a new language")
    add_parser.add_argument("language", help="Language code (e.g., 'en', 'es', 'fr')")

    # Remove language command
    remove_parser = subparsers.add_parser("remove", help="Remove a language")
    remove_parser.add_argument("language", help="Language code to remove")

    # Update translations command
    subparsers.add_parser("update", help="Update all translation files")

    # Compile translations command
    subparsers.add_parser("compile", help="Compile all translation files")

    # Check translations command
    subparsers.add_parser("check", help="Check translation status")

    # List languages command
    subparsers.add_parser("list", help="List all available languages")

    args = parser.parse_args()

    if args.command == "add":
        add_language(args.language)
    elif args.command == "remove":
        remove_language(args.language)
    elif args.command == "update":
        update_translations()
    elif args.command == "compile":
        compile_translations()
    elif args.command == "check":
        check_translations()
    elif args.command == "list":
        list_languages()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 