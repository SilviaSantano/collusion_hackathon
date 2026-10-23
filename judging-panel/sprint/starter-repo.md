# The starter repo (this fork's upstream)

Upstream: https://github.com/poseidon-research/collusion_hackathon (Poseidon Research). Its README
is titled "Hackathon NY starter repo" and is the official starter linked from the sprint Resources tab.
Summarised in our own words; read the upstream README and `COMPUTE.md` for exact commands.

## What it contains

Ten research codebases on LLM agents and collusion, bundled so a team can clone once. Every project
runs on a normal laptop without a GPU, calling models through a hosted provider configured once at
the repo root. The starter provides working harnesses, not results.

| Folder | Paper (original code) | Sprint questions | Note |
|---|---|---|---|
| `algorithmic-pricing-llms/` | Romero, Sauer & Peist 2025 (master's project) extending Fish et al. 2024 | 1.1 | 2–5 LLM firms, 300-round Calvano pricing game; default model Mistral-Large-Instruct-2411 (Nebius) |
| `llm-cartel/` | Riemer et al. 2026 (ICML position paper) | 1.1, 1.2 | Bertrand duopoly/triopoly, 19 prompt variants, monitoring notices, LLM judges, checkpoint branching; GPU steering scripts optional |
| `focal-points/` | Aharon et al. 2026 | 1.2, 1.3, 3.3 | Schelling coordination tasks vs human data; benign control |
| `llm-agent-collusion/` | Agrawal et al. 2025 | 1.3, 1.4, 1.5, 3.4 | Continuous double auction; seller chat, overseer, caps, pressure; adds `--overseer_sample_fraction`; default 3/3/15 |
| `colosseum/` | Nakamura et al. 2026 | 2.1, 2.3, 3.1 | Tool-calling agent teams (Jira, hospital); preflight script; 2.1 conditions as configs |
| **`llm-trust-breaking/`** | **Shi et al. 2026, *When Agents Lie* (arXiv 2607.05132)** | **2.2**, 3.3 | **Our base.** 10-round strategic games with private plans and public commitments; currently OpenAI-family models only; each trial-round = 4 calls per agent plus pairwise reflection (full documented run ~8,000 calls) |
| `collusive-llm-agents/` | Lin et al. 2024 | 3.1 | Bertrand and Cournot notebooks |
| `llm-agent-collusion-2/` | Zeng & Rudzicz 2026 (Voluntary Collusion) | 3.2 | Liar's Bar and Cleanup with secret alliances, via API |
| `steganographic-collusion/` | Tailor 2025 (*Audit the Whisper*), building on Mathew et al. 2024 | 2.3 | ColludeBench, calibrated detectors; scripted configs need no key; large (raw transcripts kept as data) |
| `trace-guard/` | Nguyen et al. 2026 (TraceGuard) | 2.2 | Single-agent 5-dimension monitor; needs Docker; ~10-min smoke test |
| `redteaming/` | Poseidon model organism Dolos-1.5B | Red-teaming | Local, no key |
| `util/` | — | all | Shared compute layer `poseidon_compute` |
| `literature/` | — | all | ~230 tagged papers, PDF download script, `definitions/` comparing how 139 papers define collusion |

## Setup (upstream)

- Prerequisites: `uv` (also fetches the right Python), Docker only for `trace-guard`, a Nebius or OpenRouter key, optionally a Modal account (`pip install modal && modal setup`).
- `cp compute.env.example compute.env`, add `NEBIUS_API_KEY` and/or `OPENROUTER_API_KEY`.
- `./setup.sh` installs everything; `./setup.sh llm-trust-breaking` installs only our folder.
- One entry point runs any experiment with a chosen model: `poseidon-run --model <id> -- <command>`; routes Nebius → OpenRouter → Modal, and stops with a clear error rather than substituting a model.
- Experiments import `from poseidon_compute import make_client, resolve_model`.

## llm-trust-breaking smoke test (upstream README)

```
cd llm-trust-breaking && uv sync
uv run python experiments/run_endogenous.py --game diners --agents 2 --trials 1 --rounds 1 \
  --model openai/gpt-4o-mini --use-queue      # ~10 calls
```

## Upstream guidance worth remembering

- Decide early which kind of collusion the project studies (see `literature/definitions/`); it decides what can be measured and what counts as evidence. For us: an **explicit, communicated agreement** (vote trading via a private channel), detected from public behaviour.
- Upstream says you do not have to use any starter code or even a cited paper.
- Earlier question numbering differed; the README has an old→new mapping (old 2.3 = current 2.2).
