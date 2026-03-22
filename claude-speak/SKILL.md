---
name: speak
description: 当用户想要语音输入或询问 speak / voice / 语音 相关内容时使用。引导用户完成安装、配置和故障排除。
---

# speak — 按键说话，自动转写

按住触发键录音，松开后由本地 Whisper 转写，文字自动粘贴到当前窗口。
无需 API Key，完全离线，支持 Windows / macOS / Linux。

## 环境要求

- Python 3.9+
- 麦克风
- 磁盘空间约 400 MB～1.2 GB（首次运行时自动下载模型）

## 安装

```bash
# 方式 A — 一键安装
# Windows:
install.bat
# macOS / Linux:
chmod +x install.sh && ./install.sh

# 方式 B — 手动安装
pip install faster-whisper sounddevice keyboard pyperclip numpy

# 复制 speak.py 到脚本目录：
#   Windows:    %USERPROFILE%\.claude\scripts\speak.py
#   macOS/Linux: ~/.claude/scripts/speak.py

# 安装 Claude Code 技能：
mkdir -p ~/.claude/skills/speak
cp SKILL.md ~/.claude/skills/speak/SKILL.md
```

> **Windows**：若热键无响应，请以**管理员身份**运行终端。
> **macOS**：在**系统设置 → 隐私与安全性 → 辅助功能**中为终端授权。

## 使用方法

在**独立终端**中运行，保持与 Claude Code 并行：

```bash
# 推荐配置（中文，小模型，Caps Lock 触发）
python ~/.claude/scripts/speak.py --model small --lang zh --key caps_lock

# 英文，默认触发键（右 Alt）
python ~/.claude/scripts/speak.py --lang en
```

**步骤：**
1. 在独立终端保持 speak.py 运行
2. 点击 Claude Code 输入框使其获得焦点
3. 按住触发键 → 看到 🔴 录音中...
4. 说话
5. 松开 → 🔄 转写中... → ✅ 自动粘贴
6. 若自动粘贴失败，文字已复制到剪贴板，可手动 Ctrl+V

按 **Ctrl+C** 退出。

## 参数说明

| 参数 | 可选值 | 默认值 | 说明 |
|------|--------|--------|------|
| `--model` | tiny / base / small / medium / large-v3 | `base` | 模型大小 |
| `--lang` | zh / en / ja / auto | `auto` | 语言 |
| `--key` | caps_lock / right_alt / f9 / … | `right_alt` | 触发键，推荐 `caps_lock` |

**模型选择：**

| 模型 | 速度 | 准确度 | 内存 |
|------|------|--------|------|
| `tiny` | 最快 | 低 | ~400 MB |
| `base` | 快 | 中 | ~600 MB |
| `small` | 中 | **中文最佳** | ~1.2 GB |
| `medium` | 慢 | 最高 | ~2.4 GB |

## 故障排除

| 现象 | 解决方案 |
|------|---------|
| 按键没有反应 | Windows 以管理员身份运行 / macOS 授予辅助功能权限 |
| Ctrl+C 无法停止 | 更新到最新版 speak.py（v2 已修复） |
| 转写结果为空 | 检查麦克风权限；尝试 `--model small` |
| 中文识别差 | 使用 `--lang zh --model small` |
| 自动粘贴无效 | 文字已打印到终端并复制到剪贴板，手动粘贴即可 |
| 强制关闭后终端快捷键错乱 | 更新到最新版 speak.py（v2 已修复）；已错乱则重启终端 |

## 注意事项

- **`suppress=False` 模式**：触发键不在 OS 层拦截，`caps_lock` 仍会切换大写锁定状态。若不希望如此，改用 `right_alt` 或 `f9`。
- **焦点要求**：自动粘贴会向当前焦点窗口发送 Ctrl+V，松开触发键前请确保 Claude Code 输入框已获得焦点。
- **首次运行**：Whisper 模型会在首次运行时自动下载（约 400 MB～1.2 GB，取决于所选模型）。
