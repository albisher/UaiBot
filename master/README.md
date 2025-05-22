# UaiBot Processing Stages and AI Prompt Template

## UaiBot Main Processing Stages

1. **Human Input**: The user provides input to UaiBot (text, voice, image, or video).
2. **AI Prompt Construction**: UaiBot passes the user input to an AI model. At this stage, the app constructs a prompt for the AI using a template.
3. **AI Analysis**: The AI analyzes the input and returns a structured, formatted JSON output describing the user's intent and required actions.
4. **Execution**: UaiBot assesses the AI's output and executes actions if required.
5. **Output to Human**: UaiBot returns the result or information to the user.

## About `app/utils/template_prompt.txt`

- This file contains the template used to construct the prompt for the AI model at **stage 2**.
- The template provides context, instructions, and a sample JSON output format for the AI.
- The template is loaded and used by the `build_ai_prompt` function in `app/utils/ai_json_tools.py`.
- To ensure consistent and clear communication with the AI, all user input should be passed through this template before being sent to the AI model.

## How to Use

- Use the function `build_ai_prompt(user_input)` from `app/utils/ai_json_tools.py` to generate the AI prompt.
- The resulting prompt should be sent to the AI model for analysis and response.

---

## Command-Line Usage & Automation

UaiBot now supports clear, automation-friendly CLI flags and modes:

- `-c`, `--command` : Run a single command and exit (non-interactive mode)
- `-f`, `--file`    : Run commands from a file and exit (non-interactive mode)
- `--fast`          : Fast mode (minimal prompts, skips username and handler prompts)
- `-d`, `--debug`   : Enable debug output

**Example:**
```sh
python3 app/main.py --command "list files in current directory" --fast
```

- In non-interactive or fast mode, UaiBot will not prompt for username or block on missing handlers.
- All prompts and interactive flows are only triggered in interactive mode.

---

**Note:**
If you update the template or the expected JSON output format, make sure all code that builds AI prompts uses this file via `build_ai_prompt` to ensure consistency across the app. 