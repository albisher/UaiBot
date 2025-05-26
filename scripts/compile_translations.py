#!/usr/bin/env python3
"""Script to compile translation files for the Labeeb platform.

This script:
- Compiles .po files to .mo files
- Validates translation files
- Updates translation files
- Generates translation statistics
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any

def compile_translations() -> None:
    """Compile all translation files in the locales directory."""
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    for lang_dir in locales_dir.iterdir():
        if not lang_dir.is_dir():
            continue

        lc_messages_dir = lang_dir / "LC_MESSAGES"
        if not lc_messages_dir.exists():
            continue

        po_file = lc_messages_dir / "labeeb.po"
        if not po_file.exists():
            continue

        print(f"Compiling translations for {lang_dir.name}...")
        try:
            subprocess.run(
                ["msgfmt", str(po_file), "-o", str(lc_messages_dir / "labeeb.mo")],
                check=True
            )
            print(f"Successfully compiled translations for {lang_dir.name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to compile translations for {lang_dir.name}: {e}")
        except FileNotFoundError:
            print("msgfmt not found. Please install gettext tools.")

def validate_translations() -> None:
    """Validate all translation files."""
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    for lang_dir in locales_dir.iterdir():
        if not lang_dir.is_dir():
            continue

        lc_messages_dir = lang_dir / "LC_MESSAGES"
        if not lc_messages_dir.exists():
            continue

        po_file = lc_messages_dir / "labeeb.po"
        if not po_file.exists():
            continue

        print(f"Validating translations for {lang_dir.name}...")
        try:
            subprocess.run(
                ["msgfmt", "--check", str(po_file)],
                check=True
            )
            print(f"Successfully validated translations for {lang_dir.name}")
        except subprocess.CalledProcessError as e:
            print(f"Validation failed for {lang_dir.name}: {e}")
        except FileNotFoundError:
            print("msgfmt not found. Please install gettext tools.")

def update_translations() -> None:
    """Update translation files from source."""
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    # Get list of all .py files
    py_files = list(Path("src").rglob("*.py"))
    if not py_files:
        print("No Python files found")
        return

    # Extract messages
    try:
        subprocess.run(
            ["xgettext", "-d", "labeeb", "-o", "locales/labeeb.pot"] + [str(f) for f in py_files],
            check=True
        )
        print("Successfully extracted messages")
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract messages: {e}")
        return
    except FileNotFoundError:
        print("xgettext not found. Please install gettext tools.")
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

def generate_stats() -> None:
    """Generate translation statistics."""
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    print("\nTranslation Statistics:")
    print("-" * 50)

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
            print(f"Failed to get statistics for {lang_dir.name}: {e}")
        except FileNotFoundError:
            print("msgfmt not found. Please install gettext tools.")

def main() -> None:
    """Main function to run all translation tasks."""
    print("Starting translation tasks...")
    
    print("\nValidating translations...")
    validate_translations()
    
    print("\nUpdating translations...")
    update_translations()
    
    print("\nCompiling translations...")
    compile_translations()
    
    print("\nGenerating statistics...")
    generate_stats()
    
    print("\nTranslation tasks completed!")

if __name__ == "__main__":
    main() 