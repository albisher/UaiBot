# UaiBot Agentic Refactor & Enhancement TODO

## 1. AI-Driven Command Interpretation & Planning
- [x] Refactor command interpretation pipeline to support multi-step, conditional, and parameterized tasks
- [x] Expand JSON output schema (task lists, conditionals, parameters, confidence)
- [x] Enhance multilingual understanding (English, Arabic, etc.)
- [x] Update prompt templates and engineering

## 2. Execution Engine / Controller
- [x] Design and implement internal controller/orchestrator
  - Implemented in `app/core/controller/execution_controller.py`
  - Supports multi-step plan execution with success/failure paths
  - Handles state management and persistence
  - Provides robust error handling and recovery
- [x] Support for multi-step plan execution and state management
  - State variables with $ prefix for persistence
  - Execution history tracking
  - Step completion and failure tracking
- [x] Robust error handling and recovery
  - Error state tracking
  - Recovery paths for failed steps
  - Detailed error reporting
- [x] Integration with all UaiBot modules/tools
  - File operations (create, read, delete)
  - Shell command execution
  - AI operations
  - Extensible operation type system

## 3. Output & User Experience
- [ ] Revalidate output formatting in all modules/integration tests (see todo/output_fixes.txt)
- [ ] Add color formatting for improved UX

## 4. Foundational Improvements
- [ ] Continue modularization and file/folder reordering
- [ ] Expand and update tests for new agentic features
- [ ] Update documentation for new architecture/components
- [ ] Consolidate and improve system information gathering

## Implementation Details

### Execution Controller Features
1. Multi-step Plan Execution
   - Sequential and conditional execution
   - Success and failure paths
   - State variable management
   - Operation type handling

2. State Management
   - Persistent state storage (execution_state.json)
   - State variable tracking
   - Execution history
   - Step completion tracking

3. Error Handling
   - Graceful error recovery
   - Error state tracking
   - Detailed error reporting
   - Operation-specific error handling

4. Operation Types
   - file.*: File operations (create, read, delete)
   - shell.*: Shell command execution
   - ai.*: AI model operations

### Testing
- Comprehensive test suite in `tests/core/controller/test_execution_controller.py`
- Tests cover:
  - Successful plan execution
  - Failure handling and recovery
  - State persistence
  - State variable management
  - Operation type handling

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