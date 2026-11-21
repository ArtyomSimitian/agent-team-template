"""Hook: append one short line per Claude Code event to .work/events.jsonl.

Claude Code runs this script on the events listed in .claude/settings.json and sends the
event as JSON on stdin. It records only short summaries, never file contents. The
monitoring dashboard (ops/monitor.py) reads the log.

Standard library only, so it works with any Python on the machine.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def short(value, limit=160):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def summarize(event):
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    if tool in ("Agent", "Task"):
        return f"delegate -> {tool_input.get('subagent_type', '?')}: {short(tool_input.get('description', ''), 80)}"
    if tool in ("Bash", "PowerShell"):
        return short(tool_input.get("command", ""))
    if tool in ("Edit", "Write", "Read", "MultiEdit"):
        return short(tool_input.get("file_path", ""))
    if event.get("hook_event_name") in ("SubagentStop", "Stop"):
        return short(event.get("last_assistant_message", ""), 200)
    return short(tool_input) if tool_input else ""


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0  # never break the session because of logging

    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or ".")
    log_path = project / ".work" / "events.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event.get("hook_event_name", ""),
        "agent": event.get("agent_type") or "coordinator",
        "agent_id": event.get("agent_id", ""),
        "tool": event.get("tool_name", ""),
        "summary": summarize(event),
    }
    response = event.get("tool_response")
    if isinstance(response, dict) and response.get("is_error"):
        record["error"] = True

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
