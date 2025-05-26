import json
import os
import warnings

"""
AI JSON Tools for Labeeb

This module provides utilities for processing and handling JSON output from AI models,
particularly for generating import statements and building AI prompts. It includes
functions for parsing AI-generated JSON responses and constructing prompts using
templates.

Note: This module is deprecated. Use JSONTool from src/labeeb/core/tools/json_tools.py instead.

Key features:
- JSON output processing and validation
- Import statement generation from AI responses
- AI prompt template management
- Error handling for malformed JSON

See also: src/labeeb/core/tools/json_tools.py for the current implementation
"""

warnings.warn("ai_json_tools.py is deprecated. Use JSONTool from src/labeeb/core/tools/json_tools.py instead.")

def process_ai_json_output(ai_json_str):
    """
    Process the AI's JSON output and generate a valid import statement.
    """
    try:
        data = json.loads(ai_json_str) if isinstance(ai_json_str, str) else ai_json_str
        # If the AI returns a list of imports
        if isinstance(data, list):
            return [process_ai_json_output(item) for item in data]
        # Normalize module to lowercase
        module = data.get("module", "").lower()
        class_name = data.get("class", "")
        # Use provided import_statement if present and valid
        if "import_statement" in data and data["import_statement"]:
            return data["import_statement"].strip()
        # Otherwise, generate it
        if module and class_name:
            return f"from {module} import {class_name}"
        raise ValueError("Missing 'module' or 'class' in AI JSON output.")
    except Exception as e:
        print(f"Error processing AI JSON output: {e}")
        return None

def build_ai_prompt(user_input, prompt_template_path=None):
    """
    Build the AI prompt by inserting user input into the app's template prompt.
    The template is stored in app/utils/template_prompt.txt by default.
    """
    if prompt_template_path is None:
        prompt_template_path = os.path.join(os.path.dirname(__file__), "template_prompt.txt")
    with open(prompt_template_path, "r") as f:
        template = f.read()
    # Replace placeholder with user input
    prompt = template.replace("{user_input}", user_input)
    return prompt 