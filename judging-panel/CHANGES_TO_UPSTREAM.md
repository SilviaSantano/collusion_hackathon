# Changes to upstream code

Every edit made **outside** `judging-panel/` goes here. Upstream baseline = git tag `sprint-start`
(the untouched fork of `poseidon-research/collusion_hackathon`). Mark each edited spot in code
with a `# JUDGING-PANEL:` comment so `grep -rn "JUDGING-PANEL" llm-trust-breaking/` finds them all.

Allowed scope: `llm-trust-breaking/` only. Root files allowed: `CLAUDE.md`, `.gitignore` (adding entries only).

| Date | File | Change | Why |
|---|---|---|---|
| _example_ | `llm-trust-breaking/src/games/judging.py` | New file (moved from `judging-panel/drafts/`) | New game |
| | `llm-trust-breaking/src/games/__init__.py` (or registry) | Register `judging` | `--game judging` must resolve |
| | model routing (`src/llm/client_factory.py` / shared `util/`) | Allow OpenAI-compatible base URL for Qwen (Ollama / Modal) | Harness noted as OpenAI-family only |
| | `src/endogenous/core/trial_runner.py` | Private-message step for the secret pair; C2 notice; game seed/language passthrough | Secret pair + conditions |
| | `src/endogenous/core/prompt_builders.py` | Stage prompts in EN/ES; three-score stage-1/2 formats | Spanish arm; multi-score action |

Replace the example rows with real ones as edits are made.
