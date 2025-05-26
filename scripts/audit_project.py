import os
import re
import sys
import platform
import json
import logging
import ast # For syntax checking project files
import py_compile # For syntax checking project files
import subprocess # For running unittest on stubs
from pathlib import Path
from datetime import datetime

# --- Configuration (Ideally from a config file like config.json or pyproject.toml) ---
# For demonstration, keeping them here.
# Remember to create a venv for this project:
# python -m venv venv
# source venv/bin/activate  # On Windows: venv\Scripts\activate
# pip install toml # for pyproject.toml parsing by this script

# --- (START) User Configurable Variables ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent # Assuming this script is in a 'scripts' or 'tools' subdir
CONFIG = {
    "project_name": "Labeeb",
    "old_project_names_regex": r'UaiBot|uaibot|UaiAgent|uaiagent', # Case-insensitive by default in usage
    "src_dir_name": "src/app",
    "tests_dir_name": "tests",
    "docs_dir_name": "docs",
    "todo_dir_name": "todo",
    "cursor_rules_path": ".labeeb/.cursor/rules/project_rules.json", # Example path
    "readme_name": "README.md",
    "main_todo_filename": "labeeb_project_professional_todo.md",
    "platform_core_dir_segment": "platform_core", # Segment identifying the root of platform-specific code, relative to src_dir
    "platform_dirs_keywords": ['ubuntu', 'windows', 'mac', 'linux'], # Keywords to identify platform-specific files by name
    "agent_tool_dirs": ['core/ai/agent_tools', 'core/ai/agents'], # Relative to src_dir
    "agent_docs_subdir": "agents_tools", # Relative to docs_dir
    "test_file_prefix": "test_",
    "unit_test_subdir": "unit", # Relative to tests_dir
    "evaluation_keywords_regex": r'evaluat|feedback|metric',
    "doc_link_keywords_regex": r'#.*docs|#.*example|\[.*\]\(.*docs\/.*\)|see also:', # Check for # comments or markdown links
    "compliance_keywords": {
        "A2A": r'A2A|Agent2Agent|agent_to_agent',
        "MCP": r'MCP|ModelContextProtocol|multi_channel_protocol',
        "SmolAgents": r'SmolAgent|smol_agent|minimal_agent'
    },
    "i18n_keywords_regex": r'i18n|internationalization|translate|gettext|_\(|\b_l\(|\btranslate_text\(',
    "rtl_keywords_regex": r'rtl|arabic|bidi|right-to-left|direction:\s*rtl',
    "generate_stubs": True,
    "test_generated_stubs": True, # New: Whether to attempt to test generated test stubs
    "check_project_syntax": True, # New: Whether to perform syntax check on all project .py files
    "update_todo_file": True,
    "update_readme_file": False,
    "readme_audit_section_placeholder": ("", ""),
    "excluded_dirs": ['.git', '__pycache__', 'venv', 'node_modules', '.vscode', '.idea', 'build', 'dist', '*.egg-info'],
    "text_file_extensions": ('.py', '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css', '.js', '.ts', '.rst', '.toml'),
    "python_file_extensions": ('.py',)
}
# --- (END) User Configurable Variables ---

# --- Path Setup using Configuration ---
SRC_DIR = PROJECT_ROOT / CONFIG["src_dir_name"]
TESTS_DIR = PROJECT_ROOT / CONFIG["tests_dir_name"]
DOCS_DIR = PROJECT_ROOT / CONFIG["docs_dir_name"]
TODO_DIR = PROJECT_ROOT / CONFIG["todo_dir_name"]
TODO_FILE = TODO_DIR / CONFIG["main_todo_filename"]
# PLATFORM_ROOT_FULL is the absolute path to the directory that SHOULD contain all OS-specific code.
PLATFORM_ROOT_FULL = SRC_DIR / CONFIG["platform_core_dir_segment"]

# --- Logging Setup ---
LOG_FILE = PROJECT_ROOT / "labeeb_audit.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

VIOLATIONS = []
PROJECT_RULES = {}

# --- Helper Functions ---
def ensure_dir_exists(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def add_violation(category: str, message: str, file_path: Path = None, line_number: int = None, suggestion: str = None):
    violation = {"category": category, "message": message}
    if file_path:
        # Store relative path from project root for consistent reporting
        try:
            violation["file"] = str(file_path.relative_to(PROJECT_ROOT))
        except ValueError: # If file_path is not under PROJECT_ROOT for some reason
            violation["file"] = str(file_path)
    if line_number:
        violation["line"] = line_number
    if suggestion:
        violation["suggestion"] = suggestion
    VIOLATIONS.append(violation)
    logger.warning(f"Violation [{category}]: {message}" + (f" in {violation.get('file', '')}" if file_path else ""))

def get_all_project_files(root_dir: Path, extensions: tuple, excluded_dirs: list = None):
    if excluded_dirs is None:
        excluded_dirs = CONFIG["excluded_dirs"]
    all_files = []
    if not root_dir.exists():
        logger.warning(f"Directory {root_dir} does not exist. Skipping file search within it.")
        return all_files
        
    for item in root_dir.rglob('*'):
        # Check if any part of the path string contains an excluded directory name.
        # This is a simple check; more robust would be to check exact path segments.
        if any(excluded_dir in str(item.relative_to(PROJECT_ROOT)) for excluded_dir in excluded_dirs):
            continue
        if item.is_file() and item.suffix.lower() in extensions: # Ensure extension check is case-insensitive
            all_files.append(item)
    return all_files

# --- Audit Functions ---

# 0. Load Project Specific Rules
def load_project_specific_rules():
    global PROJECT_RULES
    rules_file_path = PROJECT_ROOT / CONFIG["cursor_rules_path"]
    if rules_file_path.exists():
        try:
            with open(rules_file_path, 'r', encoding='utf-8') as f:
                PROJECT_RULES = json.load(f)
            logger.info(f"Successfully loaded project rules from: {rules_file_path}")
        except Exception as e:
            logger.error(f"Error loading or parsing project rules file {rules_file_path}: {e}")
            PROJECT_RULES = {}
    else:
        logger.info(f"Project rules file not found at: {rules_file_path}. Proceeding with default checks.")

# 1. Audit Script Output / Check OS-specific code is in correct platform directory
def check_platform_isolation_and_os_detection():
    logger.info("1. Checking Platform Isolation and OS Detection...")
    current_os = platform.system().lower()
    logger.info(f"Audit script is running on: {current_os.capitalize()}")
    ensure_dir_exists(PLATFORM_ROOT_FULL) # Ensure the designated platform root exists

    platform_keywords = CONFIG["platform_dirs_keywords"]
    
    for py_file in get_all_project_files(SRC_DIR, CONFIG["python_file_extensions"]):
        try:
            # Check 1: Platform-specific keywords in filename outside designated platform root
            is_platform_specific_by_name = any(p_keyword in py_file.name.lower() for p_keyword in platform_keywords)
            is_within_platform_root = py_file.is_relative_to(PLATFORM_ROOT_FULL) if PLATFORM_ROOT_FULL.exists() else False

            if is_platform_specific_by_name and not is_within_platform_root:
                add_violation(
                    "PLATFORM_ISOLATION",
                    f"Platform-specific named file '{py_file.name}' found outside designated platform directory '{PLATFORM_ROOT_FULL.relative_to(PROJECT_ROOT)}'.",
                    py_file,
                    suggestion=f"Move OS-specific file '{py_file.name}' into an appropriate subdirectory of '{PLATFORM_ROOT_FULL.relative_to(PROJECT_ROOT)}/'. If it's not OS-specific, rename it."
                )

            # Check 2: Platform detection code (sys.platform, etc.) in any file
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            platform_check_regex = r'sys\.platform|platform\.system\(\)|platform\.release\(\)|os\.name'
            if re.search(platform_check_regex, content):
                if not is_within_platform_root:
                    # Allow platform detection in explicitly permitted files (e.g., main entry points, config)
                    allowed_files_rules_key = "allowed_platform_check_files"
                    allowed_non_platform_core_files = PROJECT_RULES.get(allowed_files_rules_key, [])
                    relative_file_path_str = str(py_file.relative_to(PROJECT_ROOT))

                    if relative_file_path_str not in allowed_non_platform_core_files:
                        add_violation(
                            "PLATFORM_ISOLATION",
                            f"Platform detection code (e.g., sys.platform) found in file not under '{PLATFORM_ROOT_FULL.relative_to(PROJECT_ROOT)}'.",
                            py_file,
                            suggestion=f"Abstract OS-dependent logic from '{py_file.name}' into modules within '{PLATFORM_ROOT_FULL.relative_to(PROJECT_ROOT)}'. If this file must check OS (e.g. main script), consider adding '{relative_file_path_str}' to '{allowed_files_rules_key}' in project rules."
                        )
        except Exception as e:
            logger.error(f"Error processing file {py_file} for platform isolation: {e}")

# 1b. Syntax Check for all Project Python Files (New)
def check_project_wide_python_syntax():
    if not CONFIG["check_project_syntax"]:
        logger.info("Skipping project-wide Python syntax check as per configuration.")
        return
        
    logger.info("1b. Performing Syntax Check on all Project Python files...")
    has_syntax_errors = False
    for py_file in get_all_project_files(PROJECT_ROOT, CONFIG["python_file_extensions"]): # Check ALL .py files in project
        try:
            with open(py_file, 'rb') as f: # ast.parse needs bytes if there's an encoding declaration
                source_code = f.read()
            ast.parse(source_code, filename=str(py_file))
            # More thorough check with py_compile, which also checks for some other import issues
            # py_compile.compile(str(py_file), doraise=True, quiet=1) # quiet=1 to suppress output on success
            logger.debug(f"Syntax OK: {py_file.relative_to(PROJECT_ROOT)}")
        except (SyntaxError, py_compile.PyCompileError) as e:
            line_num = e.lineno if hasattr(e, 'lineno') else 'N/A'
            offset = e.offset if hasattr(e, 'offset') else 'N/A'
            add_violation(
                "SYNTAX_ERROR",
                f"Syntax error in Python file: {e.msg}",
                py_file,
                line_number=line_num,
                suggestion=f"Fix syntax error near line {line_num}, offset {offset}. This will block execution."
            )
            has_syntax_errors = True
        except Exception as e: # Catch other errors like file not found if list changes during iteration
            logger.error(f"Could not perform syntax check for {py_file}: {e}")
            add_violation("SYNTAX_CHECK_FAILURE", f"Could not perform syntax check: {e}", py_file)
            has_syntax_errors = True
    if not has_syntax_errors:
        logger.info("Project-wide Python syntax check passed.")

# 2. A2A, MCP, SmolAgents Compliance
def check_agent_compliance():
    logger.info("2. Checking A2A, MCP, SmolAgents Compliance...")
    agent_base_dirs = [SRC_DIR / Path(p_dir) for p_dir in CONFIG["agent_tool_dirs"]]
    compliance_keywords = CONFIG["compliance_keywords"]

    for agent_dir_path in agent_base_dirs:
        if not agent_dir_path.exists():
            logger.warning(f"Agent directory not found: {agent_dir_path}. Skipping compliance check for this path.")
            continue
        for py_file in get_all_project_files(agent_dir_path, CONFIG["python_file_extensions"]):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                for compliance_type, regex_pattern in compliance_keywords.items():
                    if not re.search(regex_pattern, content, re.IGNORECASE):
                        add_violation(
                            "AGENT_COMPLIANCE",
                            f"Potential lack of {compliance_type} compliance.",
                            py_file,
                            suggestion=f"Review '{py_file.name}' for {compliance_type} patterns (e.g., method calls, class structures related to '{regex_pattern}'). Refer to {compliance_type} guidelines."
                        )
            except Exception as e:
                logger.error(f"Error processing file {py_file} for agent compliance: {e}")

# 3. Multi-Language & Multi-System Support
def check_multi_language_and_system_support():
    logger.info("3. Checking Multi-Language & Multi-System Support...")
    for py_file in get_all_project_files(SRC_DIR, CONFIG["python_file_extensions"]):
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f_py:
                content = f_py.read()
            if not re.search(CONFIG["i18n_keywords_regex"], content, re.IGNORECASE):
                 # Heuristic: be less strict for non-UI/core logic files unless specific rules exist
                if any(sub_path in str(py_file.relative_to(SRC_DIR)).lower() for sub_path in ["ui", "view", "display", "gui", "report"]): # More likely to have user strings
                     add_violation("I18N_SUPPORT", "No clear i18n/translation keywords found in a potential user-facing module.", py_file,
                                   suggestion=f"Ensure '{py_file.name}' uses translation functions (e.g., gettext's `_()`) for all user-visible strings. Relevant keywords: {CONFIG['i18n_keywords_regex']}")
            
            if CONFIG["project_name"] == "Labeeb":
                if "rtl_keywords_regex" in CONFIG and CONFIG["rtl_keywords_regex"]: # Check if regex is defined and not empty
                    if not re.search(CONFIG["rtl_keywords_regex"], content, re.IGNORECASE):
                        # This is still broad. Add only if file is likely UI related.
                        # For now, it remains a placeholder for more specific checks.
                        # add_violation("RTL_SUPPORT", f"No explicit RTL/Arabic handling keywords ({CONFIG['rtl_keywords_regex']}) found.", py_file,
                        #               suggestion=f"Ensure '{py_file.name}' correctly handles RTL text if it processes or displays Arabic user content.")
                        pass 

        except UnicodeDecodeError:
            add_violation("ENCODING", "File is not UTF-8 encoded.", py_file,
                          suggestion="Convert file to UTF-8 for multi-language support, especially Arabic.")
        except Exception as e:
            logger.error(f"Error processing file {py_file} for multi-language support: {e}")

    locale_dir = PROJECT_ROOT / "locales"
    if "gettext" in CONFIG["i18n_keywords_regex"] or "translate" in CONFIG["i18n_keywords_regex"]:
        if not locale_dir.exists():
            add_violation("I18N_SETUP", f"Expected i18n 'locales' directory not found at '{locale_dir.relative_to(PROJECT_ROOT)}'.",
                        suggestion=f"If using gettext-style i18n, create a '{locale_dir.name}' directory and i18n catalogs (e.g., .po files).")
        elif CONFIG["project_name"] == "Labeeb":
            arabic_locales_exist = any(d.name.lower().startswith('ar') for d in locale_dir.iterdir() if d.is_dir())
            if not arabic_locales_exist:
                add_violation("I18N_ARABIC", f"No Arabic (ar_*) locale subdirectories found in '{locale_dir.relative_to(PROJECT_ROOT)}'.",
                            suggestion=f"Ensure Arabic translation files (e.g., ar/LC_MESSAGES/{CONFIG['project_name'].lower()}.po) are present for {CONFIG['project_name']}.")

# 4. Testing and Validation
def check_tests_and_validation():
    logger.info("4. Checking Testing and Validation (Tests, Docs, Evaluation Hooks)...")
    agent_tool_base_dirs = [SRC_DIR / Path(p_dir) for p_dir in CONFIG["agent_tool_dirs"]]
    test_file_prefix = CONFIG["test_file_prefix"]
    unit_test_subdir_path = TESTS_DIR / Path(CONFIG["unit_test_subdir"])
    agent_docs_subdir_path = DOCS_DIR / Path(CONFIG["agent_docs_subdir"])

    ensure_dir_exists(unit_test_subdir_path)
    ensure_dir_exists(agent_docs_subdir_path)

    for tool_dir_path in agent_tool_base_dirs:
        if not tool_dir_path.exists():
            logger.warning(f"Tool/Agent directory not found: {tool_dir_path}. Skipping its test/doc check.")
            continue
        for item in tool_dir_path.iterdir():
            if item.is_file() and item.suffix == '.py' and not item.name.startswith('__'):
                module_name = item.stem
                expected_test_file_name = f"{test_file_prefix}{module_name}.py"
                test_file_path = unit_test_subdir_path / expected_test_file_name

                if not test_file_path.exists():
                    suggestion = f"Create a test file at '{test_file_path.relative_to(PROJECT_ROOT)}'."
                    if CONFIG["generate_stubs"]:
                        try:
                            ensure_dir_exists(test_file_path.parent)
                            # Create a more standard unittest stub
                            class_name = f"Test{module_name.replace('_', ' ').title().replace(' ', '')}"
                            stub_content = f"# Test for {item.name}\nimport unittest\n\n"
                            # Try to import the module being tested to catch early import errors
                            relative_module_path = item.relative_to(PROJECT_ROOT.parent) # Assuming PROJECT_ROOT is one level above src
                            # Construct import path, e.g. src.app.core.ai.agents.my_agent
                            module_import_path = str(item.relative_to(PROJECT_ROOT)).replace(os.sep, '.').replace('.py','')

                            stub_content += f"try:\n    from {module_import_path} import ... # TODO: Import specific classes/functions\n"
                            stub_content += f"except ImportError:\n    pass # Handle if module itself has issues or direct import isn't desired for test structure\n\n"
                            stub_content += f"class {class_name}(unittest.TestCase):\n"
                            stub_content += f"    def test_{module_name}_placeholder(self):\n"
                            stub_content += f"        \"\"\"Basic placeholder test for {module_name}.\"\"\"\n"
                            stub_content += f"        self.fail('Test not implemented for {module_name}')\n\n"
                            stub_content += f"if __name__ == '__main__':\n    unittest.main()\n"
                            
                            with open(test_file_path, 'w', encoding='utf-8') as tf:
                                tf.write(stub_content)
                            suggestion += f" Basic stub created. Please implement tests."
                            logger.info(f"Created stub test file: {test_file_path}")

                            if CONFIG["test_generated_stubs"]:
                                logger.info(f"Attempting to validate generated test stub: {test_file_path}")
                                try:
                                    # Try basic syntax check
                                    py_compile.compile(str(test_file_path), doraise=True, quiet=1)
                                    logger.info(f"Syntax OK for stub: {test_file_path.name}")
                                    # Try running the test file (will likely fail the placeholder test)
                                    # Ensure PYTHONPATH is set up if tests have relative imports from src
                                    env = os.environ.copy()
                                    env['PYTHONPATH'] = str(PROJECT_ROOT) + os.pathsep + env.get('PYTHONPATH', '')
                                    
                                    # Best to run specific test file to avoid discovering all tests
                                    process = subprocess.run(
                                        [sys.executable, "-m", "unittest", str(test_file_path)],
                                        capture_output=True, text=True, timeout=10, env=env
                                    )
                                    if process.returncode == 0 or "FAIL: test_" in process.stderr or "FAIL: test_" in process.stdout : # 0 if all pass (unlikely), or 1 if failures (expected)
                                        logger.info(f"Generated test stub {test_file_path.name} is runnable (may have failing placeholder tests). Output:\n{process.stderr or process.stdout}")
                                    else:
                                        logger.warning(f"Generated test stub {test_file_path.name} might have issues or ran unexpectedly. Return code: {process.returncode}\nStderr:\n{process.stderr}\nStdout:\n{process.stdout}")
                                        # Do not add as violation, as it's a stub. This is informative.
                                except py_compile.PyCompileError as e_compile:
                                    logger.warning(f"Syntax error in generated stub {test_file_path.name}: {e_compile}")
                                    suggestion += f" Warning: Generated stub has syntax error: {e_compile.msg}."
                                except subprocess.TimeoutExpired:
                                    logger.warning(f"Timeout validating generated test stub: {test_file_path.name}")
                                except Exception as e_val:
                                    logger.warning(f"Could not fully validate generated test stub {test_file_path.name}: {e_val}")
                        except Exception as e:
                            suggestion += f" Failed to create or validate stub: {e}."
                            logger.error(f"Failed to create/validate stub test file {test_file_path}: {e}")
                    add_violation("TESTING", f"Missing test file for tool/agent: {module_name}", item, suggestion=suggestion)

                # Doc file check (similar logic for stub generation)
                doc_file_name = f"{module_name}.md"
                doc_file_path = agent_docs_subdir_path / doc_file_name
                if not doc_file_path.exists():
                    suggestion = f"Create documentation at '{doc_file_path.relative_to(PROJECT_ROOT)}'."
                    if CONFIG["generate_stubs"]:
                        try:
                            ensure_dir_exists(doc_file_path.parent)
                            with open(doc_file_path, 'w', encoding='utf-8') as df:
                                df.write(f"# {module_name.replace('_', ' ').title()}\n\n## Overview\n\nProvide a brief overview of {module_name}.\n\n## Functionality\n\nDescribe its main functions and capabilities.\n\n## Usage Examples\n\n```python\n# TODO: Add usage example\n```\n\n## Configuration\n\nDetail any configuration options.\n")
                            suggestion += f" Basic stub created. Please fill in the details."
                            logger.info(f"Created stub documentation file: {doc_file_path}")
                        except Exception as e:
                            suggestion += f" Failed to create doc stub: {e}."
                            logger.error(f"Failed to create stub doc file {doc_file_path}: {e}")
                    add_violation("DOCUMENTATION", f"Missing documentation file for tool/agent: {module_name}", item, suggestion=suggestion)

    logger.info("   Checking for evaluation/feedback hooks in agents/tools...")
    for tool_dir_path in agent_tool_base_dirs: # Reuse already defined paths
        if not tool_dir_path.exists():
            continue
        for py_file in get_all_project_files(tool_dir_path, CONFIG["python_file_extensions"]):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if not re.search(CONFIG["evaluation_keywords_regex"], content, re.IGNORECASE):
                    add_violation(
                        "EVALUATION",
                        f"No apparent evaluation, feedback, or metric collection logic found.",
                        py_file,
                        suggestion=f"Ensure '{py_file.name}' includes mechanisms for evaluation or feedback (keywords: {CONFIG['evaluation_keywords_regex']})."
                    )
            except Exception as e:
                logger.error(f"Error processing file {py_file} for evaluation hooks: {e}")

    logger.info("   Checking for docstrings, documentation links, and AI-friendly comments...")
    for py_file in get_all_project_files(SRC_DIR, CONFIG["python_file_extensions"]):
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if not (content.strip().startswith('"""') or content.strip().startswith("'''")):
                add_violation("DOCSTRING", "Missing module-level docstring.", py_file,
                            suggestion=f"Add a module-level docstring to '{py_file.name}' explaining its purpose.")
            if not re.search(CONFIG["doc_link_keywords_regex"], content, re.IGNORECASE | re.MULTILINE):
                add_violation(
                    "DOC_LINKS",
                    "Missing references or links to detailed documentation/examples within the code.",
                    py_file,
                    suggestion=f"Add comments linking to relevant documentation (e.g., '# See: docs/feature.md' or 'see also: MyClass') or usage examples in '{py_file.name}'."
                )
        except Exception as e:
            logger.error(f"Error processing file {py_file} for docstrings/comments: {e}")

# 5. Documentation and TODOs Management
def manage_docs_and_todos():
    logger.info("5. Managing Documentation and TODOs...")
    logger.info("   Checking for old project name references...")
    old_names_regex = CONFIG["old_project_names_regex"]
    correct_name = CONFIG["project_name"]
    for text_file in get_all_project_files(PROJECT_ROOT, CONFIG["text_file_extensions"]):
        try:
            if text_file == LOG_FILE or (TODO_FILE and text_file == TODO_FILE):
                continue
            with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if re.search(old_names_regex, content, re.IGNORECASE):
                # Avoid self-flagging if the audit script itself contains old names (e.g. in comments or strings)
                if "labeeb_audit.py" in str(text_file) or "audit_script_name.py" in str(text_file) : # Make this configurable if script name changes
                    continue
                add_violation(
                    "PROJECT_NAMING",
                    f"Found old project name reference (matching '{old_names_regex}') instead of '{correct_name}'.",
                    text_file,
                    suggestion=f"Replace old project names with '{correct_name}' in '{text_file.name}'."
                )
        except Exception as e:
            logger.error(f"Error processing file {text_file} for project name check: {e}")

    if CONFIG["update_todo_file"] and VIOLATIONS:
        ensure_dir_exists(TODO_DIR)
        logger.info(f"   Updating TODO file: {TODO_FILE}")
        try:
            existing_todo_items = set()
            if TODO_FILE.exists():
                with open(TODO_FILE, 'r', encoding='utf-8') as f_todo_read:
                    for line in f_todo_read:
                        # Normalize a bit for checking existence
                        norm_line = re.sub(r'\(Line: \d+\)', '(Line: ...)', line.strip()) # Ignore specific line numbers for dupe check
                        if line.startswith("- [ ]") or line.startswith("* [ ]"):
                             existing_todo_items.add(norm_line)
            
            new_todo_entries_count = 0
            with open(TODO_FILE, 'a+', encoding='utf-8') as f_todo:
                f_todo.seek(0, 2)
                if f_todo.tell() == 0:
                    f_todo.write(f"# {CONFIG['project_name']} Project TODOs\n\n")
                    f_todo.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                else:
                    f_todo.write(f"\n\n---\n*Audit run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

                current_run_added_items = set() # To avoid duplicates from the same run if violations are similar
                for v in VIOLATIONS:
                    todo_item_md = f"- [ ] **{v['category']}**: {v['message']}"
                    file_info = ""
                    if 'file' in v:
                        file_info += f" (File: `{v['file']}`"
                        if 'line' in v:
                            file_info += f", Line: {v['line']}"
                        file_info += ")"
                    todo_item_md += file_info
                    if 'suggestion' in v:
                        todo_item_md += f" - *Suggestion:* {v['suggestion']}"
                    
                    # Normalize for checking against existing_todo_items and current_run_added_items
                    norm_todo_check = f"- [ ] **{v['category']}**: {v['message']}"
                    if 'file' in v: # Only add file for dupe check, not line number
                         norm_todo_check += f" (File: `{v['file']}`)"
                    
                    # A more robust check: if a similar message for the same file and category exists, skip.
                    is_new_item = True
                    if norm_todo_check in current_run_added_items:
                        is_new_item = False
                    else:
                        for existing_item_line in existing_todo_items:
                            if norm_todo_check in existing_item_line:
                                is_new_item = False
                                break
                    
                    if is_new_item:
                        f_todo.write(f"{todo_item_md}\n")
                        current_run_added_items.add(norm_todo_check)
                        new_todo_entries_count +=1
            
            if new_todo_entries_count > 0:
                 logger.info(f"Added {new_todo_entries_count} new items to {TODO_FILE.relative_to(PROJECT_ROOT)}")
            else:
                 logger.info(f"No new distinct items to add to {TODO_FILE.relative_to(PROJECT_ROOT)} based on current violations.")
        except Exception as e:
            logger.error(f"Failed to update TODO file {TODO_FILE}: {e}")

    if CONFIG["update_readme_file"] and VIOLATIONS and CONFIG["readme_name"]:
        readme_path = PROJECT_ROOT / CONFIG["readme_name"]
        start_placeholder, end_placeholder = CONFIG["readme_audit_section_placeholder"]
        if readme_path.exists():
            logger.info(f"   Attempting to update README.md: {readme_path.relative_to(PROJECT_ROOT)}")
            try:
                content = readme_path.read_text(encoding='utf-8')
                # Create a more detailed summary
                summary_lines = [f"## Audit Summary ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
                                 f"Total violations found: {len(VIOLATIONS)}"]
                
                violations_by_cat_summary = {}
                for v_sum in VIOLATIONS:
                    violations_by_cat_summary[v_sum['category']] = violations_by_cat_summary.get(v_sum['category'], 0) + 1
                if violations_by_cat_summary:
                    summary_lines.append("Violations by category:")
                    for cat, count in sorted(violations_by_cat_summary.items()):
                        summary_lines.append(f"* {cat}: {count}")
                summary_lines.append(f"\nSee [{LOG_FILE.name}]({LOG_FILE.name}) for full details.") # Link to log
                if TODO_FILE.exists() and CONFIG["update_todo_file"]:
                     summary_lines.append(f"A list of actionable items may have been updated in [{TODO_FILE.name}]({TODO_FILE.relative_to(PROJECT_ROOT)}).")

                summary = "\n".join(summary_lines)
                
                start_index = content.find(start_placeholder)
                end_index = content.find(end_placeholder)

                if start_index != -1 and end_index != -1 and start_index < end_index:
                    new_content = (
                        content[:start_index + len(start_placeholder)] +
                        "\n\n" + summary + "\n\n" + # Add newlines for spacing
                        content[end_index:]
                    )
                    readme_path.write_text(new_content, encoding='utf-8')
                    logger.info(f"README.md audit summary section updated.")
                else:
                    logger.warning(f"README.md audit placeholders ('{start_placeholder}', '{end_placeholder}') not found. Cannot update summary.")
            except Exception as e:
                logger.error(f"Failed to update README.md: {e}")
        else:
            logger.warning(f"README.md not found at {readme_path}. Cannot update summary.")
            
    check_missing_dependencies()

# 6. OS Detection and Isolation Report
def report_os_detection_isolation_status():
    logger.info("6. OS Detection and Isolation Report:")
    logger.info(f"   OS detection for this script run: {platform.system().lower().capitalize()}")
    logger.info(f"   Platform-specific code is expected in subdirectories of: '{PLATFORM_ROOT_FULL.relative_to(PROJECT_ROOT)}'")
    logger.info(f"   Checks for platform-specific file naming and OS-check calls outside designated areas were performed.")

def check_missing_dependencies():
    logger.info("   Checking for potentially missing dependencies (this is a heuristic)...")
    try:
        importlib_metadata_available = True
        from importlib.metadata import packages_distributions, distribution # For checking if a module is part of a distribution
    except ImportError:
        importlib_metadata_available = False
        logger.warning("`importlib.metadata` not fully available (requires Python 3.8+ or `importlib_metadata` backport). Dependency check will be less accurate.")

    standard_libs = set(sys.builtin_module_names)
    if sys.version_info >= (3,10): # sys.stdlib_module_names available from 3.10
         standard_libs.update(sys.stdlib_module_names)
    else: # Fallback for older versions
        standard_libs.update(['os', 'sys', 're', 'json', 'datetime', 'pathlib', 'collections', 'math', 'logging', 'itertools', 'functools', 'subprocess', 'threading', 'multiprocessing', 'argparse', 'unittest', 'io', 'time', 'abc', 'csv', 'configparser', 'urllib', 'http', 'xml', 'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'hashlib', 'ssl', 'socket', 'select', 'asyncio', 'concurrent', 'ctypes', 'struct', 'pickle', 'copy', 'weakref', 'enum', 'typing', 'decimal', 'fractions', 'random', 'statistics', 'graphlib', 'zoneinfo']) # Expanded common stdlibs

    project_modules = set()
    # Consider all .py files under src_dir as potential project modules' top level
    src_python_files = get_all_project_files(SRC_DIR, CONFIG["python_file_extensions"])
    for py_file in src_python_files:
        if py_file.name == "__init__.py":
            project_modules.add(py_file.parent.name) # Add package name
        else:
            project_modules.add(py_file.stem) # Add module name

    imported_modules = set()
    import_pattern = re.compile(r"^\s*(?:import|from)\s+([a-zA-Z0-9_.]+)")
    for py_file in src_python_files: # Only scan src files for imports initially
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = import_pattern.match(line)
                    if match:
                        top_level_module = match.group(1).split('.')[0]
                        if top_level_module: # Ensure not empty
                            imported_modules.add(top_level_module)
        except Exception as e:
            logger.error(f"Error parsing imports from {py_file}: {e}")
            
    known_dependencies = set()
    req_files_config = PROJECT_RULES.get("dependency_files", ["requirements.txt", "requirements-dev.txt", "requirements_dev.txt"])
    req_files = [PROJECT_ROOT / rf for rf in req_files_config]

    for req_file_path in req_files:
        if req_file_path.exists():
            try:
                with open(req_file_path, 'r', encoding='utf-8') as rf:
                    for line in rf:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('-'): # Ignore comments and options like -r, -e
                            dep_name = re.split(r'[==<>;#\s\[]', line)[0]
                            if dep_name: known_dependencies.add(dep_name.lower().replace('-', '_'))
            except Exception as e: logger.warning(f"Could not parse {req_file_path}: {e}")
    
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import toml # Requires `pip install toml` for this script's venv
            data = toml.load(pyproject_path)
            # Poetry
            poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
            for dep in poetry_deps:
                if dep.lower() != 'python': known_dependencies.add(dep.lower().replace('-', '_'))
            poetry_dev_deps = data.get('tool', {}).get('poetry', {}).get('group', {}).get('dev',{}).get('dependencies', {})
            for dep in poetry_dev_deps:
                known_dependencies.add(dep.lower().replace('-', '_'))
            
            # PDM or Flit (simplified check for [project.dependencies] and optional-dependencies)
            project_deps = data.get('project', {}).get('dependencies', [])
            for dep_str in project_deps:
                dep_name = re.split(r'[==<>;#\s\[]', dep_str)[0]
                if dep_name: known_dependencies.add(dep_name.lower().replace('-', '_'))
            optional_deps = data.get('project', {}).get('optional-dependencies', {})
            for group in optional_deps.values():
                for dep_str in group:
                    dep_name = re.split(r'[==<>;#\s\[]', dep_str)[0]
                    if dep_name: known_dependencies.add(dep_name.lower().replace('-', '_'))
        except ImportError: logger.warning("`toml` library not installed. Cannot parse pyproject.toml. Run 'pip install toml'.")
        except Exception as e: logger.warning(f"Could not parse {pyproject_path}: {e}")

    potential_missing = []
    for mod_name in imported_modules:
        normalized_mod_name = mod_name.lower().replace('-', '_')
        if mod_name not in standard_libs and \
           normalized_mod_name not in standard_libs and \
           mod_name not in project_modules and \
           normalized_mod_name not in project_modules and \
           normalized_mod_name not in known_dependencies:
            
            # Try to see if module is provided by a known distribution using importlib.metadata
            is_part_of_known_dist = False
            if importlib_metadata_available:
                try:
                    # Find what distribution provides this module
                    dists = packages_distributions().get(mod_name)
                    if dists:
                        for dist_name in dists: # A module can be in multiple distributions (though rare for top-level)
                            if dist_name.lower().replace('-', '_') in known_dependencies:
                                is_part_of_known_dist = True
                                break
                except Exception as e_meta:
                     logger.debug(f"importlib.metadata check failed for {mod_name}: {e_meta}")


            if not is_part_of_known_dist:
                potential_missing.append(mod_name)

    if potential_missing:
        for missing_mod in sorted(list(set(potential_missing))):
            add_violation(
                "DEPENDENCY_MISSING",
                f"Potentially undeclared third-party dependency: '{missing_mod}'.",
                suggestion=f"If '{missing_mod}' is external, add it to your project's dependency file(s) (e.g., requirements.txt, pyproject.toml) and relevant docs. If it's a project module, ensure its path/naming is correct."
            )

# --- Main Execution ---
def main():
    logger.info(f"--- Starting {CONFIG['project_name']} Project Audit ---")
    logger.info(f"Project Root: {PROJECT_ROOT}")
    logger.info(f"Source Directory: {SRC_DIR}")
    logger.info(f"Python Executable: {sys.executable}")
    venv_path = os.getenv('VIRTUAL_ENV')
    if venv_path:
        logger.info(f"Running in Venv: {venv_path}")
    else:
        logger.warning("Not running in a detected virtual environment. This is highly discouraged.")
    
    load_project_specific_rules()

    check_platform_isolation_and_os_detection() 
    if CONFIG["check_project_syntax"]: # Check project syntax early
        check_project_wide_python_syntax()

    check_agent_compliance()
    check_multi_language_and_system_support()
    check_tests_and_validation() # This includes stub generation and validation
    manage_docs_and_todos()    # This includes dependency checks and project name check
    report_os_detection_isolation_status()

    logger.info("--- Audit Complete ---")

    if VIOLATIONS:
        logger.warning(f"\n--- {CONFIG['project_name']} PROJECT AUDIT FINDINGS ({len(VIOLATIONS)} total) ---")
        violations_by_category = {}
        for v in VIOLATIONS:
            violations_by_category.setdefault(v["category"], []).append(v)

        for category, v_list in sorted(violations_by_category.items()):
            logger.warning(f"\nCategory: {category} ({len(v_list)} issues)")
            for i, v_item in enumerate(v_list):
                msg = f"  {i+1}. {v_item['message']}"
                if 'file' in v_item:
                    msg += f" (File: {v_item['file']}"
                    if 'line' in v_item: msg += f", Line: {v_item['line']}"
                    msg += ")"
                if 'suggestion' in v_item: msg += f"\n     Suggestion: {v_item['suggestion']}"
                logger.warning(msg)
        
        print(f"\nAUDIT SUMMARY: {len(VIOLATIONS)} violation(s) found. Check '{LOG_FILE.name}' and (if updated) '{TODO_FILE.name}' for details.")
        sys.exit(1)
    else:
        logger.info(f"\n--- {CONFIG['project_name']} Project Audit Passed. No violations found. ---")
        print(f"\nAUDIT SUMMARY: Project audit passed. No violations found. Log available at '{LOG_FILE.name}'.")
        sys.exit(0)

if __name__ == "__main__":
    main() 