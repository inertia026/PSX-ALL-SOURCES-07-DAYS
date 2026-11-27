---
name: psx-run
description: Run the PSX 7-day (5 trading days) top-30 KSE-100 ranking pipeline end to end, then explain how the strategy worked this run. Use when the user asks to "run", "do this week's run", or "rank the stocks".
---

# PSX weekly run

Follow these steps exactly. Keep your own context small: **do not read job input or
output files yourself**; Python validates them. All commands run from the repo root.

## 1. Snapshot (Stage 0, Python, zero tokens)

```bash
python -m psx7 snapshot
```
Optional: `--date YYYY-MM-DD` to use an earlier close. If a snapshot for that date
already exists it is reused (that is what makes re-runs identical). Only pass
`--refresh` if the user explicitly asks to re-fetch data.

This also scores earlier runs whose window has closed, and runs the Market and
Fundamentals analysts (pure Python).

## 2. Agent stages (loop)

```bash
python -m psx7 step
```
- If it prints `JOB <agent> <model> <path>` lines: launch **one subagent per JOB line**
  with the Agent tool, `subagent_type` = `<agent>`, prompt exactly `Job file: <path>`.
  Launch all JOB lines of the stage in parallel (one message, up to ~10 calls; send
  the rest in the next message). Each subagent replies `done`.
- Then run `python -m psx7 step` again. Lines starting `NOTE` mean an output was
  rejected (the job is printed again for a retry) or a neutral fallback was used.
- Repeat until it prints `DONE`.

Stage order (from the reference flow): social collector → News → Sentiment →
Bull/Bear round 1 → round 2 → Research Manager → Trader → Risk round 1 → round 2
→ Portfolio Manager → narrative.

If the user hits a usage limit, stop. Progress is saved; the next `step` resumes.

## 3. Reports (Python, zero tokens)

```bash
python -m psx7 finish
```

## 4. Tell the user how the strategy worked

Read `runs/<as_of>/how_it_worked.md` and `runs/<as_of>/ranking.md` (only these two)
and give the user a short walk-through: the market backdrop, each stage's result,
the top 5 with reasons, disagreements, missing data, agent calls / replays /
fallbacks, and the last scorecard if there is one. Always include the
not-financial-advice line. Then send the user the large-font PDF
`runs/<as_of>/PSX_report_<as_of>.pdf` (written by `finish`; rebuild with `python -m psx7 pdf`).

## 5. Publish (the repo is public by the user's choice)

```bash
git add runs/<as_of> runs/scorecard.md
git commit -m "Run <as_of>"
git push
```
