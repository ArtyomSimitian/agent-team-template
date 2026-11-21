# Agent Team Template (Claude Code)

**What this is:** a reusable setup that lets Claude Code build a project on its own. You
write a spec. A **Coordinator** (the main Claude session) splits it into milestones and
hands each one to specialist agents: planner, researcher, developer, tester, reviewer and
product. They write the code, test it, review it, fix it, commit it and push it, without
you approving each step. A live dashboard shows what they're doing.

**When to use it:** for projects you can describe clearly up front, can test automatically,
and that take more than a few prompts. Examples: a data pipeline, a CLI tool, a small app
with a dashboard, or a library with tests. It's not worth it for quick one-off scripts or
for exploratory work where you don't know yet what you want.

**Track record:** it built **GreenShift** (Nov 2026) in one run: 3 phases, 12 milestones,
177 tests, a Streamlit dashboard and 2 features the agents chose themselves. That took
about 1 h 10 min, used 54 of 90 subagent calls, and needed no input after the first prompt.

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

---

## One-time setup

**You need:** Windows with [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
(signed in), [Git for Windows](https://git-scm.com/download/win) and Python 3.11+. Check them
in PowerShell:
```powershell
claude --version; git --version; python --version
```

**Get the template.** The recommended location is `$HOME\source\GitHub`. `$HOME` is your
user folder, e.g. `C:\Users\<you>`. New projects are created next to the template, so pick
the folder where you keep your repos.
```powershell
mkdir $HOME\source\GitHub -Force; cd $HOME\source\GitHub
git clone https://github.com/ArtyomSimitian/agent-team-template.git
```
To keep your own improvements, use **Use this template** or **Fork** on GitHub first, and
clone your copy instead.

**Allow local scripts** (once per PC, only if PowerShell says scripts are disabled):
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Placeholders in this guide:** replace `<your-username>` with your GitHub username and
`<you>` with your Windows user name. Commands that use `$HOME` work as they are.

---

## Quick start: a new project in 5 steps

The template folder stays where it is, and you never edit it for a project.

**1. Create the project**
```powershell
cd $HOME\source\GitHub\agent-team-template
.\scripts\new-project.ps1 -Name my-project -Remote https://github.com/<your-username>/my-project.git
cd ..\my-project
```
If you want it on GitHub, create the empty repo there first. Otherwise leave out `-Remote`.

**2. Describe what to build.** Fill in `SPEC.md`: what it does, the rules it must follow, and
a "done when" line for each phase. Put any test data in `fixtures\`. The better the spec,
the better the result.

**3. Warm up (about 10 minutes)**
- Terminal 2: `.\scripts\start-monitor.ps1`, then open http://localhost:8501
- Terminal 1: `claude`, accept the trust dialog, then type:
  `Read WARMUP.md and run it as the Coordinator, following CLAUDE.md.`
- When it's done: `/exit`, then `.\scripts\reset-warmup.ps1`

**4. Build.** Start a **new** `claude` session, press Shift+Tab until it says auto mode, then
type:
`Read SPEC.md and build it as the Coordinator, following CLAUDE.md. Work through every phase without stopping to ask me anything.`
Then let it run and watch the dashboard.

**5. Check the result.** Read `FINAL_REPORT.md`, which has the results and the questions it
left for you. Then try the real thing yourself once, since the tests only used offline
data.

Each new project also has an `AGENT_TEAM.md` with this checklist plus troubleshooting. The
sections below explain everything in more detail.

---

## How to use it

### The idea: this folder is a factory

**Don't clone or edit this repo for each project.** Keep it in one place
(recommended: `$HOME\source\GitHub\agent-team-template`) and run its script. The script
creates each new project as a **separate folder with its own git history**, next to this
one.

```
source\GitHub\
├── agent-team-template\   ← the factory (you only edit it to improve the template)
├── my-new-project\        ← created by the script, where the agents work
└── another-project\       ← created by the script
```

### Start a new project (2 commands)

```powershell
# 1. (Optional) create an EMPTY repo on https://github.com/new (no README), then:
cd $HOME\source\GitHub\agent-team-template
.\scripts\new-project.ps1 -Name my-new-project -Remote https://github.com/<your-username>/my-new-project.git

# 2. Go to the new project and follow its checklist
cd ..\my-new-project
```
Leave out `-Remote` to keep the project local only. Then open **`AGENT_TEAM.md`** in the new
project. It's a one-page checklist: write the spec → warm up → reset → build → read the
report.

### The scripts

| Script | Run it from | What it does |
|---|---|---|
| `scripts\new-project.ps1 -Name <name> [-Remote <url>] [-Packages a,b]` | this template folder | Creates `..\<name>`. Copies the agent team in, creates `SPEC.md` from the template, resets the status file, creates `.venv` and installs `pytest`, `streamlit`, `pandas` (plus any `-Packages`), runs `git init` and makes the first commit. With `-Remote`, it also links GitHub and pushes. It never overwrites an existing folder. |
| `scripts\start-monitor.ps1` | the new project | Starts the live agent dashboard at http://localhost:8501 (reachable only from your PC). |
| `scripts\reset-warmup.ps1` | the new project | After the warm-up: deletes the warm-up files, resets the status and the budget counter, and commits. Run it before the real build. |

If PowerShell says *"running scripts is disabled"*, run this once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### The workflow in each new project (also in its `AGENT_TEAM.md`)

1. **Write `SPEC.md`.** This is the most important step; see "Writing a good spec" below.
   Add offline test data to `fixtures\`. If the project isn't Python, edit **Project
   commands** in `CLAUDE.md`.
2. **Protect anything the agents must not see.** Add `"Read(//c/Users/<you>/path/to/folder/**)"` to
   `deny` in `.claude\settings.json`.
3. **Terminal 2:** `.\scripts\start-monitor.ps1`
4. **Terminal 1, warm-up:** run `claude`, accept the trust dialog, then type
   `Read WARMUP.md and run it as the Coordinator, following CLAUDE.md.`
   Read `.work\warmup_report.md`, then `/exit` and run `.\scripts\reset-warmup.ps1`.
5. **Build** in a **new** `claude` session. Press Shift+Tab until it says auto mode, then
   type:
   `Read SPEC.md and build it as the Coordinator, following CLAUDE.md. Work through every
   phase without stopping to ask me anything.`
6. **Read** `FINAL_REPORT.md` and `DECISIONS.md`, then check anything that touches live
   data yourself.

### Other situations

- **Improving the template:** edit the files *here*, then commit and push. New projects get
  the change. Existing projects keep the version they started with.
- **Another computer (e.g. Mac):** `git clone https://github.com/ArtyomSimitian/agent-team-template.git`
  once and use that clone as the factory there. The `.ps1` scripts are Windows-only. On
  macOS, copy the folder (minus `.git`) by hand, create the venv, and change the paths
  under "Project commands" from `.venv/Scripts/python` to `.venv/bin/python`.
- **Starting from GitHub's "Use this template" button** also works, but then you have to do
  the script's steps yourself (venv, `SPEC.md`, status reset). The script is easier.

---

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
| `AGENT_TEAM.md` | A one-page quick start copied into every new project. Delete it when you're done with it. |
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
