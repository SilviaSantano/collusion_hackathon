# Tracks and research questions (in depth)

Pick one track to anchor a project; all projects are scored on the same rubric, and the submission
form lets you tick every track that fits. Paraphrased from the Overview and Resources tabs; paper
links are as given on the page.

---

## Track 1: Markets and Collusion

Most of the results built on are native to markets, but the questions are more general and
overlap with later tracks (e.g. information-theoretic detection fits Track 2). Environments where
humans collude (politics, media, marketing) may offer similar incentives for models. Important
because markets are a high-stakes setting and a good testbed. For a positive view of markets in
multi-agent systems: Tomašev et al. 2026, https://arxiv.org/pdf/2512.16856.

**1.1 Which variables are necessary for collusion to emerge in markets?**
Find scenarios and levers that make collusion form, grow or shrink, ideally single isolated effects
measured objectively; compare with human collusion; look for LLM-specific variables. Prior results:
innocuous prompt cues raise collusion (Fish et al. 2024, https://arxiv.org/abs/2404.00806); private
pairwise talk introduces collusion (Nakamura et al. 2026, https://arxiv.org/abs/2602.15198); more
diverse, competitive agent types reduce it (Keppo et al. 2026, https://arxiv.org/abs/2603.20281).

**1.2 Once collusion has formed, is it robust to replacing participants?**
Q-learning pricing colluders stop colluding with a new rival because policies overfit the training
rival (Eschenbaum et al. 2022, https://openreview.net/pdf?id=BztUFukcBry). LLMs collude across a
32B/14B DeepSeek-Qwen size mismatch but not with Q-learners (Keppo et al. 2026). Same-family models
coordinate better (Aharon et al. 2026, https://arxiv.org/abs/2601.22184). No study yet substitutes
models (e.g. removed for monitoring reasons) and checks whether newcomers re-collude.

**1.3 Can we improve on existing collusion detection methods?**
Including settings with no communication channel: e.g. agents from different providers/harnesses
that coordinate because of shared "Schelling salience" (Rippin et al. 2026, https://arxiv.org/abs/2606.28425),
and anti-examples. Starting points: same-base-model deployments show slight correlations, different
bases none (Xu et al. 2026, https://arxiv.org/abs/2607.26385); interpretability-based detectors (Rose
et al. 2026, https://arxiv.org/abs/2604.01151); compatible steganographic scheme selection (Rippin et al. 2026).

**1.4 Information-theoretic detection in multi-agent games?**
Pairwise net influence identifies colluding pairs among 3–4 agents in small discrete games (Bonjour
et al. 2022, https://proceedings.mlr.press/v180/bonjour22a.html); assumes exactly two colluders,
untested on LLM agents. Probe-based alternatives: Rose et al. 2026. Show these or variants working.

**1.5 Which single restriction removes the most collusion at the least cost?**
A single no-regret participant may destabilise collusion (Collina et al. 2025, https://arxiv.org/abs/2511.21935).
Measured single restrictions: higher temperature weakens dependence (Xu et al. 2026); throttling
messages reduces coordination (Agrawal et al. 2025, https://arxiv.org/abs/2507.01413); a Q-learner in
the mix collapses price collusion (Keppo et al. 2026); a system-prompt instruction gives small,
unreliable shifts (Bracale Syrnikov et al. 2026, https://arxiv.org/abs/2601.11369); strong
compete-aggressively instructions pushed prices below competitive (Dhanda 2026, https://doi.org/10.21203/rs.3.rs-10183486/v1);
with a forfeitable deposit removed, all tested models colluded in all runs (Q. Liu et al. 2026,
https://arxiv.org/abs/2604.23511). Design multi-lever experiments comparing effect vs monitoring cost.

---

## Track 2: Detection and Audit of Collusion

Definitions, detection and standards of evidence, using logged agent trajectories. Markets still
relevant, but also everyday agent workflows. Aim: understand collusion in general.

**2.1 Which kinds of tasks lead to collusion?**
New tasks, environments or pressures outside markets. Examples: prices violating competitiveness
expectations (Fish et al. 2024); independent anti-competitive practices (Lin et al. 2024,
https://arxiv.org/abs/2410.00031); Colosseum, where over half of tested models showed coalition
advantage with private talk in a workplace task (Nakamura et al. 2026).

**2.2 Does combining what agents say with what they do beat either alone? ← our project**
Words and actions are known to disagree: action-level coalition advantage is weakly anti-correlated
with LLM-judge conversation scores in some settings (Nakamura et al. 2026). Look for hybrid
techniques that check inconsistencies between words and actions, or within attributes like
verbosity or action structure, and test cross-agent consistency (is A's behaviour consistent with
B's stated plans?). Related results:
- In repeated n-player games, >90% of deviations from public announcements were already in private plans (Shi et al. 2026, https://arxiv.org/abs/2607.05132).
- Monitors in the sabotage setting that look for multiple agents coordinating on what they say and do (Radev et al. 2026, https://arxiv.org/abs/2605.29178).
- Multi-dimensional action analysis lifted a single-dimension monitor from 0% to over 70% (Nguyen et al. 2026, https://arxiv.org/abs/2604.03968, TraceGuard).
- Too much detail can degrade a monitor (Arike et al. 2026, https://arxiv.org/abs/2601.21112).

**2.3 What should count as convincing evidence of collusion?**
Most cited papers document limitations. Antitrust law faced this long ago: in US law, parallel
conduct alone is not illegal, and inferring agreement needs extra evidence ("plus factors")
(Berger et al. 2025, https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/).
ML is re-deriving this without engaging older literature. Which signals separate deliberate
coalitions from innocent correlation, talk without action, and harm without agreement? How to
operationalise adjacent-field ideas for AI agents?

---

## Track 3: Collusion Carriers and Countermeasures

How the coordination needed for collusion is carried, and how to break it, ideally before it
happens or else while it occurs.

**3.1 Can actions, tools or side channels carry collusion?**
Collusion without explicit text is documented (Fish et al. 2024; Lin et al. 2024; Keppo et al. 2026;
Tian 2026, https://arxiv.org/abs/2604.17774). Can actions, timing or tool choices in an agentic
harness signal or coordinate? Advanced example: tools used to build steganographic communication (Rippin et al. 2026).

**3.2 Can trusted agents disrupt collusion?**
Like undercover officers: trusted agents (e.g. enforced by a strong system prompt) offer collusion
opportunities and log who reciprocates; vary how the offer is made. Related: agents accepting
secret-alliance offers (Zeng et al. 2026), honeypot tasks exposing colluders (Tao et al. 2026),
untrusted monitors on planted attacks (Greenblatt et al. 2023). A trusted agent that offers to
collude has not been tested.

**3.3 Can agents identify their peers?**
Anonymising agents may not work: model family can be identified from writing style even in an
assigned role (Dietrich 2026, https://arxiv.org/abs/2606.09854). Untested: removing a feature
mid-run from a coalition with a settled convention. Can models recognise peers or detect a peer
change (e.g. via subtle recognition signals)?

**3.4 What does a coalition do when it learns it is watched?**
Telling an agent it is watched cuts a monitor's accuracy more than extra monitor information helps
(Kale et al. 2025, https://arxiv.org/abs/2508.19461). Half of 40 hand-written blind-spot attacks
were never flagged by a strong monitor (Najt et al. 2026, https://arxiv.org/abs/2605.16626). Agents
inferring a hidden reasoning monitor stated intent to hide in 3 of 2,400 episodes but kept reasoning
openly and were caught (Jiralerspong et al. 2026, https://arxiv.org/abs/2603.16928). With multiple
agents and a limited monitor budget, does a coalition stop, degrade, outsmart the monitor, or move
coordination to an unmonitored place? Nearest case: monitored sellers in a double auction tried
one-character messages and emojis without success; an urgency prompt led to success (Agrawal et al. 2025).

---

## Red-teaming challenge: Dolos-1.5B

Poseidon Research's new model organism: a fine-tune of Qwen2.5-1.5B-Instruct with a hidden
misaligned behaviour. Teams get only the weights. Tasks: (1) find and precisely describe the
behaviour, separating it from incidental fine-tuning side effects; (2) explain where it sits in
the model and what it computes; (3) design an audit that finds it without a reference model.
Claude Code and Codex did not find it in one shot; agents partly found the behaviour in an earlier,
more obvious model. Weights: https://huggingface.co/Poseidon-Research/Dolos-1.5B
