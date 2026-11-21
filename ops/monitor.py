"""Mission control: a live view of the agent team.

Run it in a second terminal while the agents work:
    scripts\\start-monitor.ps1   (or: .venv\\Scripts\\python -m streamlit run ops/monitor.py --server.address localhost)

Reads two files and refreshes every 3 seconds:
  .work/status.json   - the Coordinator's own account of where it is (the source of truth)
  .work/events.jsonl  - every hook event (detail; hooks can occasionally miss an event)
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / ".work"

st.set_page_config(page_title=f"{ROOT.name} agents", layout="wide")
st.title(f"{ROOT.name}: agent mission control")


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_events():
    path = WORK / "events.jsonl"
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return pd.DataFrame(rows)


@st.fragment(run_every="3s")
def live():
    status = read_json(WORK / "status.json", {})
    limits = read_json(WORK / "limits.json", {"max_subagent_calls": 80})
    used = read_json(WORK / "guard_count.json", {}).get("subagent_calls", 0)
    cap = limits.get("max_subagent_calls", 80)

    state = status.get("state", "NOT_STARTED")
    colors = {"RUNNING": "blue", "DONE": "green", "BLOCKED": "red", "NEEDS_HUMAN": "orange"}
    st.markdown(f"### State: :{colors.get(state, 'gray')}[{state}]")

    c = st.columns(5)
    c[0].metric("Phase", status.get("phase", "–"))
    c[1].metric("Milestone", f"{status.get('milestone', '–')}")
    c[2].metric("Step / attempt", f"{status.get('step', '–')} / {status.get('attempt', '–')}")
    tests = status.get("tests", {})
    c[3].metric("Tests", f"{tests.get('passed', 0)} pass", f"-{tests.get('failed', 0)} fail" if tests.get("failed") else None)
    c[4].metric("Subagent budget", f"{used} / {cap}")
    st.progress(min(used / cap, 1.0) if cap else 0.0)

    st.caption(f"Working on: {status.get('milestone_title', '')} · active agent: "
               f"**{status.get('agent', '–')}** · last result: {status.get('last_result', '–')} · "
               f"updated {status.get('updated_utc', '–')}")

    left, right = st.columns([1, 2])
    with left:
        st.subheader("Milestones")
        ms = status.get("milestones", {})
        if ms:
            st.dataframe(pd.DataFrame({"milestone": list(ms), "status": list(ms.values())}),
                         hide_index=True, width="stretch")
        else:
            st.write("No plan yet.")
        log = WORK / "log.md"
        if log.exists():
            st.subheader("Milestone log")
            st.markdown(log.read_text(encoding="utf-8")[-3000:])

    with right:
        events = read_events()
        st.subheader("Activity")
        if events.empty:
            st.write("No events yet.")
        else:
            delegations = events[events["summary"].str.startswith("delegate ->", na=False)]
            if not delegations.empty:
                who = delegations["summary"].str.extract(r"delegate -> ([\w-]+)")[0]
                st.bar_chart(who.value_counts(), horizontal=True)
            show = events.tail(40).iloc[::-1][["ts", "event", "agent", "tool", "summary"]]
            st.dataframe(show, hide_index=True, width="stretch", height=520)


live()
