import os
import re

TESTS_DIR = "tests"

def update_imports_in_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # Replace app imports with uaibot imports
    content = content.replace("from app.", "from uaibot.")
    content = content.replace("import app.", "import uaibot.")
    
    # Fix src imports
    content = content.replace("from src.", "from uaibot.")
    content = content.replace("import src.", "import uaibot.")
    
    # Fix specific imports
    content = content.replace("from src.pathlib import Path", "from pathlib import Path")
    content = content.replace("from src.datetime import datetime", "from datetime import datetime")

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