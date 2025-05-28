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
from typing import List, Dict, Any

# --- Configuration (Ideally from a config file like config.json or pyproject.toml) ---
# For demonstration, keeping them here.
# Remember to create a venv for this project:
# python -m venv venv
# source venv/bin/activate  # On Windows: venv\Scripts\activate
# pip install toml # for pyproject.toml parsing by this script

# --- (START) User Configurable Variables ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG = {
    "project_name": "Labeeb",
    "old_project_names_regex": r'uai|Uai|UAIBOT|UaiBot',
    "src_dir_name": "src",
    "tests_dir_name": "tests",
    "docs_dir_name": "docs",
    "todo_dir_name": "todo",
    "cursor_rules_path": ".cursor/rules/project_rules.json",
    "readme_name": "README.md",
    "main_todo_filename": "labeeb_project_professional_todo.md",
    
    # Updated directory structure
    "required_dirs": {
        "ai": {
            "subdirs": ["agents", "models", "tools"],
            "naming": {
                "agents": r'^[A-Z][a-zA-Z]*Agent\.py$',
                "models": r'^[A-Z][a-zA-Z]*Model\.py$',
                "tools": r'^[A-Z][a-zA-Z]*Tool\.py$'
            }
        },
        "core": {
            "subdirs": ["capabilities", "workflows", "protocols"],
            "naming": {
                "capabilities": r'^[A-Z][a-zA-Z]*Capability\.py$',
                "workflows": r'^[A-Z][a-zA-Z]*Workflow\.py$',
                "protocols": r'^[A-Z][a-zA-Z]*Protocol\.py$'
            }
        },
        "platform_services": {
            "subdirs": ["common", "macos", "linux", "windows"],
            "naming": {
                "handlers": r'^[A-Z][a-zA-Z]*Handler\.py$'
            }
        },
        "services": {
            "naming": r'^[A-Z][a-zA-Z]*Service\.py$'
        },
        "tools": {
            "naming": r'^[A-Z][a-zA-Z]*Tool\.py$'
        },
        "ui": {
            "subdirs": ["cli", "gui", "web"]
        }
    },
    
    "platform_core_dir_segment": "labeeb/platform_services",
    "platform_dirs_keywords": ['ubuntu', 'windows', 'mac', 'linux'],
    "tool_dirs": ['labeeb/ai/tools', 'labeeb/ai/agents'],
    "agent_docs_subdir": "agents_tools",
    "test_file_prefix": "test_",
    "unit_test_subdir": "unit",
    
    # Compliance checks
    "compliance_keywords": {
        "A2A": r'A2A|Agent2Agent|agent_to_agent',
        "MCP": r'MCP|ModelContextProtocol|multi_channel_protocol',
        "SmolAgents": r'SmolAgent|smol_agent|minimal_agent'
    },
    
    # Internationalization
    "i18n_keywords_regex": r'i18n|internationalization|translate|gettext|_\(|\b_l\(|\btranslate_text\(',
    "rtl_keywords_regex": r'rtl|arabic|bidi|right-to-left|direction:\s*rtl',
    
    # Audit settings
    "generate_stubs": True,
    "test_generated_stubs": True,
    "check_project_syntax": True,
    "update_todo_file": True,
    "update_readme_file": False,
    "readme_audit_section_placeholder": ("", ""),
    
    # Exclusions
    "excluded_dirs": ['.git', '__pycache__', '.venv', 'node_modules', '.vscode', '.idea', 'build', 'dist', '*.egg-info', '.cache', '.pytest_cache', '.cursor'],
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

# Add a list of doc folders to skip
SKIP_DOC_FOLDERS = [
    "docs/secret/",
    "docs/architecture/",
    "docs/rules/",
    "docs/research/",
    # Add more as needed
]

# --- Helper Functions ---
def ensure_dir_exists(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def add_violation(category: str, message: str, file_path: Path = None, line_number: int = None, suggestion: str = None):
    violation = {"category": category, "message": message}
    if file_path:
        try:
            violation["file"] = str(file_path.relative_to(PROJECT_ROOT))
        except ValueError:
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
        if any(excluded_dir in str(item.relative_to(PROJECT_ROOT)) for excluded_dir in excluded_dirs):
            continue
        if item.is_file() and item.suffix.lower() in extensions:
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
    ensure_dir_exists(PLATFORM_ROOT_FULL)
    platform_keywords = CONFIG["platform_dirs_keywords"]
    for py_file in get_all_project_files(SRC_DIR, CONFIG["python_file_extensions"]):
        try:
            is_platform_specific_by_name = any(p_keyword in py_file.name.lower() for p_keyword in platform_keywords)
            is_within_platform_root = py_file.is_relative_to(PLATFORM_ROOT_FULL) if PLATFORM_ROOT_FULL.exists() else False
            if is_platform_specific_by_name and not is_within_platform_root:
                add_violation(
                    "PLATFORM_ISOLATION",
                    f"Platform-specific named file '{py_file.name}' found outside designated platform directory '{PLATFORM_ROOT_FULL.relative_to(PROJECT_ROOT)}'.",
                    py_file,
                    suggestion=f"Move OS-specific file '{py_file.name}' into an appropriate subdirectory of '{PLATFORM_ROOT_FULL.relative_to(PROJECT_ROOT)}/'. If it's not OS-specific, rename it."
                )
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            platform_check_regex = r'sys\.platform|platform\.system\(\)|platform\.release\(\)|os\.name'
            if re.search(platform_check_regex, content):
                if not is_within_platform_root:
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
    agent_base_dirs = [SRC_DIR / Path(p_dir) for p_dir in CONFIG["tool_dirs"]]
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
                if any(sub_path in str(py_file.relative_to(SRC_DIR)).lower() for sub_path in ["ui", "view", "display", "gui", "report"]):
                    add_violation("I18N_SUPPORT", "No clear i18n/translation keywords found in a potential user-facing module.", py_file,
                        suggestion=f"Ensure '{py_file.name}' uses translation functions (e.g., gettext's `_()`) for all user-visible strings. Relevant keywords: {CONFIG['i18n_keywords_regex']}")
            if CONFIG["project_name"] == "Labeeb":
                if "rtl_keywords_regex" in CONFIG and CONFIG["rtl_keywords_regex"]:
                    if not re.search(CONFIG["rtl_keywords_regex"], content, re.IGNORECASE):
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
    # TODO: Implement this function
    pass

def convert_txt_to_md(file_path: Path) -> bool:
    """
    Convert a .txt file to .md format.
    Returns True if conversion was successful, False otherwise.
    """
    try:
        # Read the content of the .txt file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create the new .md file path
        md_file_path = file_path.with_suffix('.md')
        
        # Write the content to the new .md file
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Remove the original .txt file
        file_path.unlink()
        
        logger.info(f"Successfully converted {file_path} to {md_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error converting {file_path} to .md: {e}")
        return False

def manage_docs_and_todos():
    logger.info("5. Managing Documentation and TODOs...")
    
    # Check for old project name references
    logger.info("   Checking for old project name references...")
    old_names_regex = CONFIG["old_project_names_regex"]
    correct_name = CONFIG["project_name"]
    for text_file in get_all_project_files(PROJECT_ROOT, CONFIG["text_file_extensions"]):
        try:
            # Skip the audit log file, TODO file, the audit script itself, and doc folders
            if text_file == LOG_FILE or (TODO_FILE and text_file == TODO_FILE) or text_file.name == "audit_project.py":
                continue
            # Skip all configured doc folders
            rel_path = str(text_file.relative_to(PROJECT_ROOT))
            if any(rel_path.startswith(folder) for folder in SKIP_DOC_FOLDERS):
                continue
            with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if re.search(old_names_regex, content, re.IGNORECASE):
                add_violation(
                    "PROJECT_NAMING",
                    f"Found old project name reference (matching '{old_names_regex}') instead of '{correct_name}'.",
                    text_file,
                    suggestion=f"Replace old project names with '{correct_name}' in '{text_file.name}'."
                )
        except Exception as e:
            logger.error(f"Error processing file {text_file} for project name check: {e}")
    
    # Ensure docs directory exists
    ensure_dir_exists(DOCS_DIR)
    
    # Convert .txt files to .md files
    txt_files = get_all_project_files(PROJECT_ROOT, ('.txt',))
    for txt_file in txt_files:
        if txt_file.name != 'requirements.txt':  # Skip requirements.txt
            convert_txt_to_md(txt_file)
    
    # Ensure todo directory exists
    ensure_dir_exists(TODO_DIR)
    
    # Create or update main todo file
    if CONFIG["update_todo_file"]:
        try:
            with open(TODO_FILE, 'w', encoding='utf-8') as f:
                f.write(f"# {CONFIG['project_name']} Project TODO List\n\n")
                f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## Project Audit Findings\n\n")
                for violation in VIOLATIONS:
                    f.write(f"### {violation['category']}\n")
                    f.write(f"- {violation['message']}\n")
                    if 'file' in violation:
                        f.write(f"  - File: {violation['file']}\n")
                    if 'line' in violation:
                        f.write(f"  - Line: {violation['line']}\n")
                    if 'suggestion' in violation:
                        f.write(f"  - Suggestion: {violation['suggestion']}\n")
                    f.write("\n")
            logger.info(f"Updated TODO file at: {TODO_FILE}")
        except Exception as e:
            logger.error(f"Error updating TODO file: {e}")

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

# New function to check directory structure and naming conventions
def check_directory_structure_and_naming():
    logger.info("Checking directory structure and naming conventions...")
    labeeb_dir = SRC_DIR / "labeeb"
    
    if not labeeb_dir.exists():
        add_violation(
            "DIRECTORY_STRUCTURE",
            f"Main package directory 'labeeb' not found in {SRC_DIR}",
            suggestion="Create the 'labeeb' directory in src/"
        )
        return
    
    # Check required directories and their structure
    for dir_name, dir_config in CONFIG["required_dirs"].items():
        dir_path = labeeb_dir / dir_name
        if not dir_path.exists():
            add_violation(
                "DIRECTORY_STRUCTURE",
                f"Required directory '{dir_name}' not found in {labeeb_dir}",
                suggestion=f"Create the '{dir_name}' directory in {labeeb_dir}"
            )
            continue
            
        # Check subdirectories if specified
        if "subdirs" in dir_config:
            for subdir in dir_config["subdirs"]:
                subdir_path = dir_path / subdir
                if not subdir_path.exists():
                    add_violation(
                        "DIRECTORY_STRUCTURE",
                        f"Required subdirectory '{subdir}' not found in {dir_path}",
                        suggestion=f"Create the '{subdir}' directory in {dir_path}"
                    )
        
        # Check naming conventions if specified
        if "naming" in dir_config:
            for file_type, pattern in dir_config["naming"].items():
                for py_file in get_all_project_files(dir_path, CONFIG["python_file_extensions"]):
                    if not re.match(pattern, py_file.name):
                        add_violation(
                            "NAMING_CONVENTION",
                            f"File '{py_file.name}' does not follow the {file_type} naming convention",
                            py_file,
                            suggestion=f"Rename file to follow the pattern: {pattern}"
                        )

# --- Main Execution ---
def main():
    logger.info("Starting project audit...")
    load_project_specific_rules()
    
    # Run all audit functions
    check_platform_isolation_and_os_detection()
    check_project_wide_python_syntax()
    check_agent_compliance()
    check_multi_language_and_system_support()
    check_directory_structure_and_naming()  # Add new check
    check_tests_and_validation()
    manage_docs_and_todos()
    report_os_detection_isolation_status()
    check_missing_dependencies()
    
    # Report violations
    if VIOLATIONS:
        logger.warning(f"\nFound {len(VIOLATIONS)} violations:")
        for violation in VIOLATIONS:
            logger.warning(f"\nCategory: {violation['category']}")
            logger.warning(f"Message: {violation['message']}")
            if 'file' in violation:
                logger.warning(f"File: {violation['file']}")
            if 'line' in violation:
                logger.warning(f"Line: {violation['line']}")
            if 'suggestion' in violation:
                logger.warning(f"Suggestion: {violation['suggestion']}")
    else:
        logger.info("No violations found. Project structure is compliant.")
    
    return len(VIOLATIONS) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 