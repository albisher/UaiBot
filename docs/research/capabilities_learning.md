# Capabilities Learning in UaiBot

## Overview
UaiBot is designed to learn and adapt its capabilities over time, enabling robust cross-platform automation and intelligent user interaction. This document outlines the architecture, rationale, and future research directions for capability learning in UaiBot.

## Architecture
- **Knowledge Base:**
  - Stores structured logs of command results, including capability, OS, action, command pattern, and success/failure counts.
  - Enables UaiBot to track which actions and patterns are reliable on which platforms.

- **Embeddings & Vector Search (TODO):**
  - **Future Enhancement:** UaiBot will use Sentence Transformers to generate semantic embeddings for commands and store them in Milvus, a scalable vector database.
  - **Current State:** UaiBot continues to learn using a structured knowledge base, tracking command patterns and success/failure counts.
  - **Rationale:** Embeddings will enable semantic generalization, allowing UaiBot to suggest alternatives based on meaning, not just exact patterns.

- **Learning Pipeline:**
  1. **Command Execution:** Each command is executed and the result is logged.
  2. **Knowledge Update:** The knowledge base is updated with the outcome, and the command embedding is stored in Milvus.
  3. **Suggestion:** On failure (or proactively), UaiBot queries Milvus for similar commands and suggests alternatives based on both pattern and semantic similarity.

## Rationale
- **Cross-Platform Adaptation:** By tracking OS and capability, UaiBot can adapt its behavior to the user's environment.
- **Semantic Generalization:** Embeddings allow UaiBot to generalize from past experience, suggesting alternatives even for novel or paraphrased commands.
- **Continuous Improvement:** Every interaction makes UaiBot smarter, as the knowledge base and vector store grow over time.

## Example Use Cases
- If a mouse drag command fails on Linux, UaiBot can suggest a similar successful command or a different action (e.g., move and click) that worked on that OS.
- For a new keyboard shortcut, UaiBot can find and suggest similar shortcuts that have been successful in the past.

## Future Research Directions
- **Multi-Modal Embeddings:** Integrate visual, audio, or context embeddings for richer capability learning.
- **Context-Aware Suggestions:** Use session/user context to further personalize suggestions.
- **Active Learning:** Proactively ask users for feedback on suggestions to accelerate learning.
- **Capability Chaining:** Learn and suggest multi-step workflows based on past successful sequences.

## References
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io)
- [Milvus Vector Database](https://milvus.io)
- [Sentence Transformers](https://www.sbert.net)
- [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/chapter18/) 