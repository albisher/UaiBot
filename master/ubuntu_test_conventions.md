# Ubuntu Test Run Summary & Development Conventions

## Test Run Summary
- All tests were run using `pytest` on Ubuntu.
- **Main Issue:**
  - `ModuleNotFoundError: No module named 'uaibot'` occurred in `tests/conftest.py`.
  - This prevented tests from running and is likely due to import path issues or missing the `uaibot` package/module in the current environment.
- **Other Observations:**
  - Some tests or plugins expect a certain project structure or installed package.
  - There are warnings about permissions for mouse/keyboard libraries (expected on Linux without root).

## Differences/Issues to Address
- **Import Path Consistency:**
  - Ensure all imports use relative or absolute paths that work both in development and CI environments.
  - Consider using `PYTHONPATH=.` or installing the package in editable mode (`pip install -e .`).
- **Test Isolation:**
  - Tests should not depend on global state or require special permissions (root) unless absolutely necessary.
- **Platform-Specific Handlers:**
  - Provide clear error messages and fallbacks for platform-specific features (audio, USB, mouse, etc.).
- **Test Discovery:**
  - Ensure all test files and dependencies are present and importable.

## Conventions for Stable Development
1. **Consistent Imports:**
   - Use absolute imports from the project root or ensure the package is installed in editable mode.
   - Avoid ambiguous or relative imports that break in different environments.
2. **Testable Code:**
   - Write code and tests that work on all supported platforms (Linux, macOS, Windows) or skip platform-specific tests gracefully.
   - Avoid requiring root for tests unless testing privileged features.
3. **Clear Error Handling:**
   - All platform-specific failures should be logged with actionable messages.
   - Tests should fail gracefully and provide hints for fixing environment issues.
4. **CI/CD Ready:**
   - Ensure tests can be run in CI/CD pipelines with minimal setup.
   - Document any environment variables or setup steps required.
5. **Documentation:**
   - Document all conventions, test requirements, and known issues in this file.
   - Update this file whenever a new convention or issue is discovered.

---

## AI Import Convention

- All prompts to the AI must use the template in `app/utils/template_prompt.txt` and request a JSON object with:
  - `"module"`: the full Python import path, all lowercase.
  - `"class"`: the class name to import.
  - Optionally, `"import_statement"`: the full import line.
- **No regex or string manipulation is allowed before the AI JSON is received.**
- After receiving the JSON, use the provided Python script (`app/utils/ai_json_tools.py`) to generate the correct import statement.
- All normalization and import generation is done after parsing the AI's JSON.

---

**Next Steps:**
- Fix the `ModuleNotFoundError` by ensuring the `app` module is importable (install as package or adjust `PYTHONPATH`).
- Review and update all test imports for consistency.
- Use this file as a living document for all future Ubuntu (and cross-platform) development conventions. 