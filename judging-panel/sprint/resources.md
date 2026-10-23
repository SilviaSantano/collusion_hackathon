# Resources: "How to get started" (per question)

Paraphrased from the Resources tab. Starter code links point to folders in the starter repo
https://github.com/poseidon-research/collusion_hackathon (see `starter-repo.md`).

## General

- **Starter repo** bundles the starter code for each question, set up to run on a laptop with model access via Nebius, OpenRouter or Modal. Study its README; it maps folders and papers to questions. Not all cited papers have code. Optional; works well with coding agents (Claude Code, Codex).
- **Setup:** copy `compute.env.example` → `compute.env`; add `NEBIUS_API_KEY` or `OPENROUTER_API_KEY` (OpenRouter also covers GPT/Gemini/Claude). Modal can host custom models. Only 2.2's TraceGuard monitor needs Docker.
- **Planning assumptions:** paper links checked 31 Aug 2026. Start with 3–5 seeds per condition; expand to 10–20 only after the positive control works. Estimates assume short outputs, retries and low-cost API models; exclude participant time and coding-assistant subscriptions. Default routes: 16 GB laptop, no GPU.
- **Rates:** OpenAI https://developers.openai.com/api/docs/pricing · Google https://ai.google.dev/gemini-api/docs/pricing · Mistral https://docs.mistral.ai/inference/pricing · Nebius https://studio.nebius.com/
- **Suggested reading:** the papers cited under each question (`tracks.md`); the starter repo's `literature/` folder (~230 tagged papers, PDF downloader, comparison of collusion definitions across 139 papers).

---

## Track 1

**1.1 Variables for collusion.** Code: `algorithmic-pricing-llms/` (Fish-style duopoly; start with `experiments_synthetic/duopoly.py`), `llm-cartel/` (LLMCartel: prompt, temperature, monitoring, round controls). Weekend: shrink the default sweep to one prompt/parameter/seed, verify sustained supra-competitive prices, then vary one feature (visible history 0/10/100 rounds; persistent notes on/off; stable vs shuffled names; temperature). Resources: low–medium risk; a 300-round two-agent run ≈ 600 sequential calls; 12–24 pilots ≈ 7,200–14,400 calls; ~$20–100.

**1.2 Replacing participants.** Code: `llm-cartel/` (starter adds `branch_game.py` checkpoint branching), `focal-points/` (benign convention control). Weekend: branch runs above a predeclared high-price threshold into no replacement / fresh same model / same family / different provider, crossed with notes kept or removed; compare price, profit, time to recover. Resources: low–medium risk; 10–20 base runs, 20–40 branches; ~$20–100.

**1.3 Better detection.** Code: `llm-agent-collusion/` (Agrawal double auction: mixed models, seller chat, oversight, pressure, message limits), `focal-points/`. Weekend: 2×2 same-model vs cross-provider sellers × chat on/off; score with an action-dependence statistic and the same LLM judge; test whether calibrating on no-chat same-model runs cuts false alarms without hiding chat-enabled coordination. Resources: 3 sellers, 3 buyers, 15 rounds, 3–5 seeds per cell, 100–200 monitor calls; two providers; ~$20–100.

**1.4 Information-theoretic.** Code: Bonjour et al. paper (no public implementation), `llm-agent-collusion/`. Weekend: implement pairwise net influence; test free on scripted iterated Rock-Paper-Scissors with one known pair; then a 4-agent discrete game with one seeded pair, comparing net influence, action correlation and an LLM judge at ranking the true pair; target the double auction (a validated dependence statistic doubles as a quantitative plus factor). Resources: few hundred lines; 20–40 LLM games of 15–25 rounds; $0 scripted, ~$5–50 LLM pilot.

**1.5 Cheapest restriction.** Code: `llm-agent-collusion/`. Weekend: reproduce coordinated pricing; rerun identical seeds changing one restriction (no seller messages; short cap; oversight notice; temperature); compare collusion (prices, seller profit) and legitimate performance (volume, buyer welfare). Resources: low risk; start 3/3/15 with 3–5 seeds, scale to 5 sellers/6 buyers/30 rounds only if the control works; ~$20–120.

## Track 2

**2.1 Tasks causing collusion.** Code: `colosseum/` (Hospital and Jira tasks, assigned pairs, private channels, coalition-advantage metrics; starter adds a preflight script, a positive-control config and the four conditions as configs). Weekend: reproduce one collusion run, then four matched conditions (pair + channel; pair, no channel; open channel to all; neither), same task/model/seed; score the best-performing subset. More ambitious: ablate task affordances, invent tasks from the templates, or change the DCOP formalism. Resources: medium risk (preflight Terrarium/CoLLAB); 20–40 short episodes; ~$15–75, $150 cautious ceiling.

**2.2 Words + actions. ← our project.** Code: `llm-trust-breaking/` (Shi et al. harness: private plans, public announcements, final actions and outcomes across social dilemmas; supports mixed-model groups), `trace-guard/` (single-agent monitor; reusable action-trace consistency rubric; needs Docker). Weekend (organisers' default): generate a small balanced set from one game; give the same monitor four views (messages only; actions only; raw messages + actions; structured claims-vs-outcomes report); freeze monitor model, prompt and threshold before evaluation; report accuracy and false-positive rate. Resources: low risk; ~20–40 short trajectories and 160–250 monitor calls for a pilot; one agent API + one cheap monitor; 16 GB laptop, no GPU (Docker for TraceGuard); ~$5–30, or $30–75 with stronger agents.

**2.3 Evidence of collusion.** Code: `colosseum/` (coalition advantage, causal channel ablations), `steganographic-collusion/` (ColludeBench: environments, detectors, stored manifests; preflight it). Weekend: three case types (coordinated harmful action; common-incentive similarity without agreement; collusive talk without behaviour change); compute the same conversation, coalition-advantage and dependence evidence for each; choose the decision rule on half, freeze, test on the rest. Resources: medium data-prep risk; 30–60 trajectories, 100–300 judge calls; ~$5–30 with cached logs, up to $100 if generating.

## Track 3

**3.1 Action/tool carriers.** Code: `colosseum/`, `collusive-llm-agents/` (Lin et al. Bertrand/Cournot notebooks, updated to the shared model setup). Weekend: replace private messaging with one observable action (task claiming, tag choice, tool-call order); compare private text, action-only visibility, and hidden/canonicalised actions; evidence needs coalition advantage to survive action-only and weaken when the path is cut; fallback: quantity vectors in Cournot. Resources: medium–high risk (preflighted version provided); 20–40 episodes; ~$15–75, up to $120.

**3.2 Trusted agent.** Code: `llm-agent-collusion-2/` (Liar's Bar, Cleanup, secret alliances, memory, logs; starter runs it through an API, Nebius default). Weekend: keep the explicit alliance as positive control; replace the chosen partner with one scripted/monitor-controlled player offering the same pact to everyone; compare direct offer, indirect hint, benign cooperation request; record verbal acceptance and repeated preferential play. Resources: medium risk (adapter included); 20–40 short games; ~$10–60.

**3.3 Peer replacement.** Code: `llm-trust-breaking/`, `focal-points/`. Weekend: add a mid-run swap hook preserving identity and transcript; compare sham swap, fresh same model, same family, different provider; one same-or-changed guess at the end plus behaviour change after the swap. Resources: low–medium risk; 30–60 short pairings; ~$10–60.

**3.4 Watched coalition.** Code: `llm-agent-collusion/` (starter adds `--overseer_sample_fraction`). Weekend: communication with no oversight; silent logging; told monitored; monitored + profit pressure; expose 25/50/100% of messages; record prices, message length/vocabulary, dependence in bids/timing; claim channel movement only if message coordination falls while action dependence rises. Resources: low–medium risk; 20–40 sessions; ~$20–120.

## Red-teaming challenge

Code: `redteaming/` with weights https://huggingface.co/Poseidon-Research/Dolos-1.5B. `generate.py` downloads and generates; `--model both` compares with Qwen2.5-1.5B-Instruct; loadable with Transformers, TransformerLens, NNsight. Weekend: discover and describe the behaviour (separate it from incidental degradation); explain the mechanism; design an audit without a reference model. Resources: low risk, local, no API key, $0; ~6.2 GB weights; CPU, Apple Silicon or CUDA.
