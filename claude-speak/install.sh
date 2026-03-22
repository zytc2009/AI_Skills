#!/usr/bin/env bash
set -e

echo ""
echo "================================================"
echo " claude-speak  —  Voice Input for Claude Code"
echo "================================================"
echo ""

command -v python3 >/dev/null 2>&1 || {
    echo "[ERROR] python3 not found. Install Python 3.8+."
    exit 1
}

echo "[1/3] Installing Python dependencies..."
pip3 install -r scripts/requirements.txt

echo ""
echo "[2/3] Copying files..."
mkdir -p ~/.claude/scripts ~/.claude/skills/speak

cp scripts/speak.py  ~/.claude/scripts/speak.py
cp SKILL.md          ~/.claude/skills/speak/SKILL.md
chmod +x ~/.claude/scripts/speak.py

echo "[3/3] Done!"
echo ""
echo "  Script : ~/.claude/scripts/speak.py"
echo "  Skill  : ~/.claude/skills/speak/SKILL.md"
echo ""
echo "To start:"
echo "  python3 ~/.claude/scripts/speak.py --lang zh"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS: Grant Accessibility permission to your terminal at"
    echo "       System Settings → Privacy & Security → Accessibility"
    echo ""
fi
