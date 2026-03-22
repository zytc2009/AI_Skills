---
name: calendar-reminder
description: Add Google Calendar reminders using natural language. Triggers when user says "remind me...", "add calendar event", "schedule...", or describes a time-based task. Parses time expressions in Chinese or English and calls the bundled add_calendar_event.py script to create events synced to iPhone/Android.
---

# Google Calendar Auto-Reminder

Parses natural language time descriptions and calls the bundled `scripts/add_calendar_event.py` to create Google Calendar events.

## Script Location

The script is bundled with this skill at:

```
~/.claude/skills/calendar-reminder/scripts/add_calendar_event.py
```

`credentials.json` and `token.json` must also be placed in the same `scripts/` directory.

Resolve the path at runtime:

```bash
# macOS / Linux
echo "$HOME/.claude/skills/calendar-reminder/scripts/add_calendar_event.py"

# Windows PowerShell
echo "$env:USERPROFILE\.claude\skills\calendar-reminder\scripts\add_calendar_event.py"
```

## Trigger Phrases

**English:** "Remind me to X at Y", "Schedule a meeting at 3pm tomorrow", "Add calendar event: dentist Friday 2pm"

**Chinese:** "提醒我明天下午3点开会", "周五早上9点提醒我交报告", "帮我加个日历：后天下午6点买菜"

## Execution Steps

### Step 1 — Get today's date

```bash
# macOS / Linux
date +%Y-%m-%d

# Windows
powershell Get-Date -Format yyyy-MM-dd
```

### Step 2 — Parse time to absolute datetime

| Expression | Rule |
|-----------|------|
| today / 今天 | current date |
| tomorrow / 明天 | +1 day |
| day after tomorrow / 后天 | +2 days |
| this/next Monday / 下周一 | next occurrence of that weekday |
| morning / 早上 / 上午 | 09:00 |
| noon / 中午 | 12:00 |
| afternoon / 下午 | 14:00 |
| evening / 晚上 | 19:00 |

If time has already passed today, default to tomorrow. When ambiguous, ask the user to confirm before running.

### Step 3 — Extract parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `--title` | Yes | Short event name |
| `--start` | Yes | Format: `YYYY-MM-DD HH:MM` |
| `--end` | No | Defaults to 1 hour after start |
| `--reminder` | No | Minutes before event, default 10 |
| `--description` | No | Extra notes |

Convert: "1 hour before" → `--reminder 60`

### Step 4 — Run the script

```bash
# macOS / Linux
python3 "$HOME/.claude/skills/calendar-reminder/scripts/add_calendar_event.py" \
  --title "Event title" \
  --start "YYYY-MM-DD HH:MM" \
  --reminder 10

# Windows
python "%USERPROFILE%\.claude\skills\calendar-reminder\scripts\add_calendar_event.py" ^
  --title "Event title" ^
  --start "YYYY-MM-DD HH:MM" ^
  --reminder 10
```

### Step 5 — Report result

On success:
```
✅ Calendar event created
📅 Title: [title]
🕐 Time: [start] → [end]
⏰ Reminder: [N] minutes before
🔗 View: [htmlLink]
```

On failure:
- `access_denied` → Set OAuth consent screen to "Production" or add email as test user
- `token.json` invalid → Delete `scripts/token.json` and re-run to re-authorize
- Script not found → Confirm `~/.claude/skills/calendar-reminder/scripts/` exists

## Edge Cases

**Multiple events:** Call the script once per event, sequentially.

**Recurring reminders:** Script does not support recurrence. Offer to create multiple individual events or tell user to set recurrence manually in Google Calendar.

**Timezone:** Edit line 25 of `add_calendar_event.py`:
```python
TIMEZONE = "Asia/Shanghai"  # Change to your timezone
```
Common: `Asia/Shanghai`, `Asia/Dubai`, `America/New_York`, `Europe/London`, `Asia/Tokyo`
