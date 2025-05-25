# CLI/GUI Import Troubleshooting Checklist

- [x] All core imports use absolute paths (e.g., 'from uaibot.core...')
- [x] No sys.path hacks in agentic core or tools
- [x] CLI/GUI launchers prepend 'src' to sys.path if not present
- [x] README updated with import/run instructions
- [x] Troubleshooting section added to README
- [ ] Add CI/pre-commit check for import path compliance
- [ ] Document any future import errors and fixes here

## Debugging Steps
1. Always run from project root: `cd /home/a/Documents/Projects/UaiBot`
2. Use: `PYTHONPATH=src python3 scripts/launch.py` or `launch_gui.py`
3. If import error persists, check for relative imports or sys.path hacks
4. Check this checklist and README for updates 