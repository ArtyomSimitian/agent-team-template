# Warm-up task (run this before the real build)

This is a deliberately tiny task. It checks that the team, the hooks, the budget guard and
the dashboard all work in this project. It is **not** part of the real build.

Follow the loop in CLAUDE.md, with these differences:
- Skip the researcher, and treat this whole file as a single phase ("W").
- The planner writes exactly 2 milestones to `.work/plan.md`:
  - **W1:** `warmup/rank.py` with `rank_values(values: list[float]) -> list[int]`. It
    returns the indices of the non-NaN values, sorted from smallest to largest, and ties
    keep the lower index. Tests go in `tests/test_warmup.py` and cover ties, NaN and an
    empty list.
  - **W2:** `warmup/cli.py`, so that `python -m warmup.cli 0.8 0.6 nan 0.2` prints
    `3 1 0`. Add a test for it.
- Before W1, create a minimal `pyproject.toml` with pytest as a dev dependency, if it
  doesn't exist yet.
- Commit after each milestone passes. **Don't push.**
- Finish by writing `.work/warmup_report.md`: how many subagent calls were used, how many
  fix attempts each milestone needed, and anything in CLAUDE.md or the agent files that was
  unclear.

After the warm-up, the human runs `scripts/reset-warmup.ps1`.
