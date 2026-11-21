"""Hook: a hard budget that code enforces, so it doesn't rely on the model obeying.

Runs before every Agent (subagent) call. Counts the calls in .work/guard_count.json and
blocks the call (exit code 2) once the cap in .work/limits.json is reached. When Claude
Code sees exit code 2 from a PreToolUse hook, it cancels the tool call and shows Claude
the message written to stderr.

To reset after a run, delete .work/guard_count.json.
"""
import json
import os
import sys
from pathlib import Path


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0

    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or ".")
    work = project / ".work"
    work.mkdir(exist_ok=True)

    limits = {"max_subagent_calls": 80}
    try:
        limits.update(json.loads((work / "limits.json").read_text(encoding="utf-8")))
    except Exception:
        pass

    count_file = work / "guard_count.json"
    try:
        count = json.loads(count_file.read_text(encoding="utf-8")).get("subagent_calls", 0)
    except Exception:
        count = 0

    cap = int(limits["max_subagent_calls"])
    if count >= cap:
        print(
            f"BUDGET REACHED: {count}/{cap} subagent calls used. Do not delegate again. "
            "Set state to BLOCKED in .work/status.json, write FINAL_REPORT.md, and stop.",
            file=sys.stderr,
        )
        return 2

    count_file.write_text(json.dumps({"subagent_calls": count + 1}), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
