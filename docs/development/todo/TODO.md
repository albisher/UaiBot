# TODO

- [x] Implement robust, multi-language, multi-tool plan logic in agent
- [x] Ensure all tool names match the canonical registry
- [x] Test all tool actions via main.py --fast with English and Arabic instructions
- [x] Save all test artifacts in tests/files_and_folders_tests/
- [x] Check communication path for each task to confirm correct tool usage
- [x] Enforce project naming: Labeeb (not uaibot, etc.)
- [x] Document all changes in README and docs
- [x] Do not pass anything to the internet unless explicitly requested
- [x] Isolate all OS-specific changes
- [x] Update docs and README as features are completed
- [ ] Continue creative, human-like tool testing in both English and Arabic
- [ ] Verify all documentation and audit trails
- [ ] Address any issues, warnings, or bugs immediately






## Architecture Audit Results
Last audit: 2025-05-28 21:37:34
Status: ✅ Passed
Violations: 0
## Overview
This workflow tests Labeeb's ability to orchestrate multiple tools (browser automation, screenshot, vision, mouse/keyboard, file/folder, doc creation) in a complex, real-world scenario. All steps must be performed locally, with no data sent to the internet unless explicitly requested.

---

## Technology Choice
- **PyAutoGUI** is the official and default technology for all screenshots, mouse, and keyboard automation in this workflow. This ensures cross-platform compatibility (Linux, macOS, Windows).

---

## Workflow Steps

0. **Browser Fallback Logic**
   - If default browser fails to open via automation:
     - Take a screenshot of the desktop/applications menu using PyAutoGUI.
     - Use vision tool to locate the browser icon (e.g., Brave, Firefox, Chrome) in the apps menu or on the desktop.
     - If vision/screenshot is not effective:
       - Use a command-line approach:
         - Open the applications folder (e.g., `/usr/share/applications` or equivalent).
         - List available apps.
         - Find and run the browser (e.g., `brave-browser`, `firefox`, `chromium-browser`) via command line.
     - If the browser is already open, use PyAutoGUI to click the new tab button.
     - Once the browser is open and ready, proceed with the planned workflow.

1. **Open Default Browser**
   - Use browser automation tool to open the default web browser.
   - Confirm browser window is active.

2. **Take Initial Screenshot**
   - Use PyAutoGUI to capture the current screen.
   - Save screenshot to `labeeb_tool_tests/صور_الشاشة/` with timestamped filename.

3. **Verify Browser Location and Main Bar**
   - Use vision tool to analyze screenshot and locate the browser window and main bar/search area.
   - Log coordinates/region for later mouse automation.

4. **Mouse and Keyboard Automation: Search**
   - Use PyAutoGUI to move mouse to main bar/search area and click.
   - Use PyAutoGUI to type: `what is the weather in Kuwait now` (or Arabic equivalent).
   - Use PyAutoGUI to press Enter.

5. **Take Post-Search Screenshot**
   - Use PyAutoGUI to capture another screenshot after search results load.

6. **Analyze Search Results**
   - Use vision tool to describe/analyze the screenshot.
   - Verify that weather information is present on the screen.

7. **Navigate to Information/Link**
   - Use vision tool to identify a relevant link or information area.
   - Use PyAutoGUI to move mouse to that region and click.
   - Optionally, repeat screenshot and analysis to confirm navigation.

8. **Find and Crop Relevant Image**
   - Use vision tool to find a good image about the request (e.g., weather icon, map, etc.).
   - Use PyAutoGUI and image processing to crop the exact image area from the screenshot.

9. **Create Documentation File**
   - Use file/folder tool to create a doc file in the `testing` folder.
   - Insert the cropped image and relevant information/description into the doc file.

10. **Final Checks**
    - Ensure all steps are logged.
    - Confirm all files (screenshots, doc) are saved in the correct locations.
    - No data is sent to the internet unless explicitly requested.

---

## Tools Involved
- Browser Automation Tool
- PyAutoGUI (screenshots, mouse, keyboard)
- Vision Tool (SmolVLM-256M, local-only)
- File/Folder Tool
- (Optional) Doc/Markdown Creation Tool

## Expected Checks
- Each tool is invoked and works as intended.
- PyAutoGUI is used for all image/screenshot, mouse, and keyboard automation.
- All file operations are local and compliant with privacy rules.
- Multi-language and multi-system support is maintained.
- All outputs are saved in the correct folders.

---

## TODOs
- [ ] Register and test VisionTool with a local image
- [ ] Integrate VisionTool with screenshot workflow
- [ ] Implement browser open and focus logic
- [ ] Implement browser fallback logic (vision + mouse open, or command line)
- [ ] Automate mouse/keyboard for search using PyAutoGUI
- [ ] Automate screenshot and vision analysis after search using PyAutoGUI
- [ ] Implement navigation to relevant link/information using PyAutoGUI
- [ ] Find and crop relevant image from screenshot
- [ ] Create and populate doc file in `testing` folder
- [ ] Log and verify all steps
- [ ] Ensure no internet data transfer unless explicitly requested 
