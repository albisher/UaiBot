Automate Rule Enforcement

What it does:
- Checks all OS-specific code is in the correct platform_Labeeb subdirectory.
- Ensures all new tools/agents have associated tests and documentation.
- Validates that evaluation metrics and feedback hooks are present in new tools/agents.
- Lints for documentation links and AI-friendly comments.
- Prints a summary of violations and exits with a nonzero code if any are found.

How to use:
- Run manually in Cursor’s terminal:

python scripts/audit_project.py