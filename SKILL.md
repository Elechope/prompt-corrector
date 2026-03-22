---
name: prompt-corrector
description: A commercial-grade intent and spelling corrector with auto-learning and codebase indexing. Analyzes user prompts for errors, prevents false positives using context, and learns from user feedback. Trigger automatically on new user queries.
---

# Prompt Corrector (意图与拼写纠正器)

## Instructions

When receiving a new prompt from the user, before executing any complex tasks, searching the codebase, or writing code, you MUST follow this commercial-grade workflow:

### Step 1: Fast Pre-filtering (Latency Optimization)
Run the lightweight Python pre-filter script to perform a fast heuristic and dictionary check.
Run command: `python .cursor/skills/prompt-corrector/scripts/pre_filter.py "<user_prompt>"`
- If the script outputs `{"status": "PASS"}`, proceed with the user's request directly. Skip the rest of this skill.
- If the script outputs `{"status": "NEEDS_LLM"}`, proceed to Step 2.

### Step 2: Contextual Memory & Dictionary Check (False Positive Prevention)
Before deciding a word is a typo, you MUST check two layers of memory:
1. **Long-term Memory (Dictionary)**: Read `.cursor/skills/prompt-corrector/assets/user_dictionary.json`. Any terms listed in the `whitelist` or `project_terms` MUST NOT be corrected.
2. **Short-term Memory (Context Window)**: Scan the current conversation history and any files you have recently read. If the suspected typo exactly matches a variable name, file name, or a term the user has insisted on using earlier, **DO NOT correct it**.

### Step 3: Semantic Analysis & Confidence Grading
If the term is not in memory, analyze the prompt for errors (refer to `references/correction-rules.md`). Assign a Confidence Level:
- **High Confidence / Low Risk**: Obvious typos (e.g., "funciton" -> "function", "下在" -> "下载").
- **Low Confidence / High Risk**: Severe garbling, ambiguous terms, or major structural changes.

### Step 4: Execution & UX Handling (Non-blocking UX)
**Mode A: Silent Auto-Correction (High Confidence)**
DO NOT block the user. Proceed immediately using the corrected prompt. Prepend this note to your response:
- Chinese: `*(已自动将“{原词}”识别为“{正确词}”)*`
- English: `*(Auto-corrected "{original}" to "{corrected}")*`

**Mode B: Intercept and Confirm (Low Confidence)**
DO NOT proceed. Ask for confirmation using EXACTLY these formats:
- Chinese: `请问您是指“[纠正后的完整句子]”的意思吗？如果是的话请直接回答“是”，如果不是请详细说明。`
- English: `Do you mean "[Corrected full sentence]"? If so, please answer directly with "Yes". If not, please provide a detailed explanation.`

### Step 5: Feedback Loop, Smart Search & Auto-Learning
If you used Mode B and the user rejects your correction (e.g., "不是，我就是指 [原词]"), you MUST follow this sequence:
1. **Smart Search (Targeted Verification)**: Before immediately adding it to the whitelist, use the `Glob` or `Grep` tools to perform a quick, targeted search in the codebase for the `[原词]` or any file paths mentioned in the user's prompt.
2. **If Found**: 
   - Acknowledge the finding.
   - Automatically run: `python .cursor/skills/prompt-corrector/scripts/add_to_whitelist.py "<user_original_word>"`
   - Proceed with the user's task.
3. **If NOT Found**:
   - DO NOT add it to the whitelist yet.
   - Reply to the user: `我在当前项目中没有搜索到名为“[原词]”的文件或代码。请问它是一个外部概念，还是在某个特定的目录下？请提供更多上下文。`

### Step 6: Codebase Indexing (Background Task)
To keep the `project_terms` up to date with the codebase without blocking the user, the Agent can periodically index the project.
- **Do not run this on every prompt.**
- Run this ONLY when the user explicitly asks to "更新词库", "扫描项目", or when initializing the project for the first time.
- Command: `python .cursor/skills/prompt-corrector/scripts/extract_project_terms.py`