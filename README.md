# Agent Team Template (Claude Code)

A ready-to-use multi-agent setup for Claude Code. A **Coordinator** (the main session) works
through a spec on its own, using six specialist subagents. Hooks log activity and enforce a
budget, and a live dashboard shows progress.

It was proven on **GreenShift** (Nov 2026): 3 phases, 12 milestones, 177 tests, a Streamlit
dashboard and 2 self-chosen features. That took about 1 h 10 min, used 54 of 90 subagent
calls, and needed no human input after the first prompt.

```
                    ┌──────────────────────────┐
     You ──task──▶  │  COORDINATOR             │ ◀── CLAUDE.md (loop, rules, stopping)
                    │  (main Claude session)   │ ◀── SPEC.md   (what to build)
                    └────────────┬─────────────┘
          delegates + gets       │       reads/writes .work/ (plan, status, log, notes)
          short reports back     │
   ┌───────────┬────────────┬────┴──────┬────────────┬────────────┐
   ▼           ▼            ▼           ▼            ▼            ▼
 planner   researcher   developer    tester      reviewer     product
 plan.md   notes/       code+tests   PASS/FAIL   APPROVE/     ROADMAP.md
                        (only one    (read-only) CHANGES      (feature
                        that edits)              (read-only)  phase only)
```

## Quick start

```powershell
cd C:\Users\simit\source\GitHub\agent-team-template
.\scripts\new-project.ps1 -Name my-project -Remote https://github.com/ArtyomSimitian/my-project.git
cd ..\my-project
```
`-Remote` is optional. Create the empty GitHub repo first (no README), and the script pushes
the first commit, which also signs you in once.

1. **Write `SPEC.md`.** Start from the template copy: ground rules, phases, and "done when"
   lines that can be checked. This is the most important step; see "Writing a good spec".
2. **Adjust `CLAUDE.md` → Project commands** if the project isn't Python. Also adjust the
   `allow` list in `.claude\settings.json` to match.
3. **Protect anything the agents must not see.** For example, to keep them out of an
   existing repo, add `"Read(//c/Users/simit/path/to/repo/**)"` to `deny`.
4. **Start the dashboard** in terminal 2: `.\scripts\start-monitor.ps1`, then open
   http://localhost:8501.
5. **Warm up** in terminal 1: run `claude`, accept the trust dialog, then type
   `Read WARMUP.md and run it as the Coordinator, following CLAUDE.md.`
   Read `.work\warmup_report.md` and fix anything it flags.
6. **Reset:** `.\scripts\reset-warmup.ps1`, then `/exit`.
7. **Build** in a **new** `claude` session. CLAUDE.md is only read when a session starts.
   Press Shift+Tab until it says auto mode, then type:
   `Read SPEC.md and build it as the Coordinator, following CLAUDE.md. Work through every
   phase without stopping to ask me anything.`
8. **When it stops:** read `FINAL_REPORT.md` (results, open questions) and `DECISIONS.md`.

## What's inside

| Path | Purpose |
|---|---|
| `CLAUDE.md` | The Coordinator's rulebook: the loop, handoff format, status rules, stopping conditions, hard rules. **Same for every project**, except the Project commands table. |
| `SPEC.template.md` | Skeleton for SPEC.md: inputs, ground rules, phases with "done when" lines, an optional "own features" phase. |
| `.claude/agents/*.md` | Six subagents. Each file sets the agent's role, its tools (least privilege) and its report format. |
| `.claude/settings.json` | Permissions (allow and deny lists) and hook wiring. |
| `.claude/hooks/guard.py` | **Hard budget.** Blocks subagent calls once the cap in `.work/limits.json` is reached. |
| `.claude/hooks/log_event.py` | Writes one line per event to `.work/events.jsonl` for the dashboard. |
| `ops/monitor.py` | Live mission-control dashboard (Streamlit, refreshes every 3 s). |
| `.work/` | Shared memory: `status.json` (the source of truth), `plan.md`, `log.md`, `notes/`, `limits.json`. |
| `fixtures/` | Offline test data. |
| `WARMUP.md` | A tiny 2-milestone task that tests the whole system. |
| `scripts/` | `new-project.ps1`, `reset-warmup.ps1`, `start-monitor.ps1`. |

## How it works

- **Hub and spoke.** Only the Coordinator delegates. Subagents can't start other subagents
  and never talk to each other, which keeps the flow predictable and easy to debug.
- **Context goes through files.** Each subagent starts with an empty context. It reads the
  plan and notes from disk, writes details to files, and returns a report of 15 lines or
  less. The Coordinator's context stays small, so it lasts through long runs.
- **Independent checks.** The tester and reviewer have no edit tools and run in parallel
  after every attempt. They can't "fix" a problem just to make it pass.
- **Ground rules make autonomy safe.** Specific, numbered rules in SPEC.md let the Reviewer
  reject work without asking you. For example, it rejected Streamlit's default telemetry
  under the "no network" rule.
- **Fix cycles have a limit.** After 3 attempts a milestone is marked BLOCKED and the run
  moves on or stops. It never loops forever.

## Safety layers

| Layer | Where | Enforced by |
|---|---|---|
| Least-privilege tools per agent | agent frontmatter `tools:` | Claude Code |
| Allow and deny command lists, protected files | `.claude/settings.json` | Claude Code |
| Subagent call budget | `guard.py` + `limits.json` | code (hook exit 2) |
| Fix-attempt cap, stopping rules, no questions mid-run | `CLAUDE.md` | the model |
| Git checkpoints: commit per milestone, push per phase | `CLAUDE.md` + allow list | both |
| Telemetry off, dashboards bound to localhost | `.streamlit/config.toml` | Streamlit |

Rules enforced by Claude Code or by code are hard limits. Rules in CLAUDE.md are followed
well, but they are instructions, not guarantees. Note that `Bash(python *)` lets the agents
run any Python, so treat the permissions as guardrails, not a sandbox.

## Writing a good spec

- Say **what** to build and the **rules**, not how. Fix interfaces (CLI, file formats) only
  where you need them.
- Make ground rules **checkable**. "Missing values stay NaN and are reported" works;
  "handle data carefully" doesn't.
- Every phase gets a **"done when"** line. A UI only counts as verified if code can check it,
  e.g. with Streamlit `AppTest` or Playwright.
- Write down the **quirks you already know**. The agents handled every quirk the GreenShift
  spec named.
- Provide **fixtures** so tests run offline, then check against live data yourself
  afterwards.
- An optional **own-features phase** with a cap lets the agents go further without going
  out of bounds.

## Budget and timing

- GreenShift used 54 calls for 12 milestones, about 4.5 per milestone including the
  planner, gates and fixes. Set `.work/limits.json` to about
  `6 × expected milestones + 10`.
- If your plan's usage limit is hit, the session pauses. Run `claude --continue` and say
  "continue from .work/status.json". The state is in files, so it can resume.

## Lessons learned (and already included here)

- Update status with the **Write tool**, not shell helpers. Shell variables trigger
  permission prompts.
- **One budget counter** (`guard_count.json`), protected by a deny rule.
- `status.json` is **git-ignored**, so each commit leaves a clean tree.
- **`.gitattributes`** prevents CRLF warnings on Windows.
- **Anchored ignores** (`/data/` instead of `data/`). The unanchored form silently left a
  `pkg/data/` package out of a commit.
- **Telemetry off and localhost only** for Streamlit.
- **Agents never stop processes they didn't start.** They report them instead. In the
  GreenShift run, the "unknown process" on port 8501 was this monitor.
- Remote tools from the Claude app can't write into `.claude/`. When Claude sets this up
  for you remotely, the files arrive in `_claude/`, and you run `Move-Item _claude .claude`
  once.

## Using other languages (e.g. C++)

Change the **Project commands** table in CLAUDE.md, for example
`cmake --build build && ctest --test-dir build`. Update the `allow` list
(`Bash(cmake *)`, `Bash(ctest *)`) and remove the Python-specific entries. The agents refer
to "the test command in CLAUDE.md", so nothing else needs to change. Replace `WARMUP.md`
with an equally tiny task in that language.
