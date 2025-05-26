#!/usr/bin/env python3
"""Script to extract translatable strings from the codebase.

This script:
- Scans Python files for translatable strings
- Extracts strings marked with _() and ngettext()
- Generates a template .pot file
- Updates existing .po files
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Set, Tuple

def find_python_files() -> List[Path]:
    """Find all Python files in the codebase.
    
    Returns:
        List[Path]: List of Python file paths
    """
    src_dir = Path("src")
    if not src_dir.exists():
        print("No src directory found")
        return []

    return list(src_dir.rglob("*.py"))

def extract_strings_from_file(file_path: Path) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    """Extract translatable strings from a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Tuple[Set[str], Set[Tuple[str, str]]]: Sets of simple strings and plural strings
    """
    simple_strings = set()
    plural_strings = set()

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return simple_strings, plural_strings

    # Find simple translations: _("string")
    simple_pattern = r'_\s*\(\s*["\'](.*?)["\']\s*\)'
    for match in re.finditer(simple_pattern, content):
        simple_strings.add(match.group(1))

    # Find plural translations: ngettext("singular", "plural", count)
    plural_pattern = r'ngettext\s*\(\s*["\'](.*?)["\']\s*,\s*["\'](.*?)["\']\s*,\s*\w+\s*\)'
    for match in re.finditer(plural_pattern, content):
        singular = match.group(1)
        plural = match.group(2)
        plural_strings.add((singular, plural))

    return simple_strings, plural_strings

def generate_pot_file(strings: Tuple[Set[str], Set[Tuple[str, str]]]) -> None:
    """Generate a template .pot file from extracted strings.
    
    Args:
        strings: Tuple of simple strings and plural strings
    """
    simple_strings, plural_strings = strings
    pot_file = Path("locales/labeeb.pot")

    # Create locales directory if it doesn't exist
    pot_file.parent.mkdir(parents=True, exist_ok=True)

    # Write header
    header = '''msgid ""
msgstr ""
"Project-Id-Version: Labeeb 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2024-03-14 12:00+0000\\n"
"PO-Revision-Date: 2024-03-14 12:00+0000\\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"\\n"
'''
    pot_file.write_text(header, encoding="utf-8")

    # Write simple strings
    with pot_file.open("a", encoding="utf-8") as f:
        for string in sorted(simple_strings):
            f.write(f'\nmsgid "{string}"\n')
            f.write('msgstr ""\n')

    # Write plural strings
    with pot_file.open("a", encoding="utf-8") as f:
        for singular, plural in sorted(plural_strings):
            f.write(f'\nmsgid "{singular}"\n')
            f.write(f'msgid_plural "{plural}"\n')
            f.write('msgstr[0] ""\n')
            f.write('msgstr[1] ""\n')

def update_po_files() -> None:
    """Update all .po files with new strings."""
    locales_dir = Path("locales")
    if not locales_dir.exists():
        print("No locales directory found")
        return

    pot_file = locales_dir / "labeeb.pot"
    if not pot_file.exists():
        print("No template file found")
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

        print(f"Updating translations for {lang_dir.name}...")
        try:
            subprocess.run(
                ["msgmerge", "--update", str(po_file), str(pot_file)],
                check=True
            )
            print(f"Successfully updated translations for {lang_dir.name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to update translations for {lang_dir.name}: {e}")
        except FileNotFoundError:
            print("msgmerge not found. Please install gettext tools.")

def main() -> None:
    """Main function to extract and process translatable strings."""
    print("Starting string extraction...")

    # Find Python files
    py_files = find_python_files()
    if not py_files:
        print("No Python files found")
        return

    # Extract strings
    all_simple_strings = set()
    all_plural_strings = set()

    for file_path in py_files:
        print(f"Processing {file_path}...")
        simple_strings, plural_strings = extract_strings_from_file(file_path)
        all_simple_strings.update(simple_strings)
        all_plural_strings.update(plural_strings)

    # Generate template file
    print("\nGenerating template file...")
    generate_pot_file((all_simple_strings, all_plural_strings))

    # Update translation files
    print("\nUpdating translation files...")
    update_po_files()

    print("\nString extraction completed!")
    print(f"Found {len(all_simple_strings)} simple strings and {len(all_plural_strings)} plural strings")

if __name__ == "__main__":
    main() 