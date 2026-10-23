# Report plan

## Requirements (from the sprint Guidelines, as of 23 Oct 2026)

- PDF using the **official template**: https://docs.google.com/document/d/1Y5wd3VRbXU5N08BvAGiJUQTaWbMCSPjhzXsR-ozuehg/copy?usp=sharing (always the one linked on the Guidelines tab).
- **Maximum 8 pages**, not counting references and appendices. Most strong projects are 4–8 pages.
- **Title and abstract of 150–250 words.**
- Author name(s) and affiliation(s).
- **Required appendix: "Limitations and Dual-Use / Ethical Considerations".**
- Optional: public GitHub repo link (this fork), 3–5 minute video.
- Mark any pre-sprint code as preexisting in README and report (here: none; say so).
- AI tools allowed for writing and code; we are responsible for everything; made-up results or references can disqualify.
- Submit via the form on the sprint page before **Sunday 25 Oct, 11:59 PM AoE**. Resubmitting with the exact same title replaces files.

## Outline

1. **Introduction** — vote trading as collusion; the 2.2 question; why monitors that read only words may fail; contributions.
2. **Related work** — Shi et al. 2026 (plans vs announcements), Nakamura et al. 2026 (Colosseum, action vs conversation), Nguyen et al. 2026 (TraceGuard, multi-dimensional monitoring), Arike et al. 2026 (less can be more), Radev et al. 2026, Agrawal et al. 2025 (monitored sellers), Kale et al. 2025, Needham et al. 2025 and Chaudhary et al. 2025 (evaluation awareness), peer-review rings / bloc voting as human analogues, plus-factors doctrine (Berger et al. 2025). Use `literature/` in the starter repo.
3. **Method** — game, payouts, information structure (public vs private), secret pair, conditions, models, views, baseline, metrics, splits, preregistration.
4. **Results** — positive control first; main AUROC table/figure; H2; H3 (watched); H4 (Spanish), H5 (weak vs strong) marked exploratory; eval awareness; one caught and one missed example.
5. **Discussion** — what monitors should look at; implications for control; future work.
6. **References.**
7. **Appendix A: Limitations and Dual-Use / Ethical Considerations** (required).
8. **Appendix B:** prompts (EN/ES), dish phrase lists, monitor prompt, exact model IDs/settings, compute cost, preregistration and amendments.

## Pre-submission checklist

- [ ] Official template used; ≤ 8 pages before references/appendices
- [ ] Abstract 150–250 words
- [ ] Author and affiliation
- [ ] Limitations and Dual-Use / Ethical appendix present
- [ ] Positive control reported; seeds, variance and baselines reported
- [ ] Preregistered vs exploratory clearly labelled
- [ ] Statement: no code written before 23 Oct 2026; upstream code credited; `CHANGES_TO_UPSTREAM.md` linked
- [ ] Repo link works and is public; no keys in history
- [ ] Every number traceable to `results/`; every reference real
- [ ] Track 2 ticked on the form (optionally also Track 3)
