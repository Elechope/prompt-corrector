# Prompt Corrector Skill (意图与拼写纠正器)

A commercial-grade intent and spelling corrector skill for AI Agents (like Cursor, Claude Code, etc.). It acts as an intelligent guardrail, intercepting typos, homophone errors, and garbled speech-to-text inputs before they cause hallucinations or execute destructive commands.

一个为 AI Agent（如 Cursor, Claude Code 等）打造的商业级意图与拼写纠错技能。它作为一道智能护栏，能够在错别字、同音字错误或语音输入乱码导致 AI 产生幻觉或执行破坏性命令之前，对其进行拦截与纠正。

## Features | 核心特性

- ⚡ **Zero-Latency Pre-filtering | 零延迟预过滤**: Uses a lightweight Python script to instantly pass whitelisted or short terms without consuming LLM tokens. (使用轻量级 Python 脚本瞬间放行白名单或简短词汇，不消耗大模型 Token。)
- 🧠 **Context-Aware Correction | 上下文感知纠错**: Understands Chinese homophones (e.g., "运型" -> "运行") and English typos based on programming context. (基于编程上下文，精准理解中文同音字错误及英文拼写错误。)
- 🛡️ **False Positive Prevention | 防误杀机制**: Checks local dictionaries and project context before correcting, preventing domain jargon from being "fixed". (在纠错前检查本地词典与项目上下文，防止专业术语或黑话被错误“修正”。)
- 🔄 **Self-Evolving Feedback Loop | 自我进化反馈闭环**: If a user rejects a correction, the agent searches the codebase to verify the term and automatically adds it to the whitelist. (当用户拒绝纠正时，Agent 会自动搜索代码库进行求证，并将确认的词汇自动加入白名单。)
- 📂 **Codebase Indexing | 代码库索引**: Includes a background script to rapidly index project files and extract domain-specific terminology. (内置后台脚本，支持极速索引项目文件并提取项目专有名词。)

## Directory Structure | 目录结构

```text
prompt-corrector/
├── SKILL.md                          # Core agent instructions / Agent 核心指令与工作流
├── references/
│   └── correction-rules.md           # Knowledge base for typos / 常见错误知识库
├── scripts/
│   ├── pre_filter.py                 # Fast heuristic check / 极速预过滤脚本
│   ├── add_to_whitelist.py           # Auto-learning script / 自动学习脚本
│   └── extract_project_terms.py      # Codebase indexing script / 代码库索引脚本
└── assets/
    ├── config.json                   # Extensible scan configuration / 可扩展的扫描配置
    └── user_dictionary.json          # Whitelist and project terms / 白名单与项目词汇表 (自动更新)
```

## Installation | 安装指南

1. Copy the `prompt-corrector` folder into your project's `.cursor/skills/` directory (or the equivalent skills directory for your agent).
   (将 `prompt-corrector` 文件夹复制到你项目的 `.cursor/skills/` 目录下，或你的 Agent 对应的技能目录中。)
2. The agent will automatically read `SKILL.md` and apply the guardrails to your future prompts.
   (Agent 会自动读取 `SKILL.md`，并在你后续的对话中应用这些智能护栏。)

## Usage Examples | 使用示例

**1. Silent Auto-Correction (High Confidence) | 静默纠正（高置信度）**
- User: "帮我运型一下这个脚本"
- Agent: *(已自动将“运型”识别为“运行”)* -> Proceeds to run the script. (继续执行脚本)

**2. Intercept and Confirm (Low Confidence) | 拦截并确认（低置信度）**
- User: "把数局不熟到买色扣"
- Agent: "请问您是指“把数据部署到MySQL”的意思吗？如果是的话请直接回答“是”，如果不是请详细说明。"

**3. Auto-Learning from Rejection | 拒绝后的自动学习**
- User: "不是，我就是指 uzer 表"
- Agent: *(Searches codebase for "uzer" / 在代码库中搜索 "uzer")* -> *(Adds "uzer" to whitelist / 将其加入白名单)* -> Proceeds with task. (继续执行任务)