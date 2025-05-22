# UaiBot Refactor & Corrections Master Plan (Reference for main.py)

## Reference: Robust, Automation-Friendly main.py

### CLI Flags & Modes
- `-c`, `--command` : Run a single command and exit (non-interactive mode)
- `-f`, `--file`    : Run commands from a file and exit (non-interactive mode)
- `--fast`          : Fast mode (minimal prompts, skips username and handler prompts)
- `-d`, `--debug`   : Enable debug output
- `--gui`, `-g`     : Start in GUI mode (not covered here)

### Mode Awareness
- The app distinguishes between `interactive`, `command`, and `file` modes.
- Mode is determined at startup and passed to all core components (UaiBot, PlatformManager, CommandProcessor, etc).
- In non-interactive or fast mode, all blocking prompts (e.g., username, handler setup) are skipped.

### Handler Initialization & Error Handling
- Audio, USB, and input handler initialization errors are logged as warnings, not errors.
- In non-interactive or fast mode, missing handlers do not block or prompt the user.
- Only escalate to error if a required handler is missing for a requested operation.

### Prompt & User Experience Logic
- Username prompt and similar interactive flows are only triggered in interactive mode.
- In non-interactive or fast mode, environment or default values are used for username and other settings.
- The app never hangs or blocks for input in automation/scripting scenarios.

### Example Usage
```sh
python3 app/main.py --command "list files in current directory" --fast
```
- This will process the command, skip all prompts, and exit cleanly.

### Maintenance & Extension
- When adding new features or prompts, always check the mode and fast_mode flags.
- All new interactive flows must be gated by `mode == 'interactive'`.
- All handler and platform initialization should degrade gracefully in automation mode.

---

**This file is the canonical reference for how main.py and related startup logic should behave.**
