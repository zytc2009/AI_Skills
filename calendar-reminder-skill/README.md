# calendar-reminder — Claude Code Skill

A Claude Code skill that lets you add Google Calendar reminders using natural language. Works with any Claude agent.

**Example:** Tell Claude → "Remind me to take medicine tomorrow at 8am" → Event created in Google Calendar → Synced to your phone.

---

## Quick Start

### 1. Install Python dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib tzdata
```

### 2. Set up Google Cloud credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project (e.g. `claude-calendar`)
3. **APIs & Services** → **Enable APIs** → search `Google Calendar API` → Enable
4. **Credentials** → **Create Credentials** → **OAuth Client ID**
5. Configure OAuth consent screen: choose **External** → fill in app name and email → Save
6. Application type: **Desktop app** → Create
7. Download the JSON file → rename to `credentials.json` → place in the same directory as `add_calendar_event.py`

> **Note on consent screen:** For personal use, you can keep the app in "Testing" mode and add your Google email as a test user instead of publishing it.

### 3. Configure your timezone

Edit line 25 in `add_calendar_event.py`:

```python
TIMEZONE = "Asia/Shanghai"   # Change to your timezone
```

Common timezones:

| Region | Timezone |
|--------|---------|
| China | `Asia/Shanghai` |
| UAE / Dubai | `Asia/Dubai` |
| UK | `Europe/London` |
| US East | `America/New_York` |
| US West | `America/Los_Angeles` |
| Japan | `Asia/Tokyo` |

### 4. First-time authorization

Run the script once to authorize:

```bash
python add_calendar_event.py --title "Test" --start "2025-01-01 10:00"
```

A browser window will open → sign in with your Google account → grant calendar access. This creates `token.json` which is reused automatically going forward.

### 5. Install the skill

Copy the entire skill folder (including the bundled script) to your Claude skills directory:

```bash
# macOS / Linux
cp -r skills/calendar-reminder ~/.claude/skills/calendar-reminder

# Windows (PowerShell)
Copy-Item -Recurse "skills\calendar-reminder" "$env:USERPROFILE\.claude\skills\calendar-reminder"
```

Then place your `credentials.json` in the scripts directory:

```bash
# macOS / Linux
cp credentials.json ~/.claude/skills/calendar-reminder/scripts/

# Windows
Copy-Item "credentials.json" "$env:USERPROFILE\.claude\skills\calendar-reminder\scripts\"
```

The skill directory structure will be:

```
~/.claude/skills/calendar-reminder/
├── SKILL.md                   ← Claude reads this
└── scripts/
    ├── add_calendar_event.py  ← bundled script
    ├── credentials.json       ← you provide this
    └── token.json             ← auto-generated after first auth
```

---

## Usage

Once installed, just talk to Claude naturally:

```
Remind me to call the doctor tomorrow at 10am
Schedule team meeting Friday 3pm, 1 hour duration
Add calendar: dentist appointment next Monday 2pm, remind me 30 minutes before
提醒我明天早上8点吃药
下周五下午3点开会，提前15分钟提醒
```

Claude will:
1. Parse the time from your message
2. Extract title, start/end time, and reminder minutes
3. Call `add_calendar_event.py` automatically
4. Confirm the event was created with a link to view it

---

## Script Reference

`add_calendar_event.py` is a standalone CLI tool — it can also be used directly without Claude:

```bash
# Basic
python add_calendar_event.py --title "Meeting" --start "2025-03-25 15:00"

# With all options
python add_calendar_event.py \
  --title "Doctor appointment" \
  --start "2025-03-25 14:00" \
  --end "2025-03-25 15:00" \
  --reminder 30 \
  --description "Bring insurance card"
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--title` | Yes | — | Event title |
| `--start` | Yes | — | Start time: `YYYY-MM-DD HH:MM` |
| `--end` | No | start + 1h | End time: `YYYY-MM-DD HH:MM` |
| `--reminder` | No | 10 | Minutes before event to send reminder |
| `--description` | No | `""` | Event notes |

**Output (JSON):**

```json
{
  "success": true,
  "event_id": "abc123xyz",
  "title": "Doctor appointment",
  "start": "2025-03-25T14:00:00+04:00",
  "end": "2025-03-25T15:00:00+04:00",
  "link": "https://www.google.com/calendar/event?eid=..."
}
```

---

## Syncing to your phone

**Android:** Install the Google Calendar app and sign in with the same Google account — events appear automatically.

**iPhone (Option A — recommended):** Download the Google Calendar app from the App Store and sign in.

**iPhone (Option B — native Calendar):** Settings → Calendar → Accounts → Add Account → Google → sign in.

---

## For Developers / Agent Builders

The skill file at `skills/calendar-reminder/SKILL.md` follows the standard Claude Code skill format and can be:

- **Dropped into any Claude Code plugin** — add it to your `skills/` directory
- **Used in AGENTS.md** — reference it in your project's agent instructions
- **Called from other skills** — invoke it as a sub-step when another skill needs to schedule something

### Using in AGENTS.md

```markdown
## Available Tools

- Use the `calendar-reminder` skill when the user asks to schedule, remind, or set a calendar event.
```

### Plugin structure

```
calendar-reminder-skill/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── skills/
│   └── calendar-reminder/
│       └── SKILL.md         # The skill Claude reads
├── add_calendar_event.py    # The script Claude calls
└── README.md                # This file
```

---

## Troubleshooting

**`access_denied` error**
→ In Google Cloud Console, set OAuth consent screen status to **"Production"**, or add your email as a test user under "Test users".

**`token.json` expired / invalid**
→ Delete `token.json` and run the script again. The browser will prompt for re-authorization.

**Event created but not visible on phone**
→ Confirm your phone is signed into the same Google account. Wait a few minutes for sync.

**Wrong time on events**
→ Check the `TIMEZONE` value in `add_calendar_event.py` matches your local timezone.

**Script not found**
→ Make sure `credentials.json` is in the same directory as `add_calendar_event.py`.

---

## Files

| File | Purpose |
|------|---------|
| `add_calendar_event.py` | CLI script that creates Google Calendar events |
| `credentials.json` | OAuth credentials from Google Cloud Console (you provide this) |
| `token.json` | Auth token, auto-generated after first login (do not delete) |
| `skills/calendar-reminder/SKILL.md` | Claude skill instructions |
| `.claude-plugin/plugin.json` | Plugin metadata for Claude Code marketplace |

---

## License

MIT
