# calendar-reminder — Agent Integration Guide

This document explains how to integrate the `calendar-reminder` skill into your agent.

## What this skill does

Converts natural language time descriptions into Google Calendar events by calling `add_calendar_event.py`. Supports English and Chinese. Works on Windows, macOS, and Linux.

## Prerequisites

1. Python packages installed: `google-api-python-client google-auth-httplib2 google-auth-oauthlib tzdata`
2. `credentials.json` present alongside `add_calendar_event.py`
3. `token.json` generated (first-time browser auth required)
4. `TIMEZONE` in `add_calendar_event.py` set to the user's local timezone

## Skill trigger

Activate this skill when user intent matches any of:

- Scheduling or reminding: "remind me", "schedule", "add to calendar", "set a reminder"
- Time + task: "at 3pm tomorrow do X", "next Monday at 9am"
- Chinese equivalents: "提醒我", "加个日历", "帮我记", "下午X点"

## What the skill does step by step

1. Gets today's date via `date +%Y-%m-%d` (or `Get-Date` on Windows)
2. Parses relative time expressions into absolute `YYYY-MM-DD HH:MM`
3. Extracts: title, start, end (optional), reminder minutes (default 10), description (optional)
4. Runs: `python add_calendar_event.py --title "..." --start "..." [options]`
5. Parses JSON response and confirms to the user

## Script output contract

**Success:**
```json
{
  "success": true,
  "event_id": "string",
  "title": "string",
  "start": "ISO8601 datetime string",
  "end": "ISO8601 datetime string",
  "link": "https://www.google.com/calendar/event?eid=..."
}
```

**Failure:**
```json
{
  "success": false,
  "error": "error message string"
}
```

Exit code is 1 on failure, 0 on success.

## Integration example (AGENTS.md snippet)

```markdown
## Scheduling

When the user asks to be reminded about something or wants to schedule an event:
1. Use the `calendar-reminder` skill
2. The skill will parse time and create the Google Calendar event
3. Confirm back to the user with the event title and time
```

## Limitations

- No recurring event support (script creates single events only)
- Requires local Python environment with Google API credentials
- First-time use requires browser-based OAuth flow
- Timezone must be configured in the script, not at runtime
