# Agent team — quick start

This project was created from **agent-team-template**. This file is a one-page cheat
sheet. You can delete it once you no longer need it; nothing depends on it.
Full guide: https://github.com/ArtyomSimitian/agent-team-template

## 1. Prepare (about 15 min)

- [ ] **Write `SPEC.md`.** Fill in every `<...>`: inputs, ground rules that can be checked,
      phases with "done when" lines. Then delete `SPEC.template.md`.
- [ ] **Put offline test data** in `fixtures/` and list it under "Inputs" in the spec.
- [ ] **Not Python?** Edit **Project commands** in `CLAUDE.md` and the `allow` list in
      `.claude\settings.json`.
- [ ] **Protect folders** the agents must not read: add
      `"Read(//c/Users/simit/path/**)"` to `deny` in `.claude\settings.json`.
- [ ] **Set the budget** in `.work\limits.json`: about `6 × expected milestones + 10`.
- [ ] Commit: `git add -A; git commit -m "Spec"`

## 2. Warm up (about 10 min)

**Terminal 2:**
```powershell
.\scripts\start-monitor.ps1        # dashboard at http://localhost:8501
```
**Terminal 1:**
```powershell
claude                             # accept the trust dialog the first time
```
Paste this prompt:
```
Read WARMUP.md and run it as the Coordinator, following CLAUDE.md.
```
Check `.work\warmup_report.md` and fix anything it flags. Then `/exit` and run:
```powershell
.\scripts\reset-warmup.ps1
```

## 3. Build

Start a **new** session, because CLAUDE.md is only read when a session starts:
```powershell
claude
```
Press **Shift+Tab** until it says **auto mode**, then paste:
```
Read SPEC.md and build it as the Coordinator, following CLAUDE.md. Work through every phase without stopping to ask me anything.
```
Watch the dashboard. Commits are pushed after each phase gate (if a remote is set).

## 4. When it stops

- **`FINAL_REPORT.md`:** results, what failed, numbered open questions for you.
- **`DECISIONS.md`:** every judgment call the agents made.
- **`.work\log.md`:** one line per milestone.
- **Check anything live yourself.** Tests were offline and network calls were mocked, so
  run the real thing once.

## Troubleshooting

| What you see | What to do |
|---|---|
| Permission prompt during a run | Choose Yes. If it keeps coming up, add that command to `allow` in `.claude\settings.json`. |
| `BUDGET REACHED` | Working as designed. Read FINAL_REPORT.md, raise `.work\limits.json` if needed, then run `claude --continue` and say "continue from .work/status.json". |
| Usage limit hit / session paused | After it resets: `claude --continue`, then "continue from .work/status.json". |
| Dashboard shows "No events yet" | Hooks aren't running. Check that `python` works in this terminal and that the trust dialog was accepted. |
| Port 8501 in use | That's probably the monitor already running. Run the project's own app with `--server.port 8502`. |
| Agents asked to stop an "unknown process" | They report it instead of acting. Check whether it's your monitor or app. |
| Remote tools can't write `.claude\` | Expected. Files arrive in `_claude\`; run `Move-Item _claude .claude`. |

## Reset everything for another run
```powershell
Remove-Item .work\guard_count.json, .work\events.jsonl -ErrorAction SilentlyContinue
Copy-Item .work\status.initial.json .work\status.json -Force
```
