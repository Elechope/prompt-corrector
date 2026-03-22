# Prompt Corrector Skill

A commercial-grade intent and spelling corrector skill for AI Agents (like Cursor, Claude Code, etc.). It acts as an intelligent guardrail, intercepting typos, homophone errors, and garbled speech-to-text inputs before they cause hallucinations or execute destructive commands.

## Features

- ⚡ **Zero-Latency Pre-filtering**: Uses a lightweight Python script to instantly pass whitelisted or short terms without consuming LLM tokens.
- 🧠 **Context-Aware Correction**: Understands Chinese homophones (e.g., "运型" -> "运行") and English typos based on programming context.
- 🛡️ **False Positive Prevention**: Checks local dictionaries and project context before correcting, preventing domain jargon from being "fixed".
- 🔄 **Self-Evolving Feedback Loop**: If a user rejects a correction, the agent searches the codebase to verify the term and automatically adds it to the whitelist.
- 📂 **Codebase Indexing**: Includes a background script to rapidly index project files and extract domain-specific terminology.

## Directory Structure

```text
prompt-corrector/
├── SKILL.md                          # Core agent instructions and workflow
├── references/
│   └── correction-rules.md           # Knowledge base for common typos
├── scripts/
│   ├── pre_filter.py                 # Fast heuristic check
│   ├── add_to_whitelist.py           # Auto-learning script
│   └── extract_project_terms.py      # Codebase indexing script
└── assets/
    └── user_dictionary.json          # Whitelist and project terms (auto-updated)
```

## Installation

1. Copy the `prompt-corrector` folder into your project's `.cursor/skills/` directory (or the equivalent skills directory for your agent).
2. The agent will automatically read `SKILL.md` and apply the guardrails to your future prompts.

## Usage Examples

**1. Silent Auto-Correction (High Confidence)**
- User: "帮我运型一下这个脚本"
- Agent: *(已自动将“运型”识别为“运行”)* -> Proceeds to run the script.

**2. Intercept and Confirm (Low Confidence)**
- User: "把数局不熟到买色扣"
- Agent: "请问您是指“把数据部署到MySQL”的意思吗？..."

**3. Auto-Learning from Rejection**
- User: "不是，我就是指 uzer 表"
- Agent: *(Searches codebase for "uzer")* -> *(Adds "uzer" to whitelist)* -> Proceeds with task.