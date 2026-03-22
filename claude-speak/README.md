# claude-speak

> 按住按键说话，松开自动转写粘贴到 Claude Code。

本地 Whisper 转写，无需 API Key，完全离线，支持 Windows / macOS / Linux。

---

## 工作原理

```
按住触发键  →  sounddevice 录制音频（16 kHz）
松开按键    →  faster-whisper 本地转写（CPU）
            →  文字通过剪贴板自动粘贴到当前窗口
```

---

## 安装

### 方式 A — 一键安装

```bash
# Windows
install.bat

# macOS / Linux
chmod +x install.sh && ./install.sh
```

### 方式 B — 手动安装

```bash
# 1. 安装 Python 依赖
pip install -r scripts/requirements.txt

# 2. 复制 speak.py 到脚本目录
#    Windows:    %USERPROFILE%\.claude\scripts\speak.py
#    macOS/Linux: ~/.claude/scripts/speak.py

# 3. 安装 Claude Code 技能
mkdir -p ~/.claude/skills/speak
cp SKILL.md ~/.claude/skills/speak/SKILL.md
```

---

## 使用方法

在**独立终端**中运行 `speak.py`，保持与 Claude Code 并行：

```bash
# 推荐配置（中文，小模型，Caps Lock 触发）
python ~/.claude/scripts/speak.py --model small --lang zh --key caps_lock

# 英文，默认触发键（右 Alt）
python ~/.claude/scripts/speak.py --lang en
```

**步骤：**

1. 点击 Claude Code 输入框使其获得焦点
2. 按住触发键，看到 🔴 录音中...
3. 说话
4. 松开 → 🔄 转写中... → ✅ 自动粘贴
5. 若自动粘贴失败，文字会打印到终端并已复制到剪贴板，可手动 Ctrl+V 粘贴

在 speak 终端按 **Ctrl+C** 退出。

### 参数说明

| 参数 | 示例 | 默认值 | 说明 |
|------|------|--------|------|
| `--model` | `--model small` | `base` | Whisper 模型大小 |
| `--lang` | `--lang zh` | `auto` | 语言代码 |
| `--key` | `--key caps_lock` | `right_alt` | 触发键 |

### 推荐触发键

| 系统 | 按键 | 参数 | 备注 |
|------|------|------|------|
| Windows | Caps Lock | `caps_lock` | 推荐，副作用最少 |
| Windows | 右 Alt | `right_alt` | 默认 |
| macOS | 右 Cmd | `right_cmd` | |
| 全平台 | F9 | `f9` | |

### 模型大小

| 模型 | 速度 | 准确度 | 内存占用 |
|------|------|--------|---------|
| tiny | ⚡⚡⚡ | ★★☆ | ~400 MB |
| base | ⚡⚡ | ★★★ | ~600 MB |
| small | ⚡ | ★★★★ | ~1.2 GB |
| medium | 🐢 | ★★★★★ | ~2.4 GB |

> **中文用户：** `--model small --lang zh` 效果最佳。

---

## 平台说明

### Windows
- 若热键无响应，请以**管理员身份**运行终端（`keyboard` 库的要求）。
- 推荐使用 **Caps Lock** 作为触发键，副作用最少。

### macOS
- 前往**系统设置 → 隐私与安全性 → 辅助功能**，为终端应用授权。

### Linux
- 可能需要 `sudo`，或将自己加入 `input` 用户组。

---

## v2 修复内容

| 问题 | 修复方案 |
|------|---------|
| Ctrl+C 无法停止脚本 | 用 `threading.Event` 事件轮询替代 `keyboard.wait()` 阻塞 |
| 强制关闭后终端快捷键错乱 | 注册 `atexit` 退出清理 + 改用 `suppress=False` 避免 OS 级钩子泄漏 |
| 文字粘贴到错误窗口 | 粘贴前等待 150ms，确保焦点切回目标窗口 |

---

## 集成为 Claude Code 技能

将 `SKILL.md` 放入 `~/.claude/skills/speak/` 后，Claude Code 会自动加载该技能。

在 Claude Code 中输入 `/speak` 即可获得安装引导和故障排除帮助。

---

## 集成到其他 AI 助手

`SKILL.md` 遵循标准 Claude 技能格式（YAML frontmatter + Markdown）。可复制到其他支持技能/规则系统的 AI 助手目录中使用。

对于使用纯 Markdown 规则文件的助手（如 `AGENTS.md`、`.cursor/rules`），去掉 frontmatter 后直接使用即可。

---

## 环境要求

- Python 3.9+
- 麦克风
- `faster-whisper` 或 `openai-whisper`（推荐 faster-whisper）

---

## 许可证

MIT
