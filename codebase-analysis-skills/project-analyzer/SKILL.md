---
name: project-analyzer
description: Analyze local or GitHub code projects and produce Chinese engineering documentation for the user's knowledge base. Use when the user asks to analyze a project, repo, codebase, directory, architecture, technical implementation, value, usage/playbook, onboarding notes, or to "落入知识库". Prefer this skill over generic summaries or tutorial generators unless the user explicitly asks to run PocketFlow.
---

# Project Analyzer

Use this skill to turn a code project into useful Chinese engineering documentation. The goal is not a marketing tutorial; it is an actionable project analysis that helps the user understand, use, maintain, or decide whether to adopt the project.

## Output Principle

Prefer engineering judgment over broad narration:

- Identify what the project actually does.
- Explain how it is built.
- Trace the main data/control flows.
- Call out risks, limits, and extension points.
- Explain value and practical "玩法".
- Save the result in the user's external documentation/knowledge directory when requested or implied.

Do not write project documentation inside the analyzed code repository unless the user explicitly asks.

## User Paths

Path placeholders below are configured at install time (see the bundle README). If the user's global CLAUDE.md defines different conventions, defer to CLAUDE.md.

| Project type | Code path | Documentation target |
|---|---|---|
| Obsidian vault | Any source captured as knowledge | `<OBSIDIAN_VAULT>/02-Projects/` or the relevant vault area |

Hard rule: do not write analysis documents into the analyzed code repo. Pick the destination from the user's CLAUDE.md or by asking. The skill imposes no project taxonomy of its own.

Use Chinese filenames for new documentation. Before creating a new file, list the target directory and merge/update an existing same-topic document if present.

## Quick Workflow

1. **Scope**
   - Determine the target path/repo and whether the user wants analysis only or a saved document.
   - If scope is ambiguous, ask before analyzing.
   - For batch directory analysis, skip projects whose latest meaningful Git commit is older than 3 years unless the user says otherwise.

2. **Baseline**
   - Capture project path, Git remote URL, current branch, latest commit hash/date, and analysis date.
   - If Git is unavailable or blocked by safe-directory, read `.git/config` for remote and state any missing baseline.

3. **Read in this order**
   - README / QUICKSTART / DESIGN / ARCHITECTURE / AGENTS / CLAUDE / docs.
   - Dependency manifests: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `docker-compose.yml`, etc.
   - Entrypoints and route/config files.
   - Core modules named by docs/manifests.
   - Tests only when they clarify behavior or reliability.

4. **Analyze**
   - Project positioning and audience.
   - Tech stack and runtime/deployment.
   - Directory/module map.
   - Main execution/data flows.
   - Core abstractions and responsibilities.
   - External integrations and credentials.
   - State/storage/concurrency/error handling.
   - Value, use cases, and "玩法".
   - Risks, missing tests, operational limits, and recommended next changes.

5. **Write**
   - Use concise but detailed Chinese Markdown.
   - Include source path, Git URL, branch, commit, and analysis date near the top.
   - Cite key local files with paths.
   - Make the document useful as a future onboarding note, not just a summary.

6. **Verify**
   - Confirm the output file exists and is readable as UTF-8.
   - If writing to Obsidian, rebuild/update the index when the local Obsidian tooling supports it.

## Recommended Document Structure

```markdown
# <项目名> 项目分析

- 源码路径：
- Git 地址：
- 分支 / commit：
- 分析日期：

## 1. 项目定位

## 2. 技术栈

## 3. 目录结构与模块边界

## 4. 核心技术实现

## 5. 关键流程

## 6. 外部集成与配置

## 7. 数据、状态与并发模型

## 8. 价值与适用场景

## 9. 玩法建议

## 10. 风险、限制与改造建议

## 11. 关键文件索引
```

For small projects, merge sections to keep the document readable. For large projects, split into multiple Chinese-named documents in the target documentation directory.

## PocketFlow Hand-off

If the user actually wants PocketFlow's chapter-style beginner tutorial (the `docs/<项目>/Chapter 1/2/3 ...` format), do not run it from this skill. Hand off to the `pocketflow-tutorial` skill, which owns the run command, env vars (`CLAUDE_CLI` / `CODEX_CLI`), output directory rules, and known pitfalls.

This skill stays focused on engineering analysis. Treat PocketFlow output, when it exists, as supplementary draft material—never as the final analysis.

## Quality Bar

- Do not overclaim if code was skipped, too large, or unavailable.
- Distinguish source-backed facts from inference.
- Preserve useful nuance: "project says X, code currently does Y" is often important.
- Avoid generic praise. The final document should help the user decide what to do next.
