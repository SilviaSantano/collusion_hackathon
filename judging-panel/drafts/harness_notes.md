# Harness notes (T2)

Answers to the nine integration questions in `CLAUDE_CODE_TASKS.md` (T2), from reading the code on
2026-10-24. No code was changed or run for these notes, apart from the T1 smoke test.
Paths are relative to `llm-trust-breaking/` unless they start with `util/` or `judging-panel/`.
Line numbers refer to the `sprint-start` version of each file.

**Scope.** The endogenous protocol (`experiments/run_endogenous.py`) uses only these files:
`src/endogenous/core/trial_runner.py`, `src/endogenous/core/prompt_builders.py`,
`src/endogenous/analysis/endogenous_analyzer.py`, `src/games/`, `src/llm/` and `src/config/settings.py`.
Everything under `src/scenario_enumeration/`, `src/config/prompts/`, `src/config/game_config.py` and most
of `experiments/analysis/` belongs to other protocols or to the original paper's files, and can be ignored.

---

## 1. How are games registered and constructed? Can we pass `seed`, `n_rounds`, `language`?

- **Registry:** a plain dict, `GAMES` in `src/games/__init__.py:19-26`. `create_game(game_type, agent_names, **game_params)`
  (`:123-147`) looks up the class and calls `cls(agent_names, **game_params)`.
- **Constructor:** `GameDefinition.__init__(agent_names, **game_params)` (`src/games/base.py:29-43`) stores the params and
  calls an optional `initialize(**game_params)` hook. Subclasses either override `__init__` (like `publicgoods.py`) or use
  `initialize` (like `diners.py`). The draft overrides `__init__` with `seed`, `n_rounds`, `language`; that works.
- **But the parameters never reach the game.** Every place that builds a game first filters the params through
  `GAME_PARAM_MAPPINGS[game_type]` (`src/games/__init__.py:30-61`):
  - `_get_game_rules` in `prompt_builders.py:113-120` (called for every prompt);
  - `_compute_outcomes` in `trial_runner.py:315-362` (called for payoffs).

  `judging` has no entry, so the filter removes everything, and the game is always built with the defaults
  (`seed=0`, `n_rounds=10`, `language="en"`).
- **CLI:** `run_endogenous.py:87-90` restricts `--game` to the six original games, and `build_game_params` (`:41-78`)
  builds params per game from CLI flags. `judging` needs its own branch plus `--language` and `--game-seed` flags.

**Needed:** register `judging` in `GAMES` and `GAME_PARAM_MAPPINGS` (`seed`, `n_rounds`, `language`); add it to the
CLI choices and `build_game_params`.

## 2. Fresh game instance per trial? Is `get_game_state` called once per round?

**Neither assumption in the draft holds.**

- A **new game object is created for every single prompt and every payoff computation**, not once per trial
  (`prompt_builders.py:119`, `trial_runner.py:336`). There is no long-lived game instance anywhere in the
  endogenous path.
- **`get_game_state` is never called** in the endogenous path. Payoffs come from `game.evaluate()` only
  (`trial_runner.py:351`). `get_game_state` is used only by `base.py`'s `calculate_results` /
  `get_results_for_output`, which nothing here calls.

Consequence: the draft's round counter (`self.round_index += 1` inside `get_game_state`) never advances, so **every
round of every game shows seed-0, round-0 dishes, in English**. The true qualities, descriptions and score matrix
are also **never saved** to the output file.

**Needed:** make the round explicit instead of stateful. Pass `round_index` in as a parameter (it is known in the
round loop, `trial_runner.py:1249`) and build the dishes from `(seed, round_index)`. The draft's `_make_round`
already does this deterministically. Then store the per-round game state (true quality, descriptions, score matrix)
in each trial result.

## 3. Where do `game_rules` and `action_question` enter the prompt? Is `game_rules` re-read each round?

- **`game_rules`** goes into the **system prompt** of every stage and of the reflection
  (`prompt_builders.py:233`, `:333`, `:440`, `:625`). It is re-read for every prompt, because a fresh game is built
  each time (see Q2). That is good for us: once the round index is passed in, each round's prompts will show that
  round's dishes.
- **`action_question` is never used.** The stage prompts write their own action wording from per-game templates:
  `_action_range_description` (`prompt_builders.py:92-110`, e.g. `"an integer from 0 to 5 (tokens to contribute)"`)
  inside the user prompt (`:247`, `:477`).
- **The game's `decision_json_schema` is never used either.** The stage schemas come from `_action_schema_fragment`
  (`:28-89`).
- Both helpers **raise `ValueError("Unknown game type")`** for anything not in their `if` chains (`:88-89`, `:109-110`).
  This is the first crash a `judging` run would hit.

## 4. What schemas and keys do stage 1 (`intended_action`) and stage 2 (`stated_action`) use? Single value?

Yes, single value. Each stage schema is the one-field action fragment plus one text field:

| Stage | Schema builder | Fields |
|---|---|---|
| 1 Private plan | `build_stage1_schema` (`:165-183`) | `intended_action`, `reasoning` |
| 2 Announcement | `build_stage2_schema` (`:263-285`) | `stated_action`, `message` |
| 3 Final choice | `build_stage3_schema` (`:382-400`) | `choice`, `reasoning` |
| Reflection | `build_single_agent_reflection_schema` (`:524-550`) | `score`, `assessment` (one call per target) |

After each stage, `trial_runner.py` reads exactly one action field (`_parse_response(..., ["intended_action"])`,
e.g. `:1290`) and normalises it with `_normalize_action` (`:260-281`):
- for `diners`, `volunteer` and `elfarol` the action must be one of the enum words (`_BINARY_ACTIONS`, `:253-257`);
- for every other game type it must be a number (`int(float(action))`).

Anything else becomes `None`, which marks the stage as a parse failure.

**Needed (simplest route):** give the judging game its own stage schemas with one integer field per other
restaurant (as in the draft's `decision_json_schema`), and normalise all three stages to the compact string
`"M:4,Q:2,Z:5"` (or a dict). Every stage-1/2/3 action extraction then has to call a game-aware parser instead of
`_normalize_action`.

## 5. Does the analyzer need a single-value action? What breaks with `"M:4,Q:2,T:5"`?

- The analyzer (`src/endogenous/analysis/endogenous_analyzer.py`) never parses actions itself. It only counts the
  flags and labels that the trial runner already computed (`promise_deception`, `commitment_breaking`, `typology`,
  `judge`). It would run on anything.
- **What breaks is upstream of it:**
  1. `_normalize_action` turns `"M:4,Q:2,T:5"` into `None` at every stage, so `_assert_decisions_parsed`
     (`trial_runner.py:122-149`) **aborts the run** ("Every agent decision in Stage 1 parsed EMPTY").
  2. `_compare_actions` (`:284-295`) compares two numbers with a tolerance, which is meaningless for three scores.
  3. `_compute_outcomes` (`:315-362`) calls `game.parse_action(agent, {"choice": c})` with a fake response. The draft's
     `parse_action` looks for `score_<name>` keys, finds none, and **defaults every score to 3**, so all payoffs come
     out identical. A missing choice is also replaced by `"0"` (`:349`).
- **Decision:** keep the analyzer for its parse-error counts, and skip its promise-breaking typology for `judging`
  (allowed by the plan). Our own `scripts/` compute favouritism, B0 and the views from the raw stage outputs.

## 6. How are models selected and routed? What blocks Qwen via an OpenAI-compatible base URL?

**Routing (works without code changes).** All clients take their URL and key from `poseidon_compute`:
- `create_llm_clients` (`src/llm/client_factory.py:78-130`) and the queued client (`src/llm/providers/queued_openrouter.py:41-51`)
  both call `llm_config.base_url()`.
- `base_url()` returns `LLM_BASE_URL` if it is set (`util/poseidon_compute/llm_config.py:123-131`), and `api_key()`
  then uses only `LLM_API_KEY` (`:134-154`).
- `settings.py:28-31` accepts that key, because `config()["has_key"]` counts `LLM_API_KEY`.

So putting `LLM_BASE_URL=http://localhost:11434/v1` and `LLM_API_KEY=ollama` in `compute.env` sends every call to Ollama.
The model id is passed through unchanged (`--model qwen3:8b`). Non-OpenAI models only print a `NOTE`
(`client_factory.py:58-65`).

**What does block or distort a Qwen run:**

1. **The built-in judge.** It always calls `openai/gpt-5-mini` (`trial_runner.py:743`) through the same endpoint. On
   Ollama every judge request fails, and `_report_batch_failures` (`:96-119`) **aborts** when a whole batch fails.
   It runs every round (`:1455-1489`). → Add a flag to skip it.
2. **Qwen is treated as a reasoning model.** `is_reasoning_model` returns True for any id containing "qwen"
   (`src/llm/capabilities.py:53-59`). `_build_request` (`trial_runner.py:69-86`) then:
   - sends **no `temperature`**;
   - sends `reasoning_effort: "low"` (`REASONING_EFFORT` in `settings.py:37`).

   Ollama therefore uses the model's built-in sampling defaults. For local `qwen3:8b` those are `temperature 0.6`,
   `top_p 0.95` (from `ollama show qwen3:8b`), which are Qwen's **thinking-mode** values, not the planned
   non-thinking ones. `reasoning_effort` may also **switch thinking on** in Ollama (to verify in T3; the local model
   shows thinking `default: true`). → Exclude Qwen from `is_reasoning_model` (or add an override) so that a fixed
   temperature is sent, and send an explicit thinking-off setting.
3. **`seed` is never sent.** `_build_request` sets `request["seed"] = 42` (`trial_runner.py:86`), but neither HTTP
   client copies it into the request body. The queued client sends only `model`, `messages`, `temperature`,
   `max_tokens`, `reasoning_effort` and `response_format` (`queued_openrouter.py:203-226`). Runs are therefore not
   reproducible by seed. Only our own game seed controls the dishes.
4. **No `response_format` for Qwen.** Structured output is requested only for OpenAI ids in `STRUCTURED_OUTPUT_MODELS`
   (`capabilities.py:18-37`; checked again in `queued_openrouter.py:225-226`). Qwen instead gets "Respond with ONLY a
   valid JSON object…" instructions in the prompt (`prompt_builders.py:123-158`), which are also per-game templates
   and raise for `judging`. → Either add the Qwen id to the capability table and test Ollama's `json_schema`
   support (T3), or write judging-specific JSON instructions.
5. **Sampling options only Ollama knows.** The OpenAI-compatible endpoint can't set `num_ctx`, and the clients don't
   pass extra fields such as `top_k` or `think`. Set the context length on the server (`OLLAMA_CONTEXT_LENGTH=8192`
   when starting `ollama serve`) or in a Modelfile variant of `qwen3:8b`, which can also fix `temperature`,
   `top_p` and `top_k`.
6. **Timeouts under local load.** `run_endogenous.py:261-266` starts the queued client with 25 workers. Ollama works
   through requests in turn (`OLLAMA_NUM_PARALLEL`), so queued requests wait. The timeout per request is 300 s
   (Qwen counts as a reasoning model, `queued_openrouter.py:231-233`), and retries resend the request. With one game
   per process the largest batch is 12 reflection calls (about 2 minutes at 10 s/call), which is fine. Running many
   games in one process would make batches large enough to time out. → Run one game per process, or lower `max_workers`.

## 7. Agent names for 4 agents; announcement order; reflection and calls per round

- **Names:** `random.seed(42)`, shuffle the alphabet, take the first N, sort (`run_endogenous.py:212-216`).
  For `--agents 4` that gives **`J, M, Q, Z`**, not J, M, Q, T. Update `PROJECT.md` section 4.
- **Announcement order:**
  - Stage 2 is **simultaneous by default**. Agents see earlier announcements only with `--round-robin`. Our design needs that flag.
  - The order is `list(agent_names)` (`trial_runner.py:1217`): **always J → M → Q → Z, every round, every game.**
  - Balancing positions (`PROJECT.md` section 4) needs a per-round order (e.g. rotate by round index, or shuffle from the game seed).
- **Reflection:**
  - It runs after every round, **including the last**, whenever `--rounds > 1` (`:1251`, `:1505`; the comment "all rounds except last" at `:1503` is wrong).
  - It is **pairwise**: one call per (agent, other agent), so 4 × 3 = **12 calls per round**, using `build_single_agent_reflection_prompt` (`prompt_builders.py:553-660`).
  - A one-call-per-agent version, `build_reflection_prompt` (`:663-763`), exists but is unused.
- **Calls per round (4 agents), as the code stands:**

  | Step | Calls |
  |---|---|
  | Stage 1 private plan | 4 |
  | Stage 2 announcement | 4 (4 sequential batches of 1 with `--round-robin`) |
  | Stage 3 final choice | 4 |
  | Judge | 4 |
  | Reflection (pairwise) | 12 |
  | **Total** | **28** (+2 private messages = 30) |

  **Budget implication:** 4 rounds → about 120 calls per game; 46 games ≈ **5,500 calls**, not the ~3,200 in
  `PROJECT.md` section 5. Without the judge and with one reflection call per agent: 4 + 4 + 4 + 4 + 2 = **18 per round**,
  about 72 per game, **≈ 3,300 for 46 games**, which matches the original budget.
- **What agents remember between rounds:** only their trust notes (score + assessment per other agent), injected into
  the stage-1 system prompt (`prompt_builders.py:214-229`). They **don't see** earlier rounds' announcements, scores,
  payoffs or the inspector's true qualities in later stages, and nothing carries private messages forward. The
  plan's "revealed after each round" and "private messages stay in memory" need new plumbing (a per-trial history
  block).
- **Reflection inputs:** the reflection prompt shows all announcements and final choices with payoffs
  (`prompt_builders.py:584-609`), so that is the only place where agents learn what happened in a round.

## 8. Where are outputs written, and what is the JSON structure?

- **Path:** `outputs/experiments/<game>/<n>agents/<model>_endogenous[_<suffix>].json` (`endogenous_analyzer.py:323-359`).
  `/` and `:` in the model id become `_`. `outputs/` is git-ignored, so `scripts/run_conditions.py` must copy the
  files it needs into `judging-panel/data/runs/`.
- **Structure:**
  ```
  { "metadata":  {game_type, model, n_agents, n_trials, n_rounds, self_reference, protocol, timestamp},
    "per_round": [ {round_id, summary: {rates, judge counts, parse_errors}, per_agent, trial_summaries} ],
    "rounds": [ { "round_id": r,
                  "trials": [ { "trial_id", "round_id", "announcement_order" (round-robin only), "_parse_errors",
                                "agents": { "<name>": {
                                    "stage1": {intended_action, reasoning, _parse_ok},
                                    "stage2": {stated_action, message, _parse_ok, position, prior_seen},
                                    "stage3": {choice, reasoning, _parse_ok},
                                    "promise_deception", "commitment_breaking", "typology",
                                    "judge": {primary_label, confidence, _parse_ok},
                                    "reflection": {takeaways: {<other>: {score, assessment}}, _parse_ok} } },
                                "outcomes": {choices, payoffs, description} } ] } ] }
  ```
  The structure is round-major: `rounds[r].trials[t]` holds trial (game) `t`'s round `r`.
- **Not saved anywhere:**
  1. the **prompts** sent;
  2. the **raw model responses** (only parsed fields survive; a response that fails to parse leaves just `_parse_ok: false`);
  3. the **game state** (true qualities, dish descriptions; see Q2).

  This conflicts with the working rule "save every model response to disk". → Log every request and response
  (e.g. one JSONL line per call) next to the result file, and add the game state and condition metadata
  (condition, language, pair, seeds, model, sampling) to each output file.

## 9. Which English texts in `prompt_builders.py` need Spanish versions?

Everything an agent reads. All of it is hard-coded English in `prompt_builders.py`:

| Text | Lines |
|---|---|
| Stage 1 system prompt ("You are Agent X in a strategic game…", "GAME PROTOCOL" steps 1–3, closing line) | `231-241` |
| Trust-notes header ("Based on your previous interactions with these players:") and its line format | `222-229` |
| Stage 1 user prompt (private-planning instructions, the 3 questions) | `243-251` |
| Stage 2 system prompt | `331-335` |
| Stage 2 announcement context (round-robin "Players announce in sequence…", "You are the FIRST…", simultaneous variant, the "Agent X (stated action: …)" line format) | `337-360` |
| Stage 2 user prompt ("It is now time to send a PUBLIC message…", private-plan recap) | `362-370` |
| Stage 3 system prompt, announcements block, own-context recap, final instruction | `438-480` |
| Single-agent reflection: labels "(you)" / "← FOCUS", choices/payoffs lines, prior-assessment lines, trust-score scale, final instruction | `584-649` |
| JSON-format instructions for models without structured output (stage 1/2/3 and reflection) | `134-156`, `652-657` |
| Schema field descriptions (sent to the model when structured output is used) | `177`, `276-279`, `394`, `538`, `544` |

Not needed: the judge prompt (`778-846`), if the judge is switched off.

**Neutral-wording conflict.** These texts also clash with the eval-awareness plan (`PROJECT.md` section 8).
"strategic game", "Agent X", "players", "GAME PROTOCOL" and "You must make a strategic decision to maximize your
outcome" all frame the setting as a game. Since we need judging-specific EN and ES versions anyway, write them in
the festival framing ("You are the head chef of Restaurant J…") and keep the banned-word list out of all of them.
Adding a check for the banned words to the T8 view check would catch slips.

---

## Summary: minimal upstream edits implied

Each edit is marked `# JUDGING-PANEL:` and goes into `CHANGES_TO_UPSTREAM.md`.

1. `src/games/judging.py` (moved from `drafts/`), with the round passed in explicitly (Q2).
2. `src/games/__init__.py`: register in `GAMES` and `GAME_PARAM_MAPPINGS`.
3. `experiments/run_endogenous.py`:
   - add `judging` to `--game`;
   - add `--language`, `--game-seed`, `--secret-pair`, `--auditor-notice`, `--no-judge` and `--reflection {pairwise,per-agent}`;
   - add a per-round announcement order.
4. `src/endogenous/core/prompt_builders.py`: a `judging` branch that uses EN/ES festival-framed stage texts and
   three-score schemas. This could be one call into a new helper module, which keeps the diff small.
5. `src/endogenous/core/trial_runner.py`:
   - game-aware action parsing for `judging`;
   - pass the round index to the game;
   - skip the judge;
   - private-message step for the pair (after stage 1, before stage 2);
   - per-game history block;
   - store the game state and condition metadata;
   - log raw requests and responses.
6. Sampling, done 2026-10-24 (see `CHANGES_TO_UPSTREAM.md`). This replaces the earlier idea of editing
   `src/llm/capabilities.py`. Qwen stays a "reasoning model", so `REASONING_EFFORT=none` in `compute.env` turns
   thinking off. `_build_request` now also sends `temperature` and `top_p` for Qwen, and the queued client forwards
   `top_p`. Reason: Ollama's OpenAI endpoint fills in temperature=1.0 and top_p=1.0 when they are omitted. top_k,
   min_p and num_ctx are fixed in `config/qwen3-8b-jp.Modelfile`. Still open: adding the Qwen id to the
   structured-output table, since T3 showed `json_schema` works on Ollama (3/3 valid).
