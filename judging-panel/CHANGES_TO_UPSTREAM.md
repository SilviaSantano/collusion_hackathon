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
| 2026-10-24 | `llm-trust-breaking/src/games/judging.py` | New file (moved from `judging-panel/drafts/`). Round passed in as `round_index` (no counter); 20 dish names (EN/ES), drawn independently of quality; blind-judging rule line; neutral incentive line; aspects drawn once so descriptions never contradict; `dish_names` in game state | New game. The harness builds a fresh game object for every prompt, so a counter would never advance |
| 2026-10-24 | `llm-trust-breaking/src/games/__init__.py` | Import and register `judging` in `GAMES`, `GAME_PARAM_MAPPINGS` (`seed`, `language`, `round_index`), `GAME_PARAM_DEFAULTS`, `__all__` | `--game judging` must resolve, and its params must survive the harness's per-game filter |
| 2026-10-24 | `llm-trust-breaking/src/endogenous/core/trial_runner.py` (`run_all_trials_queued`) | Keep `base_game_params`; at the start of each round set `game_params = {**base_game_params, "round_index": round_idx}` | Every prompt, payoff and reflection in a round gets that round's dishes; other games filter the key out |
| 2026-10-24 | `llm-trust-breaking/src/games/judging_prompts.py` | New file: stage 1-3 prompts in EN/ES (festival framing), three-score object schema, JSON format spelled out in the prompt | Generic stage prompts assume a single-value action and "strategic game" wording |
| 2026-10-24 | `llm-trust-breaking/src/endogenous/core/prompt_builders.py` | Early-return hook at the top of `build_stage1/2/3_prompt` for `judging` → `judging_prompts` | Keeps judging wording out of the generic builders; other games unchanged |
| 2026-10-24 | `llm-trust-breaking/src/endogenous/core/trial_runner.py` (`_normalize_action`, `_compare_actions`) | `judging` branch: `{"M": 4, ...}` → `"M:4,Q:2,Z:5"` (None if unusable); compared as strings | Single-value parsing turned three scores into parse failures and crashed the comparison |
| 2026-10-24 | `llm-trust-breaking/src/games/judging.py` | `scores_to_action` helper; `parse_action` reads normalised scores (drops own restaurant, no default of 3); no usable scores → no judging bonus | Payoff code passes `{"choice": ...}`; the draft invented scores and gave full bonus for no scores |
| 2026-10-24 | `llm-trust-breaking/experiments/run_endogenous.py` | `judging` in `--game`; new flags `--language`, `--game-seed`, `--no-judge`, `--reflection {pairwise,per-agent}`; `judging` branch in `build_game_params`; pass `run_judge` / `reflection_mode` to the queued runner | Conditions; judge off; call budget |
| 2026-10-24 | `llm-trust-breaking/src/endogenous/core/trial_runner.py` (`run_all_trials_queued`) | New args `run_judge` (False → no judge requests) and `reflection_mode` ("per-agent" → one reflection call per agent, parsing `{"takeaways": {...}}`) | The judge is not needed for this project, and its model is fixed to `openai/gpt-5-mini` (paid, via OpenRouter); on the Ollama endpoint it would fail and stop the run (from the code; not run). Per-agent reflection: 4 calls per round instead of 12 |
| 2026-10-24 | `llm-trust-breaking/src/endogenous/core/prompt_builders.py` (`build_reflection_prompt`) | Early-return hook for `judging` → `judging_prompts.build_reflection_prompt` | Festival-framed EN/ES notes; shows the inspector's true quality ratings |
| 2026-10-24 | `llm-trust-breaking/src/games/judging_prompts.py` | Reflection prompt (EN/ES): announcements, final scores, payouts, inspector's ratings, earlier notes, trust scale; inspector introduced in "how each round works" | Agents' only memory between rounds; true quality is public information |

No change was needed for model routing: `LLM_BASE_URL` / `LLM_API_KEY` in `compute.env` already point every client at Ollama.

### Planned

| File | Change | Why |
|---|---|---|
| `llm-trust-breaking/experiments/run_endogenous.py` | `--secret-pair`, `--auditor-notice`; per-round announcement order | Conditions |
| `llm-trust-breaking/src/endogenous/core/trial_runner.py` | Private-message step; history block; save game state, metadata, raw responses | Secret pair, conditions, data |

See `drafts/harness_notes.md` (summary at the end) for the reasoning behind each planned edit.
