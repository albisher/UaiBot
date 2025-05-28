# Labeeb Learning Mechanism

Labeeb uses a learning mechanism to improve its performance over time. This document explains how it works and how it can be extended.

## How It Works

1. **Learning from Results:**  
   Every command result is logged into a JSON-based knowledge base, tracking:
   - **Capability** (e.g., `mouse_control`)
   - **OS** (e.g., `darwin`, `windows`, `linux`)
   - **Action** (e.g., `move_to`, `click`)
   - **Command Pattern** (e.g., `move mouse to (x, y)`)
   - **Success/Failure Counts**

2. **Adaptation:**  
   If a command fails, Labeeb checks the knowledge base for reliable alternatives on the current OS. It suggests alternative actions or command patterns that have historically worked well.

3. **Knowledge Base Structure:**  
   ```json
   {
     "mouse_control": {
       "darwin": {
         "actions": {
           "move_to": {"success_count": 10, "fail_count": 0},
           "click": {"success_count": 8, "fail_count": 2}
         },
         "command_patterns": {
           "move mouse to (x, y)": {"success_count": 5, "fail_count": 0}
         }
       },
       "windows": {...},
       "linux": {...}
     }
   }
   ```

## Embeddings and Vector Databases

Labeeb now uses **Milvus** and **Sentence Transformers** for advanced learning:

- **Sentence Transformers:**  
  Generates high-quality embeddings for commands, capturing semantic meaning.

- **Milvus:**  
  A scalable vector database that stores and retrieves embeddings efficiently, supporting cross-platform deployment (Windows, Mac, Ubuntu, ARM).

This allows Labeeb to suggest alternatives based on semantic similarity, not just exact patterns.

## Future Improvements

- **Expanding to Other Capabilities:**  
  Extend the learning mechanism to handle other capabilities (e.g., keyboard input, screen reading).

- **Improving Suggestions:**  
  Enhance the suggestion mechanism to provide more context-aware recommendations. 