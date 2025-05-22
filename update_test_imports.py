import os
import re

TESTS_DIR = "tests"
APP_DIR = "app"

# Recursively find all .py files in app/ and build a map of module names
module_map = {}
for root, dirs, files in os.walk(APP_DIR):
    for file in files:
        if file.endswith(".py") and file != "__init__.py":
            rel_path = os.path.relpath(os.path.join(root, file), APP_DIR)
            module_name = rel_path.replace(os.sep, ".")[:-3]  # remove .py
            module_map[file[:-3].lower()] = module_name.lower()


def update_imports_in_file(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Remove any chained 'from ... import ...' on the same line
        if ", from " in line:
            # Split on ', from' and treat each as a separate import
            parts = line.split(", from ")
            # The first part is a normal import, the rest need 'from ' prepended
            new_lines.append(parts[0].strip() + "\n")
            for part in parts[1:]:
                new_lines.append("from " + part.strip() + "\n")
            continue
        # Handle multi-imports: from app.command_processor import X, Y
        m = re.match(r"from app\.command_processor import (.+)", line)
        if m:
            names = [name.strip() for name in m.group(1).split(",")]
            for name in names:
                key = name.lower()
                if key in module_map:
                    new_lines.append(f"from app.command_processor.{key} import {name}\n")
                else:
                    new_lines.append(f"from app.command_processor import {name}\n")
            continue
        # Handle single import: from app.command_processor import X
        m = re.match(r"from app\.command_processor import (\w+)", line)
        if m:
            name = m.group(1)
            key = name.lower()
            if key in module_map:
                new_lines.append(f"from app.command_processor.{key} import {name}\n")
            else:
                new_lines.append(line)
            continue
        # For all submodules in app, fix imports
        m = re.match(r"from app import (\w+)", line)
        if m:
            name = m.group(1)
            key = name.lower()
            if key in module_map:
                new_lines.append(f"from app.{module_map[key]} import {name}\n")
            else:
                new_lines.append(line)
            continue
        m = re.match(r"import app\.(\w+)(?!\.)", line)
        if m:
            name = m.group(1)
            key = name.lower()
            if key in module_map:
                new_lines.append(f"import app.{module_map[key]}\n")
            else:
                new_lines.append(line)
            continue
        new_lines.append(line)

    with open(filepath, "w") as f:
        f.writelines(new_lines)
    print(f"Updated imports in {filepath}")

def walk_and_update_tests():
    for root, dirs, files in os.walk(TESTS_DIR):
        for file in files:
            if file.endswith(".py"):
                update_imports_in_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_update_tests() 