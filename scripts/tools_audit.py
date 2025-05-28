import os
import importlib.util
import inspect
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = PROJECT_ROOT / 'src/labeeb/agent_tools'
TODO_DIR = PROJECT_ROOT / 'docs/development/todo'
TODO_FILE = TODO_DIR / "TODO.md"

results = []

def get_docstring(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    doc = None
    if lines and lines[0].strip().startswith('"""'):
        doc = lines[0].strip().strip('"')
    return doc

def import_tool_class(file_path):
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        return None, f"Import error: {e}"
    # Find the main class (ending with Tool)
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if name.lower().endswith('tool') and obj.__module__ == module.__name__:
            return obj, None
    return None, "No tool class found"

def test_tool_class(tool_cls):
    try:
        instance = tool_cls()
        # Try to call a test or execute method if available
        if hasattr(instance, 'test'):
            result = instance.test()
        elif hasattr(instance, 'execute'):
            # Try a dummy call
            try:
                result = instance.execute('test', {})
            except Exception as e:
                result = f"execute() error: {e}"
        else:
            result = "No testable method found"
        return result
    except Exception as e:
        return f"Instantiation error: {e}"

def audit_tools():
    TODO_DIR.mkdir(parents=True, exist_ok=True)
    for file in TOOLS_DIR.glob('*.py'):
        if file.name in ('__init__.py', 'tools_audit.py'):
            continue
        doc = get_docstring(file)
        doc_ok = bool(doc and len(doc) > 10 and 'tool' in doc.lower())
        tool_cls, import_err = import_tool_class(file)
        if tool_cls:
            test_result = test_tool_class(tool_cls)
        else:
            test_result = import_err or "No tool class found"
        results.append({
            'file': file.name,
            'doc_ok': doc_ok,
            'doc': doc,
            'tool_cls': tool_cls.__name__ if tool_cls else None,
            'test_result': test_result
        })
    # Write audit results to todo/tools_todo.md
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.write("# Tools Audit Results\n\n")
        for r in results:
            f.write(f"## {r['file']}\n")
            f.write(f"- Docstring OK: {r['doc_ok']}\n")
            f.write(f"- Tool class: {r['tool_cls']}\n")
            f.write(f"- Test result: {r['test_result']}\n\n")
            if not r['doc_ok']:
                f.write("  - [ ] Improve docstring\n")
            if not r['tool_cls']:
                f.write("  - [ ] Add main tool class\n")
            if r['test_result'] and 'error' in str(r['test_result']).lower():
                f.write(f"  - [ ] Fix: {r['test_result']}\n")
    print(f"Audit complete. Results written to {TODO_FILE}")

audit_tools() 