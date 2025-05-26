import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / 'src' / 'app'
TESTS_DIR = PROJECT_ROOT / 'tests'
DOCS_DIR = PROJECT_ROOT / 'docs'
TODO_FILE = PROJECT_ROOT / 'todo' / 'labeeb_project_professional_todo.md'

PLATFORM_DIRS = ['ubuntu', 'windows', 'mac']
PLATFORM_ROOT = SRC_DIR / 'platform_core'

VIOLATIONS = []

# 1. Check OS-specific code is in correct platform directory
def check_platform_isolation():
    for dirpath, _, filenames in os.walk(SRC_DIR):
        for fname in filenames:
            if fname.endswith('.py'):
                fpath = Path(dirpath) / fname
                rel = fpath.relative_to(SRC_DIR)
                # If platform-specific keywords are found outside platform_core, flag
                if any(p in fname.lower() for p in PLATFORM_DIRS) and 'platform_core' not in rel.parts:
                    VIOLATIONS.append(f"Platform-specific file outside platform_core: {rel}")
                # Check for platform checks in code
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if re.search(r'sys\.platform|platform\.system|os\.name', content):
                        if 'platform_core' not in rel.parts:
                            VIOLATIONS.append(f"Platform check in non-platform dir: {rel}")

# 2. Ensure new features have associated tests and documentation
def check_tests_and_docs():
    # Look for new tools/agents in src/app/core/ai/agent_tools and agents
    tool_dirs = [SRC_DIR / 'core' / 'ai' / 'agent_tools', SRC_DIR / 'core' / 'ai' / 'agents']
    for tdir in tool_dirs:
        if not tdir.exists():
            continue
        for fname in os.listdir(tdir):
            if fname.endswith('.py') and not fname.startswith('__'):
                tool_name = fname[:-3]
                # Test file should exist
                test_file = TESTS_DIR / 'unit' / f'test_{tool_name}.py'
                if not test_file.exists():
                    VIOLATIONS.append(f"Missing test for tool/agent: {tool_name}")
                # Doc file should exist
                doc_file = DOCS_DIR / 'agents_tools' / f'{tool_name}.md'
                if not doc_file.exists():
                    VIOLATIONS.append(f"Missing doc for tool/agent: {tool_name}")

# 3. Validate evaluation metrics and feedback hooks
def check_evaluation_hooks():
    # Look for 'evaluate', 'feedback', or 'metric' in tools/agents
    tool_dirs = [SRC_DIR / 'core' / 'ai' / 'agent_tools', SRC_DIR / 'core' / 'ai' / 'agents']
    for tdir in tool_dirs:
        if not tdir.exists():
            continue
        for fname in os.listdir(tdir):
            if fname.endswith('.py') and not fname.startswith('__'):
                fpath = tdir / fname
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if not re.search(r'evaluat|feedback|metric', content, re.IGNORECASE):
                        VIOLATIONS.append(f"No evaluation/feedback logic in: {fpath.relative_to(PROJECT_ROOT)}")

# 4. Lint for documentation links and AI-friendly comments
def check_docs_and_comments():
    for dirpath, _, filenames in os.walk(SRC_DIR):
        for fname in filenames:
            if fname.endswith('.py'):
                fpath = Path(dirpath) / fname
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Look for docstring and at least one link to docs or example
                    if not re.search(r'"""|\'\'\'|#.*docs|#.*example', content, re.IGNORECASE):
                        VIOLATIONS.append(f"Missing docstring or doc link: {fpath.relative_to(PROJECT_ROOT)}")

# 5. Check A2A, MCP, and SmolAgents compliance
def check_agent_compliance():
    agent_dirs = [SRC_DIR / 'core' / 'ai' / 'agents']
    for adir in agent_dirs:
        if not adir.exists():
            continue
        for fname in os.listdir(adir):
            if fname.endswith('.py') and not fname.startswith('__'):
                fpath = adir / fname
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Check for A2A compliance
                    if not re.search(r'A2A|Agent2Agent|agent_to_agent', content, re.IGNORECASE):
                        VIOLATIONS.append(f"Missing A2A compliance in: {fpath.relative_to(PROJECT_ROOT)}")
                    # Check for MCP compliance
                    if not re.search(r'MCP|ModelContextProtocol|multi_channel', content, re.IGNORECASE):
                        VIOLATIONS.append(f"Missing MCP compliance in: {fpath.relative_to(PROJECT_ROOT)}")
                    # Check for SmolAgents compliance
                    if not re.search(r'SmolAgent|smol_agent|minimal_agent', content, re.IGNORECASE):
                        VIOLATIONS.append(f"Missing SmolAgents compliance in: {fpath.relative_to(PROJECT_ROOT)}")

# 6. Check multi-language support
def check_multi_language():
    for dirpath, _, filenames in os.walk(SRC_DIR):
        for fname in filenames:
            if fname.endswith('.py'):
                fpath = Path(dirpath) / fname
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Check for i18n support
                    if not re.search(r'i18n|translation|gettext|_\(', content):
                        VIOLATIONS.append(f"Missing multi-language support in: {fpath.relative_to(PROJECT_ROOT)}")

# 7. Check for old project name references
def check_project_name():
    for dirpath, _, filenames in os.walk(PROJECT_ROOT):
        for fname in filenames:
            if fname.endswith(('.py', '.md', '.txt', '.json')):
                fpath = Path(dirpath) / fname
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if re.search(r'UaiBot|uaibot|UaiAgent|uaiagent', content):
                        VIOLATIONS.append(f"Found old project name in: {fpath.relative_to(PROJECT_ROOT)}")

# 8. Print summary and exit
def main():
    check_platform_isolation()
    check_tests_and_docs()
    check_evaluation_hooks()
    check_docs_and_comments()
    check_agent_compliance()
    check_multi_language()
    check_project_name()
    
    if VIOLATIONS:
        print("\nPROJECT AUDIT FAILED. Violations found:")
        for v in VIOLATIONS:
            print(f"- {v}")
        sys.exit(1)
    else:
        print("\nProject audit passed. No violations found.")

if __name__ == "__main__":
    main() 