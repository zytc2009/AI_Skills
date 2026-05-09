# codebase-analysis-skills

两个互补的 Claude Code skill，用于把代码项目转成中文文档：

| Skill | 产物风格 | 何时触发 |
|---|---|---|
| [`project-analyzer`](./project-analyzer/SKILL.md) | 工程分析（定位、技术栈、流程、风险、玩法、关键文件索引） | "分析这个项目"、"落入知识库"、"做一份工程文档"、"上手笔记" |
| [`pocketflow-tutorial`](./pocketflow-tutorial/SKILL.md) | 章节教程（Chapter 1/2/3 入门 walkthrough） | 明确点名 "PocketFlow"、"章节教程"、"入门教程"、"tutorial walkthrough" |

两者**输出风格不同、目标读者不同**，因此拆成两个 skill 而不是合一。如果用户只说"分析"，默认走 `project-analyzer`；只有显式要章节教程时才转 `pocketflow-tutorial`。

## 设计原则

skill 自身**不预设项目分类**（不强加 "工作 / 私人 / 学习" 这种结构）。文档去哪里写，按以下优先级决定：

1. 用户当前会话明确指定的输出路径。
2. 用户全局 / 项目级 `CLAUDE.md` 中定义的目录约定。
3. 都没有 → 当面问用户，不要默认行为。

skill 唯一的硬规则是：**不要把分析文档写进被分析的代码仓**（除非用户明说）。

## 决策树

```
用户说要做项目文档
      │
      ├─ 提到 "教程" / "walkthrough" / "PocketFlow" / "Chapter X" ?
      │     ├─ 是 → pocketflow-tutorial
      │     └─ 否 ↓
      │
      ├─ 想要工程判断、决策依据、玩法建议、风险评估 ?
      │     └─ 是 → project-analyzer
      │
      └─ 模糊不清 → 先问用户，不要默认行为
```

## 配置占位符

只有两个真正需要安装时配置的路径：

| 占位符 | 含义 | 说明 |
|---|---|---|
| `<POCKETFLOW_ROOT>` | PocketFlow-Tutorial-Codebase-Knowledge 源码目录 | 仅 `pocketflow-tutorial` 用到。本机克隆/下载位置。 |
| `<SKILLS_BUNDLE_ROOT>` | 当前这个 skill bundle 的本地路径 | 仅安装命令用到，安装完成后无需引用。 |

文档中其它出现的尖括号符号（`<SOURCE_PROJECT>`、`<DOCS_TARGET>`、`<项目名>` 等）是**每次会话的运行参数**，不是安装时配置——由用户在请求时给出，或 Claude 当面询问。

替换方式：

1. **手工替换**：在你本机拷贝的 `pocketflow-tutorial/SKILL.md` 中用编辑器替换 `<POCKETFLOW_ROOT>` 为真实路径。
2. **由 CLAUDE.md 指定**：在 `~/.claude/CLAUDE.md` 中写"PocketFlow 源码在 <真实路径>"，让 Claude 在调用 skill 时优先以此为准（保留占位符即可）。

## 安装

skill 通过文件系统加载，把这两个子目录放到 Claude Code 能扫到的位置即可。

### 方案 A：用户级别（所有项目共享）

```powershell
# 复制
Copy-Item -Recurse "<SKILLS_BUNDLE_ROOT>\project-analyzer"   "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse "<SKILLS_BUNDLE_ROOT>\pocketflow-tutorial" "$env:USERPROFILE\.claude\skills\"

# 或软链（推荐，改一处即生效）
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\project-analyzer"   -Target "<SKILLS_BUNDLE_ROOT>\project-analyzer"
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\pocketflow-tutorial" -Target "<SKILLS_BUNDLE_ROOT>\pocketflow-tutorial"
```

### 方案 B：项目级别（仅当前 repo 启用）

```powershell
# 假设当前仓库根
New-Item -ItemType Directory -Force -Path ".claude\skills"
Copy-Item -Recurse "<SKILLS_BUNDLE_ROOT>\project-analyzer"   ".claude\skills\"
Copy-Item -Recurse "<SKILLS_BUNDLE_ROOT>\pocketflow-tutorial" ".claude\skills\"
```

安装后重启 Claude Code 会话，让 skill 索引重建；或在新会话中验证 skill 是否出现在可用列表。

## 依赖

- **`project-analyzer`** 无外部依赖，只用 Claude 自身的 Read/Grep/Bash。
- **`pocketflow-tutorial`** 依赖：
  - PocketFlow 源码：`<POCKETFLOW_ROOT>`
  - Python 3 + `pip install -r requirements.txt`
  - 至少一个 CLI 后端：`claude` 或 `codex`，可在 PATH 中调用
  - `utils/call_llm.py` 已支持 `LLM_PROVIDER=CLAUDE_CLI` / `CODEX_CLI` / `CLI`

如果 PocketFlow 源码位置变了，更新 `pocketflow-tutorial/SKILL.md` 顶部 "Tool location" 段中的 `<POCKETFLOW_ROOT>` 引用。

## 维护说明

- **保持两个 skill 描述互斥**。改 description 时检查不会和另一个的触发词重叠（例如不要在 `project-analyzer` 里加 "tutorial"，也不要在 `pocketflow-tutorial` 里加 "工程分析"）。
- **不要往 SKILL.md 里塞个人目录约定**。skill 是通用工件，分类规则放在 CLAUDE.md，由用户自己维护。
- **PocketFlow 升级后**：检查 `main.py` 的参数是否变了、`utils/call_llm.py` 的 CLI 分支是否还在；若变了，更新 `pocketflow-tutorial/SKILL.md` 的 "Argument cheatsheet" 和 "Required environment variables"。
- **不要把这两个 skill 改成一个**。合并会让触发判定模糊，且工程分析与章节教程在写作模板、输出目录、调用路径上都不同。
