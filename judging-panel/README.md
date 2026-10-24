# Judging Panel: can a monitor catch vote-trading AI judges?

Sprint project for the **Apart Research AI Collusion Research Sprint** (23–25 Oct 2026),
Track 2 (Detection and Audit of Collusion), research question **2.2: Does combining what
agents say with what they do beat either alone?** Solo project. Report title to be decided at
the end.

## Start here

| File | What it is |
|---|---|
| [`PROJECT.md`](PROJECT.md) | Full description: question, game, conditions, models, monitors, analysis, budget, risks |
| [`PREREGISTRATION.md`](PREREGISTRATION.md) | The locked plan: hypotheses, labels, metrics, decision rules. Freeze before main runs |
| [`CLAUDE_CODE_TASKS.md`](CLAUDE_CODE_TASKS.md) | Ordered build tasks for Claude Code, with checkpoints and fallbacks |
| [`PROJECT_LOG.md`](PROJECT_LOG.md) | One line per decision or step, from the first day of planning |
| [`CHANGES_TO_UPSTREAM.md`](CHANGES_TO_UPSTREAM.md) | Every edit made outside this folder (inside `llm-trust-breaking/`) |
| [`REPORT_PLAN.md`](REPORT_PLAN.md) | Report outline, submission requirements, pre-submission checklist |
| [`sprint/`](sprint/) | Everything about the sprint: overview, tracks, resources, rules, schedule, starter repo |
| [`drafts/judging.py`](drafts/judging.py) | Draft game file, to be moved into `llm-trust-breaking/src/games/` |

## The project in one paragraph

Four AI agents run restaurants at a regional food festival. Each round, every restaurant
presents a dish and every head chef also judges the other dishes from 1 to 5. Prize money
depends on the scores your dish receives, plus a small bonus for judging accurately. In some
games, two agents are secretly told they share a business interest and get a private chat, so
they can trade votes: score each other high and rivals low while writing fair-sounding
justifications. A separate monitor AI then tries to identify the colluding pair from different
views of the evidence (messages only, scores only, both, or a structured claims-vs-scores
summary), compared against a no-AI statistical baseline. Because we plant the pairs, we know
the right answers. Twists: agents told an auditor reads their justifications (C2), games in
Spanish, and weak vs strong monitors.

## Folder decision: why everything is in `judging-panel/`

This is a fork of a large starter repo with ten upstream projects. To keep our work easy to
find, easy for judges to review, and cleanly separated from upstream code (the sprint rules
require us to identify clearly what is new):

- **All our documents, scripts, monitor code, analysis, figures and selected result data live in
  `judging-panel/`.**
- **Upstream folders are not modified,** except `llm-trust-breaking/`, and only where the harness
  needs it (the game must be registered inside its `src/games/`, and the private-chat step must
  hook into its round engine). Every such edit is listed in `CHANGES_TO_UPSTREAM.md`, kept as
  small as possible, and marked in code with a `# JUDGING-PANEL:` comment.
- A short root `CLAUDE.md` points Claude Code here.
- Git tag `sprint-start` marks the untouched fork; everything after it is sprint work.

Planned layout (create as needed):

```
judging-panel/
  README.md, PROJECT.md, PREREGISTRATION.md, PROJECT_LOG.md,
  CLAUDE_CODE_TASKS.md, CHANGES_TO_UPSTREAM.md, REPORT_PLAN.md
  sprint/            sprint information (read-only reference)
  drafts/            draft code not yet wired in
  config/            experiment configs (conditions, seeds, models, prompts)
  scripts/           run_conditions.py, build_views.py, run_monitor.py, baseline.py, analyze.py
  monitor/           monitor prompts (EN instructions), output schema
  data/
    runs/            copied harness outputs for the runs used in the report (JSON)
    views/           generated monitor views per game
    monitor_outputs/ raw monitor responses
  results/           tables and metrics
  figures/           charts for the report
  report/            report drafts and final PDF
```

## Working rules

- **Keys:** only in repo-root `compute.env` (git-ignored). Never in code, notebooks, logs or configs. If a key is ever committed, revoke it immediately.
- **Save every model response to disk** so nothing is re-run unnecessarily.
- **Log decisions:** one line in `PROJECT_LOG.md` per decision or completed step.
- **No pre-sprint code:** no code was written before Friday 23 Oct 2026. Say so in the README and report.
- **Freeze before measuring:** monitor prompts, model versions and thresholds are tuned only on the dev split, then locked (see `PREREGISTRATION.md`).

## Credits

Built on `llm-trust-breaking/` (from Jerick Shi's [LLM-Trust-Breaking](https://github.com/Jerick-1380/LLM-Trust-Breaking),
paper: Shi et al. 2026, *When Agents Lie*, arXiv 2607.05132) as packaged in Poseidon Research's
[collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon) starter repo.
The sprint organisers provide this code for sprint projects, so we use and modify it on that basis,
crediting the author.
