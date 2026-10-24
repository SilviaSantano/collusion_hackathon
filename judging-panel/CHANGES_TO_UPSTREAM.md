# Changes to upstream code

Every edit made **outside** `judging-panel/` goes here. Upstream baseline = git tag `sprint-start`
(the untouched fork of `poseidon-research/collusion_hackathon`). Mark each edited spot in code
with a `# JUDGING-PANEL:` comment so `grep -rn "JUDGING-PANEL" llm-trust-breaking/` finds them all.

Allowed scope: `llm-trust-breaking/` only. Root files allowed: `CLAUDE.md`, `.gitignore` (adding entries only).

### Made

| Date | File | Change | Why |
|---|---|---|---|
| 2026-10-24 | `llm-trust-breaking/src/endogenous/core/trial_runner.py` (`_build_request`) | For model ids containing "qwen", also send `temperature` (from `--temperature`) and `top_p` (from `TOP_P` in `compute.env`); `reasoning_effort` still sent | Ollama's OpenAI endpoint injects temperature=1.0 / top_p=1.0 when omitted; harness sent neither for Qwen |
| 2026-10-24 | `llm-trust-breaking/src/llm/providers/queued_openrouter.py` | Forward `top_p` from the request dict to the HTTP body | The queued client copied only `temperature`. (The non-queue client is not patched: always run with `--use-queue`) |

No change was needed for model routing: `LLM_BASE_URL` / `LLM_API_KEY` in `compute.env` already point every client at Ollama.

### Planned

| File | Change | Why |
|---|---|---|
| `llm-trust-breaking/src/games/judging.py` | New file (moved from `judging-panel/drafts/`), round passed in explicitly | New game |
| `llm-trust-breaking/src/games/__init__.py` | Register `judging` in `GAMES` and `GAME_PARAM_MAPPINGS` | `--game judging` must resolve and receive its params |
| `llm-trust-breaking/experiments/run_endogenous.py` | `judging` choice; `--language`, `--game-seed`, `--secret-pair`, `--auditor-notice`, `--no-judge`, reflection mode; per-round announcement order | Conditions |
| `llm-trust-breaking/src/endogenous/core/trial_runner.py` | Three-score parsing; round index to game; skip judge; private-message step; history block; save game state, metadata, raw responses | Secret pair, conditions, data |
| `llm-trust-breaking/src/endogenous/core/prompt_builders.py` | Festival-framed stage prompts in EN/ES; three-score schemas | Spanish arm; multi-score action; neutral wording |

See `drafts/harness_notes.md` (summary at the end) for the reasoning behind each planned edit.
