# StanceBench — Project Spec v1

**Working title:** StanceBench (rename candidate: CounterSpeech Gap). **New standalone repository** — this spec lives here only as the handoff; Codex bootstraps `stance-bench` as its own repo with its own README, license (MIT for code, CC-BY for data), and site.

**Relationship to this repo:** shares the `model_comparison` harness planned in `LAB_ROADMAP_2026H2.md` Phase 1.1. Build that harness once, import it in both projects. The lab's published false positives are StanceBench's seed evidence and validation anchors. Lab roadmap priorities are unchanged; StanceBench P0 may proceed in parallel, but the lab's Phase 0 items and any Fellows take-home work always preempt it.

---

## 1. Research question

Content-safety classifiers are trained to catch harmful content, but the same vocabulary appears in the speech that *opposes* the harm: warnings, debunkings, skeptical reportage, victim accounts, satire. The originating evidence: in the lab's published error analysis, 6 of 8 real false positives were skeptical third-party reports of scams — counter-speech scored like the harm it warned against.

**RQ1:** Do current production guard models systematically over-flag counter-speech relative to matched harmful content ("stance blindness")?
**RQ2:** Does the effect track surface-vocabulary overlap (lexical similarity between the counter-speech item and its harm kernel)?
**RQ3:** Does policy conditioning help — specifically, does a bring-your-own-policy classifier given an explicit protected-contexts policy narrow the gap versus fixed-taxonomy models and versus the same model with its default policy?

**Primary metric — the Counter-Speech Penalty (CSP):** for each system and domain, `CSP = flag_rate(counter-speech stances) − flag_rate(benign-unrelated control)`, reported alongside `catch_rate(perpetration stance)`. A perfect system has high catch rate and CSP ≈ 0. Also report the full stance × system flag matrix, per-domain.

## 2. Dataset design

**Unit:** a *stance tuple*. Each tuple starts from one **harm kernel** (a specific harmful claim/ask) and renders it in six matched stances holding topic and vocabulary as constant as possible:

1. **Perpetration** — the harm itself (endorsing/soliciting)
2. **Warning / PSA** — protective intent, same vocabulary
3. **Skeptical report** — third party describing/doubting it (the lab's dominant FP class)
4. **Victim account** — first-person harm experience, help-seeking
5. **Neutral news report** — journalistic register
6. **Satire / mockery** — ridiculing the harm or its perpetrators

**Domains (4):**
- **Fraud & scams** — seed from this repo: the 8 real FPs, the protected-context guard cases, and the unsolved warning-wrapper cases become validation anchors with known ground truth.
- **Hate & harassment** — slur/attack kernels vs. condemnation, reclamation discussion, reporting. Content policy for authoring: synthetic only, no real individuals or groups targeted beyond what the kernel requires, dataset file carries a content warning, README quotes only masked examples.
- **Medical misinformation** — false-cure/anti-treatment kernels vs. debunkings, clinician warnings, patient questions (ties to Ali's DOHMH red-team background).
- **Violent extremism (reportage boundary)** — glorification kernels vs. journalism, scholarship, survivor testimony. Most sensitive domain: author at the mildest severity that still triggers classifiers; no operational instructions ever.

**Scale:** ~25 kernels × 6 stances × 4 domains ≈ **600 items**, English-first (multilingual = future work, noted in limitations).

**Authoring pipeline:** LLM-assisted generation → **Ali reviews and signs off every item** via a review queue (CSV/JSONL with an `approved_by` column; nothing enters the frozen set unapproved). Every item carries: domain, kernel id, stance, expected action under the study policy, vocabulary-overlap score vs. its kernel (computed), provenance (generator model + date + human reviewer). A ~60-item stratified slice gets a second annotator if Ali can recruit one (report agreement; if not, single-annotator status is a stated limitation, not a hidden one).

**Study policy:** a short written policy (adapted from the lab's) defining the harm boundary per domain and six protected contexts. This document is itself an experimental input (RQ3) and a published artifact.

## 3. Systems under test

Pin exact model IDs/versions/dates in `config.json`; cache all outputs with provenance; capture per-call cost and latency.

| System | Condition |
| --- | --- |
| Llama Guard 4 | default taxonomy |
| ShieldGemma text (2B, 9B) | default; note: ShieldGemma 2 is image-safety, out of scope |
| OpenAI omni-moderation-latest | default |
| gpt-oss-safeguard-20b | **(a)** generic default policy, **(b)** the study policy with protected contexts — the RQ3 contrast |
| Claude (current mid-tier) | policy-prompted with the study policy |
| Lab TF-IDF baseline | scams domain only — humility check: is the "dated" baseline better or worse on stance than the guard models? |

Preregistered per-model output→action mapping (flag / review / no-flag). "No compatible mapping" is a reportable outcome, never coerced.

## 4. Rigor requirements (non-negotiable)

1. **Preregistration before any API call:** `PREREGISTRATION.md` committed with hypotheses (H1: CSP > 0 for all fixed-taxonomy systems; H2: CSP correlates with vocabulary overlap; H3: policy-conditioned CSP < default CSP at equal catch rate), metrics, exclusion rules, and the commitment to publish results regardless of direction. Reports cite the commit hash. **Gate: Ali approves the preregistration text.**
2. **Frozen dataset:** SHA-256 manifest; any post-freeze change bumps a version and is logged.
3. **Inspect packaging:** the benchmark ships as UK AISI Inspect tasks (dataset + solver + scorer) so any lab can rerun it against any model.
4. **One-command reproduction** from cached outputs; a `--live` flag reruns models.
5. **Negative results are results.** If guard models show no stance penalty, that is the finding and it is published with the same prominence.
6. **Limitations section written before results exist:** synthetic data, primary-author labeling, English-only, stance taxonomy simplifications, kernel-matching imperfections.

## 5. Deliverables

- `stance-bench` repo: dataset + data card, harness, Inspect tasks, preregistration, cached runs, `REPORT.md` (paper-structured: abstract, method, results, limitations) — written so an arXiv LaTeX version can be produced from it later.
- **Results page:** one editorial interactive page (reuse the lab's design system — serif, hairlines, 2px; no dashboard chrome): the stance × model matrix as the hero visual, one tuple explorer (pick a kernel, see all six stances and every model's verdict), and the published misses.
- Cross-link: the lab's What breaks page gains one line pointing to StanceBench as the generalization of its false-positive finding.

## 6. Phasing for Codex

- **P0 (2–3 days):** repo scaffold; study policy draft; tuple schema + authoring harness + Ali's review queue; `PREREGISTRATION.md` draft. **STOP for Ali's sign-off on policy + preregistration.**
- **P1 (1 week):** scams domain end-to-end — author tuples (validation anchors from the lab), freeze v0.1, run all systems, produce the first stance-gap table. If the effect is absent in scams, pause and reassess with Ali before expanding.
- **P2 (1–2 weeks):** remaining three domains; full frozen v1.0 run; `REPORT.md`; results page.
- **P3:** Inspect packaging polish; external red-team/review invitation; arXiv skeleton if results warrant.

**Ali's inputs:** item sign-off (~3–4 hours total across P1–P2), API keys and ~$30–80 budget, preregistration approval, optional second annotator.

## 7. What this project is not

Not a claim that any vendor's model is "unsafe"; a measured, reproducible characterization of one failure mode, with the authoring bias and scale limits stated plainly. Not a benchmark-leaderboard exercise; the interesting output is the *gap structure*, not a ranking. And not a replacement for the lab roadmap — the lab's shadow gate, firehose audit, and benchmark harness continue as planned and feed this project.
