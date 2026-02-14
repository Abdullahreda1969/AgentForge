# 🚀 AgentForge v0.6.0

An autonomous AI-powered software engineer that designs, codes, tests, and self-corrects applications.

## 🧠 Current Capabilities

- **Architecting:** Automatically generates folder structures based on project descriptions.
- **Multi-Agent Coding:** Uses **Gemma 3** to write clean, modular Python code.
- **Syntax Validation:** Built-in `TesterAgent` ensures code is syntactically correct before saving.
- **Runtime Execution:** `ExecutorAgent` runs the generated code in a sub-process to verify logic.
- **Self-Healing Loop:** The system detects runtime errors and logical failures, providing feedback to the AI for up to 3 retry attempts.

## 🛠️ Tech Stack

- **Engine:** Python 3.14+
- **AI Brain:** Google GenAI (Gemma-3-1b-it)
- **Orchestration:** Custom Multi-Agent Orchestrator

## 📈 Recent Achievement

Successfully generated **GoldTracker**, a project that went through 3 iterations of self-correction to fix `NameError` and logic failures automatically.
