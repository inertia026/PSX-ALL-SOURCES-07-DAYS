# PSX-ALL-SOURCES-07-DAYS

Ranks the top 30 KSE-100 stocks (free-float market cap) by 5-trading-day growth
potential using the 12-role agent flow in PLAN.md (Analysts → Bull/Bear →
Research Manager → Trader → Risk debate → Portfolio Manager).

- To run: use the `psx-run` skill. Never start a run unless the user asks.
- Principles: **deterministic** and **token-light**. Code decides, Claude explains.
  Numbers, levels, ranking and reports are Python. Agents only fill fixed JSON forms.
- Do not read job files during a run; Python validates them.
- Changing anything in `.claude/agents/*.md` or `prompt_version` invalidates the
  replay cache for that role (intended).
- After editing `models:` in `config/settings.yaml`, run `python -m psx7 sync-agents`.
- Tests: `python -m pytest -q` (offline, uses fixtures).
- Before changing market-signal points or thresholds, run `python -m psx7 backtest`;
  keep only rules it supports.
