---
name: pocketflow-tutorial
description: Generate beginner-style chapter tutorials for a codebase using PocketFlow-Tutorial-Codebase-Knowledge with Claude CLI or Codex CLI as the LLM backend. Use only when the user explicitly asks for PocketFlow output, "章节教程", "入门教程", "walkthrough", or wants the docs/<项目>/ Chapter 1/2/3 style. For engineering-level project analysis, use the project-analyzer skill instead.
---

# PocketFlow Tutorial Runner

This skill is a runbook for invoking PocketFlow's tutorial generator with a local CLI backend (Claude / Codex), so it does not need a Gemini API key. It produces beginner-friendly, multi-chapter Markdown tutorials—not engineering analysis.

If the user wants project decision/architecture/onboarding documentation, hand off to `project-analyzer` instead.

Path placeholders such as `<POCKETFLOW_ROOT>`, `<SOURCE_PROJECT>`, and `<DOCS_TARGET>` are configured at install time or asked from the user per run. See the bundle README. The skill imposes no project taxonomy of its own—follow the user's CLAUDE.md or ask.

## When to use

Trigger this skill when the user clearly asks for:

- "PocketFlow", "章节教程", "入门教程", "tutorial", "walkthrough"
- Output that looks like `<POCKETFLOW_ROOT>/docs/<项目>/Chapter 1 ...`
- A friendly explainer of an unfamiliar repo, not a technical decision document

If the user only says "分析这个项目" / "落入知识库" without mentioning tutorials, prefer `project-analyzer`.

## Tool location

- Source: `<POCKETFLOW_ROOT>`
- Entrypoint: `python main.py`
- LLM dispatcher: `<POCKETFLOW_ROOT>/utils/call_llm.py` (already supports `LLM_PROVIDER=CLAUDE_CLI` / `CODEX_CLI`)

Always run commands from the PocketFlow directory so relative paths (`logs/`, `llm_cache.json`, default `./output`) resolve correctly.

## Required environment variables

Pick one backend per run.

### Claude CLI

```
LLM_PROVIDER=CLAUDE_CLI
CLAUDE_CLI_COMMAND=claude -p --permission-mode dontAsk --output-format text
CLI_LLM_TIMEOUT=600
```

Notes:
- `--permission-mode dontAsk` disables the per-tool prompt because PocketFlow drives `claude` non-interactively. Do not enable this in interactive shells.
- The default command sends the prompt via stdin. Do not change it to `{prompt_content}` on Windows—`call_llm.py` rejects that.

### Codex CLI

```
LLM_PROVIDER=CODEX_CLI
CODEX_CLI_COMMAND=codex exec --skip-git-repo-check -c approval_mode=full-auto -o {output_file} -
CLI_LLM_TIMEOUT=600
```

Notes:
- `{output_file}` is templated by `call_llm.py` into a temp file; do not remove it.
- `--skip-git-repo-check` is required because the analyzed repo may not be a git workspace.

### Generic OpenAI-compatible CLI

```
LLM_PROVIDER=CLI
CLI_COMMAND=<your command, may include {prompt_file} and/or {output_file}>
```

## Output destination

Two hard rules, no taxonomy of project types:

1. **Never write into the analyzed repo.** Always pass `-o` (or `--output`) explicitly to a directory outside the source.
2. **Pick the destination from the user's CLAUDE.md or by asking.** Do not invent categories ("work" vs "private" etc.) on your own.

If the directory already has a tutorial, ask whether to overwrite, version with a date suffix, or merge.

## Run templates (PowerShell)

Always run from `<POCKETFLOW_ROOT>`. Quote paths that contain spaces.

### Local directory, Claude backend

```powershell
$env:LLM_PROVIDER = "CLAUDE_CLI"
$env:CLAUDE_CLI_COMMAND = "claude -p --permission-mode dontAsk --output-format text"
$env:CLI_LLM_TIMEOUT = "600"

python main.py `
  --dir "<SOURCE_PROJECT>" `
  --name "<项目名>" `
  --output "<DOCS_TARGET>" `
  --language "Chinese" `
  --include "*.py" "*.cpp" "*.h" "*.md" `
  --exclude "*test*" "*build*" `
  --max-abstractions 10
```

### GitHub repo, Codex backend

```powershell
$env:LLM_PROVIDER = "CODEX_CLI"
$env:CODEX_CLI_COMMAND = "codex exec --skip-git-repo-check -c approval_mode=full-auto -o {output_file} -"
$env:CLI_LLM_TIMEOUT = "600"
$env:GITHUB_TOKEN = "<token>"  # optional, only if hitting rate limits

python main.py `
  --repo "https://github.com/<owner>/<repo>" `
  --output "<DOCS_TARGET>" `
  --language "Chinese"
```

## Argument cheatsheet (from `main.py`)

| Flag | Default | Notes |
|---|---|---|
| `--repo` / `--dir` | required, mutually exclusive | One of GitHub URL or local path |
| `-n`, `--name` | derived | Always set explicitly for stable directory naming |
| `-o`, `--output` | `./output` | Override per the table above |
| `-i`, `--include` | broad code+md+yaml | Narrow this for large repos to control cost |
| `-e`, `--exclude` | tests/build/legacy | Add project-specific noise here |
| `-s`, `--max-size` | 100000 (≈100KB) | Skip giant generated files |
| `--language` | `english` | Use `Chinese` to match the user's docs |
| `--max-abstractions` | 10 | 6–8 is often cleaner for medium repos |
| `--no-cache` | off | Leave cache on for iterative runs |

## Known pitfalls

- **Windows + `{prompt_content}`**: Not supported. `call_llm.py` raises if you try. Use the default stdin/`{prompt_file}` flows.
- **Large repos**: Default include patterns plus 10 abstractions can run for a long time and burn many CLI invocations. Always narrow `--include` and lower `--max-abstractions` first.
- **Cache file**: `llm_cache.json` is in the PocketFlow directory and is shared across runs. Delete it (or pass `--no-cache`) if you switched backends and want a clean reproduction.
- **Logs**: `logs/llm_calls_YYYYMMDD.log` records every prompt and response. Useful for debugging hangs; sensitive content goes in here, do not commit.
- **`--permission-mode dontAsk`**: Bypasses Claude CLI permission prompts. Only use it for this batch generator, never as a general default.

## After the run

1. Confirm the output directory contains `index.md` and `Chapter 0X ...md` files. If only `index.md` exists, the LLM call failed mid-flow—check `logs/`.
2. Spot-check one chapter for hallucinations. PocketFlow's prompts are tuned for explanation, not correctness; treat the output as a draft.
3. If the user asked for a knowledge-base entry, also create or update a short summary under the project's documentation root linking to the tutorial directory—do not assume readers will find it on their own.

## Out of scope

- Engineering analysis, architecture decisions, "玩法/价值" sections → use `project-analyzer`.
- Editing PocketFlow's prompts or nodes → that is a code change to the upstream, not a skill task.
- Running PocketFlow against the user's work code without an explicit output path → refuse and ask, to avoid writing into the source repo.
