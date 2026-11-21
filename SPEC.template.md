# <Project name> — Build Specification

<!--
How to use this file: copy it to SPEC.md and fill in every <...>. Delete these comments.

What makes a spec work for autonomous agents:
- Say WHAT and the RULES, not HOW. Leave the module layout and names to the agents
  unless you need a fixed interface (CLI commands, file formats, an API).
- Ground rules are what let the Reviewer reject bad work without asking you. Make them
  specific enough that someone could check them.
- Every phase needs a "done when" line that can be verified. Agents can't look at a screen,
  so a UI only counts as verified if code can check it (e.g. headless tests).
- Write down the quirks you already know (odd data, edge cases) as requirements. Otherwise
  the agents rediscover them the hard way, or never do.
- Give the agents offline test data in fixtures/ whenever the project depends on outside
  data.
-->

You are building **<name>**: <one or two sentences on what it does and for whom>.

This spec says *what* to build and the rules it must follow. The internal design is up to
you, except where an interface is fixed below.

The work has these phases, done in order. Don't start a phase until the one before it
passes its "done when" checks.

## Inputs
<!-- Files the researcher should study, e.g. fixtures/, sample inputs, an API doc. Or "None". -->
- `fixtures/<...>`: <what it is>

## 0. Ground rules (apply to every phase)
1. <Correctness rule, e.g. "The model never sees test labels during training.">
2. <Data rule, e.g. "Never invent data: missing values stay missing and get reported.">
3. <Honesty and labeling rule, e.g. "Every metric shows its exact name and units.">
4. Reproducible: random processes use fixed seeds, and every run saves its inputs and
   outputs.
5. Modular: <list the parts> don't depend on each other's internals.
6. Offline tests: the test suite passes without internet access. Mock network calls.
7. <Language/version, platform> (e.g. Python 3.11+, runs on Windows).

---

## Phase 1 — <Core>
### 1.1 <Component>
- <Requirement>
- <Known quirk to handle>

### 1.x Interface
<!-- Fixed CLI commands / API endpoints / file formats, if you need them. -->
```
<command examples>
```

**Phase 1 is done when:** <specific checks, e.g. "all tests pass offline, the worked
example passes, `<command>` on the fixtures produces <output>">.

---

## Phase 2 — <Interface / dashboard / integration>
Required:
- <Feature>
- <Feature>

Testing: <how it is verified headlessly>.

**Phase 2 is done when:** <checks>.

---

## Phase 3 — Own features (at most <N>)
<!-- Optional. Delete this phase if you don't want the agents choosing features. -->
The Product agent proposes features in `ROADMAP.md`, and the Reviewer approves or rejects
each one before any code is written. A feature is allowed only if it:
- <constraints, e.g. works offline, needs no accounts, keeps earlier tests passing, has its
  own tests>;
- fits in one milestone.

Ideas you may pick from or replace:
- <idea>

Not allowed: <explicit no-go list>.

---

## Deliverables
- <package>/, `tests/`, project config, `README.md`
- `DECISIONS.md`, `ROADMAP.md` (if Phase 3 is used), `FINAL_REPORT.md`
