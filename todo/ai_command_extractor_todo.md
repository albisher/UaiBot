# TODOs for ai_command_extractor.py

- Refactor prompt so canonical examples are after user input and clearly marked as examples only.
- Add explicit instruction: "Do NOT copy the example. Generate a plan for the user's actual request above."
- Ensure user input is the clear focus of the prompt.
- Add support for including system state/context (e.g., open windows, running processes) in the prompt.
- Plan for integration of image-to-text (vision) models for milestone checks and visual feedback.
- Support passing GUI content as context to the AI for more accurate command planning.
- Consider few-shot or negative examples to prevent overfitting to the canonical example.
- Make prompt robust for future extensibility and model changes. 