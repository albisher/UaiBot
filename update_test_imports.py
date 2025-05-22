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
        content = f.read()

    # Replace uaibot imports with app imports
    content = content.replace("from uaibot.", "from app.")
    content = content.replace("import uaibot.", "import app.")

    with open(filepath, "w") as f:
        f.write(content)
    print(f"Updated imports in {filepath}")

def walk_and_update_tests():
    for root, dirs, files in os.walk(TESTS_DIR):
        for file in files:
            if file.endswith(".py"):
                update_imports_in_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_update_tests() 