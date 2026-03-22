#!/usr/bin/env python3
"""
Google Calendar 自动添加提醒脚本
用法: python add_calendar_event.py --title "标题" --start "2024-12-25 15:00" --end "2024-12-25 16:00" [--reminder 10] [--description "描述"]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Windows 终端 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Dubai"  # UTC+4，阿联酋时间

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def parse_datetime(dt_str):
    """解析时间字符串，支持多种格式"""
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间格式: {dt_str}，请使用 YYYY-MM-DD HH:MM 格式")


def add_event(title, start_str, end_str=None, reminder_minutes=10, description=""):
    tz = ZoneInfo(TIMEZONE)
    start_dt = parse_datetime(start_str).replace(tzinfo=tz)

    if end_str:
        end_dt = parse_datetime(end_str).replace(tzinfo=tz)
    else:
        end_dt = start_dt + timedelta(hours=1)

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": TIMEZONE,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": reminder_minutes},
            ],
        },
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return created


def main():
    parser = argparse.ArgumentParser(description="添加 Google Calendar 事件")
    parser.add_argument("--title", required=True, help="事件标题")
    parser.add_argument("--start", required=True, help="开始时间 (YYYY-MM-DD HH:MM)")
    parser.add_argument("--end", default=None, help="结束时间 (YYYY-MM-DD HH:MM)，默认开始后1小时")
    parser.add_argument("--reminder", type=int, default=10, help="提前提醒分钟数，默认10分钟")
    parser.add_argument("--description", default="", help="事件描述")

    args = parser.parse_args()

    try:
        event = add_event(
            title=args.title,
            start_str=args.start,
            end_str=args.end,
            reminder_minutes=args.reminder,
            description=args.description,
        )
        print(json.dumps({
            "success": True,
            "event_id": event["id"],
            "title": event["summary"],
            "start": event["start"]["dateTime"],
            "end": event["end"]["dateTime"],
            "link": event.get("htmlLink", ""),
        }, ensure_ascii=False, indent=2))
    except HttpError as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
