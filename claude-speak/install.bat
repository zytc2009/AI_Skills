@echo off
chcp 65001 >nul
echo.
echo ================================================
echo  claude-speak  —  Voice Input for Claude Code
echo ================================================
echo.

python --version >nul 2>&1 || (
    echo [ERROR] Python not found. Install Python 3.8+ from https://python.org
    pause & exit /b 1
)

echo [1/3] Installing Python dependencies...
pip install -r scripts\requirements.txt || (
    echo [ERROR] pip install failed.
    pause & exit /b 1
)

echo.
echo [2/3] Copying files...
if not exist "%USERPROFILE%\.claude\scripts" mkdir "%USERPROFILE%\.claude\scripts"
if not exist "%USERPROFILE%\.claude\skills\speak" mkdir "%USERPROFILE%\.claude\skills\speak"

copy /Y scripts\speak.py  "%USERPROFILE%\.claude\scripts\speak.py"  >nul
copy /Y SKILL.md           "%USERPROFILE%\.claude\skills\speak\SKILL.md"  >nul

echo [3/3] Done!
echo.
echo   Script : %USERPROFILE%\.claude\scripts\speak.py
echo   Skill  : %USERPROFILE%\.claude\skills\speak\SKILL.md
echo.
echo To start:
echo   python "%USERPROFILE%\.claude\scripts\speak.py" --lang zh
echo.
pause
