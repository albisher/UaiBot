# Ollama Health Check

This document explains how to verify that the Ollama AI backend is running and ready for use with Labeeb.

## 1. Starting Ollama

If you have Ollama installed, start the server with:

```bash
ollama serve
```

To download a model (e.g., gemma:2b):

```bash
ollama pull gemma:2b
```

## 2. Running the Health Check

Use the provided script to check if Ollama is running and if the required model is available:

```bash
python3 app/health_check/ollama_health_check.py
```

## 3. Interpreting Results

- `✅ Ollama server is running.` — The server is up and reachable.
- `✅ Model 'gemma:2b' is available.` — The required model is ready to use.
- `❌` messages indicate what is missing or needs to be fixed (e.g., server not running, model not downloaded).

## 4. Troubleshooting

- If the server is not running, start it with `ollama serve`.
- If the model is missing, run `ollama pull gemma:2b` (or your desired model).
- Ensure the Ollama server is listening on `http://localhost:11434` (default).

## 5. Integration

Labeeb uses Ollama as its default AI backend. This health check ensures the backend is ready for plan-based command interpretation and execution. 