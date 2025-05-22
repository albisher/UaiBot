# UaiBot Agentic Refactor & Enhancement TODO

## 1. AI-Driven Command Interpretation & Planning
- [x] Refactor command interpretation pipeline to support multi-step, conditional, and parameterized tasks
- [x] Expand JSON output schema (task lists, conditionals, parameters, confidence)
- [x] Enhance multilingual understanding (English, Arabic, etc.)
- [x] Update prompt templates and engineering

## 2. Execution Engine / Controller
- [ ] Design and implement internal controller/orchestrator
- [ ] Support for multi-step plan execution and state management
- [ ] Robust error handling and recovery
- [ ] Integration with all UaiBot modules/tools

## 3. Output & User Experience
- [ ] Revalidate output formatting in all modules/integration tests (see todo/output_fixes.txt)
- [ ] Add color formatting for improved UX

## 4. Foundational Improvements
- [ ] Continue modularization and file/folder reordering
- [ ] Expand and update tests for new agentic features
- [ ] Update documentation for new architecture/components
- [ ] Consolidate and improve system information gathering

## References
- master/refactor_code_master.md
- master/prompt.txt
- ai_human_requests.txt
- app/utils/template_prompt.txt
- test_files/t250521/
- todo/output_fixes.txt

## Appendix: Proposed AI Plan JSON Schema

```
{
  "plan": [
    {
      "step": 1,
      "description": "Create a file named test.txt",
      "operation": "file.create",
      "parameters": {
        "filename": "test.txt",
        "content": "hello"
      },
      "confidence": 0.98,
      "condition": null,
      "on_success": [2],
      "on_failure": [],
      "explanation": "Creates a new file with the specified content."
    },
    {
      "step": 2,
      "description": "Read the file test.txt",
      "operation": "file.read",
      "parameters": {
        "filename": "test.txt"
      },
      "confidence": 0.95,
      "condition": null,
      "on_success": [],
      "on_failure": [],
      "explanation": "Reads the content of the file created in step 1."
    }
  ],
  "overall_confidence": 0.96,
  "alternatives": [],
  "language": "en"
}
```

- Each step includes: operation, parameters, confidence, conditionals, explanations, and branching.
- The plan supports multi-step, conditional, and parameterized tasks.
- The schema is extensible for future needs (loops, error handling, etc.). 