---
name: prompt-corrector
description: A commercial-grade intent and spelling corrector with auto-learning and codebase indexing. Analyzes user prompts for errors, prevents false positives using context, and learns from user feedback. Trigger automatically on new user queries.
---

# Prompt Corrector (意图与拼写纠正器)

## Instructions

When receiving a new prompt from the user, before executing any complex tasks, searching the codebase, or writing code, you MUST follow this commercial-grade workflow:

### Step 1: Fast Pre-filtering (Latency Optimization)
Run the lightweight Python pre-filter script to perform a fast heuristic and dictionary check.
**Execution Guardrail**: Always use standard input (stdin) to pass the prompt to prevent Shell Injection. Do NOT concatenate the prompt directly into the command line.
Run command: `echo "<user_prompt>" | python .cursor/skills/prompt-corrector/scripts/pre_filter.py`
- If the script outputs `{"status": "PASS"}`, proceed with the user's request directly. Skip the rest of this skill.
- If the script outputs `{"status": "NEEDS_LLM"}`, proceed to Step 2.

### Step 2: Contextual Memory & Dictionary Check (False Positive Prevention)
Before deciding a word is a typo, you MUST check two layers of memory:
1. **Long-term Memory (Dictionary)**: Read `.cursor/skills/prompt-corrector/assets/user_dictionary.json`. Any terms listed in the `whitelist` or `project_terms` MUST NOT be corrected.
2. **Short-term Memory (Context Window)**: Scan the current conversation history and any files you have recently read. If the suspected typo exactly matches a variable name, file name, or a term the user has insisted on using earlier, **DO NOT correct it**.

### Step 3: Semantic Analysis & Confidence Grading
If the term is not in memory, analyze the prompt for errors (refer to `references/correction-rules.md`). Assign a Confidence Level:
- **High Confidence / Low Risk**: Obvious typos (e.g., "funciton" -> "function", "下在" -> "下载").
- **Medium Confidence / Moderate Risk**: Garbled terms that are highly likely to be a specific intent, but not 100% certain.
- **Low Confidence / High Risk**: Severe garbling, ambiguous terms, or major structural changes.

### Step 4: Execution & UX Handling (Flow Protection)
To protect the user's state of flow, minimize blocking interactions:

**Mode A: Silent Auto-Correction (High Confidence)**
DO NOT block the user. Proceed immediately using the corrected prompt. Prepend this note to your response:
- `*(已自动将“{原词}”识别为“{正确词}”)*`

**Mode B: Soft Prompting (Medium Confidence - Non-blocking)**
DO NOT block the user. Assume your correction is right and proceed with the task, but add a prominent disclaimer at the very top:
- `*[推测您是指“{正确词}”，已按此意图执行。若有误，请随时回复“停止”或纠正我。]*`

**Mode C: Intercept and Confirm (Low Confidence - Blocking)**
ONLY use this for highly ambiguous or destructive commands. DO NOT proceed. Ask for confirmation:
- `请问您是指“[纠正后的完整句子]”的意思吗？如果是的话请直接回答“是”，如果不是请详细说明。`

### Step 5: Feedback Loop, Smart Search & Auto-Learning
If the user rejects your correction (e.g., "不是，我就是指 [原词]"):
1. **Smart Search (Targeted Verification)**: Use the `Glob` or `Grep` tools to perform a quick search in the codebase for the `[原词]`.
2. **If Found**: 
   - Acknowledge the finding.
   - Automatically run (using stdin for safety): `echo "<user_original_word>" | python .cursor/skills/prompt-corrector/scripts/add_to_whitelist.py`
   - Proceed with the user's task.
3. **If NOT Found**:
   - Reply to the user: `我在当前项目中没有搜索到名为“[原词]”的文件或代码。请提供更多上下文。`

### Step 6: Codebase Indexing (Background Task)
To keep `project_terms` up to date without blocking the user:
- **Do not run this on every prompt.**
- Run this ONLY when the user explicitly asks to "更新词库", "扫描项目", or when initializing the project.
- Command: `python .cursor/skills/prompt-corrector/scripts/extract_project_terms.py`
- *Note: The script respects `.gitignore` and uses incremental scanning logic to ensure high performance.*