import json
import os

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