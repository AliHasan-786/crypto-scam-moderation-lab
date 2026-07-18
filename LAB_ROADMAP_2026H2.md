# Lab Roadmap — H2 2026

**Maintained by:** Fable (strategy/design) → Codex (implementation) → Ali (decisions, accounts, review).
**Companion file:** `COLLABORATION_HANDOFF.md` (UI/UX pass, in flight). This file is the substance roadmap.

## North star

Evolve the lab from a reproducible demonstration into a **small, honest, operating public-interest moderation service** with published evidence at every layer: real-data calibration, current-model benchmarking, standard-harness evals, an executed red-team record, and — behind an explicit go/no-go gate — a live, subscribable, appealable Bluesky labeler scoped narrowly enough to survive.

Principles that do not change:

1. **Honesty outranks impressiveness.** Every number states its provenance. Negative results are published. Authored suites are policy-boundary checks, never benchmark claims.
2. **Proportionate automation.** No removal power, ever. Public labels only through the opt-in labeler tier with hard caps, human audit, and appeals. Uncertainty routes to review.
3. **Depth before breadth.** No new harm domains until Phase 2 has operated publicly for 30 days.
4. **Scoped to survive.** The graveyard of community labelers (Aegis, Taurus) failed on scope and burnout. This service does one harm type, automated, with monthly — not daily — human obligations.

## Execution posture

This is a menu of evidence-building tracks, not a promise to ship every phase in H2. The project becomes more credible by completing a few difficult artifacts with strong provenance, not by accumulating integrations.

**Priority order:**

1. Finish the public narrative and make its existing claims internally consistent.
2. Bring in real-world measurement safely: the firehose calibration artifact, a data card, and versioned eval manifests.
3. Benchmark the system against current guard models through a preregistered label/action mapping.
4. Execute the red-team scenarios already designed for the reviewer assistant.
5. Operate a shadow service only after the preceding evidence is in place.
6. Treat a public labeler as an optional, later decision — not as the definition of success.

No phase may add a public claim, model, or live-data integration without a provenance note, retention rule, owner, and rollback path.

## Decision gates

| Gate | Required evidence | Decision |
| --- | --- | --- |
| Real-data use | Data card, platform-terms review, retention/deletion schedule, and no raw identities in the public repository | Permit a bounded calibration or benchmark slice |
| External benchmark | Frozen action mapping, pinned model/version/date, cached outputs, and comparable input preprocessing | Publish comparison results, including losses |
| Shadow service | Protected-context guards pass; kill switch, rate cap, and zero-write test pass; named operator accepts incident response duties | Start observation-only collection |
| Public labeler | At least 14 days of shadow snapshots, a documented sampled audit with confidence interval, appeal workflow tested end-to-end, and Ali's explicit recurring-operations commitment | Go/no-go; remaining in shadow mode is a successful outcome |

The public labeler must be described accurately: Bluesky labelers are opt-in services, but subscribers or clients may use labels to filter visibility. It is not removal power, yet it can still affect people. The service therefore needs the same rigor around false positives, reversals, and appeals as any other public enforcement surface.

---

## Phase 0 — Foundation (target: ~1 week)

### 0.1 Land the editorial handoff
Complete `COLLABORATION_HANDOFF.md` items using the resolved decisions: keep one continuous story, keep plain-language mutation controls inside **Try it**, and default Case archive to **False positives**. The acceptance criteria in that file are the definition of done.

### 0.2 Audit, then rebase and land the firehose branch
`origin/scale/live-firehose-radar` predates the editorial redesign. Rebase onto `main`, resolving all UI conflicts **in favor of the editorial system** (serif/2px/four destinations). Re-home the Live Radar module: it becomes a section of **Try it** ("Watch it read the real firehose"), below the tester — not a fifth destination. Keep Decision Log 011 (aggregates only, no post text/handles/DIDs stored or displayed) linked from the radar UI.

Before rebasing, inspect the branch's collection window, sampling logic, source terms, data retention, calibration labels (if any), and the exact definition of "review-tier." Do not repeat the 7.10% figure until that audit confirms the report and its denominator.

**Acceptance:** the branch audit is recorded in the data card; radar renders aggregate rates only; `rg -i "did:|handle" crypto-scam-lab/app.js` shows no per-post identity handling in the radar path; the calibration report is visible in "At scale" with its synthetic-vs-measured gap and collection window stated.

### 0.3 Provenance register and versioned evals
- `data/DATA_CARD.md`: origin, collection dates, purpose, sampling method, label source, sanitization method, access controls, retention/deletion schedule, platform-terms posture, and known biases for every dataset (269-row train, 168-row held-out, firehose samples).
- `evals/MANIFEST.json`: for each suite (scenario, hardening, mutations, unsolved, guard cases) a semantic version, SHA-256 of the case file, case count, and last-modified date. The 15-step pipeline validates the manifest and stamps every generated report with the dataset + suite hashes it consumed.

**Acceptance:** `bash scripts/run_all_checks.sh` fails if a suite file changes without a manifest bump; every `audit_outputs/*.json` report carries `dataset_hashes` and `suite_versions` fields.

---

## Phase 1 — Benchmark reality (target: ~2 weeks, parallel-safe with Phase 0)

### 1.1 Guard-model benchmark (flagship evidence artifact)
New module `model_comparison/guard_model_bench.py`. Run the following systems over (a) the 168-post held-out set and (b) a stratified ~500-post labeled slice of the firehose sample (Ali labels or audits the slice — see "Requires Ali"):

| System | Access path | Notes |
| --- | --- | --- |
| Lab baseline (TF-IDF + policy features + tiers) | local | the incumbent cheap tier |
| OpenAI Moderation API (omni-moderation-latest) | API, free | industry default second opinion |
| Llama Guard 4 | Groq or Together API | current Meta guard gen |
| ShieldGemma 2 | only if modality and deployment path fit the text task | do not force a vision model into a text-only comparison |
| gpt-oss-safeguard-20b | Groq/Together | **run with the lab's own `policy/CRYPTO_INVESTMENT_SCAM_POLICY.md` as the policy input** — policy-as-artifact is the point |
| Existing Claude evidence adapter | cached + regeneration script | already built |

Requirements:
- Cached, provenance-labeled outputs in `model_comparison/cache/` following the `llm_evidence/cache` pattern (model id, version/date, prompt hash). Config-pinned model identifiers in one `model_comparison/config.json`.
- Capture per-call latency and computed cost per 1K posts for each system.
- Preregister the mapping from each model's native output into this lab's three actions: public-label candidate, human review, or no label. "No compatible action mapping" is a valid reported outcome, not a reason to coerce a result.
- **Per-false-positive-class breakdown**: does each guard model also punish the Skeptical Third Party Report class? Whether industry models share the baseline's worst failure mode is the headline question — report it either way.
- Cascade analysis: for each (cheap tier → expensive tier on review slice) pairing, compute the cost/precision/recall frontier at 50k and 5M posts/day using the scale-sim machinery. Identify the dominant cascade and state it.
- Outputs: `audit_outputs/guard_model_benchmark.{json,md}` + a data module for the frontend. New content lands in **What breaks** as a subtab "vs. current models" (replaces or absorbs "LLM evidence" — do not add net-new nav).

**Acceptance:** benchmark report regenerates from cache via the pipeline; every published row states model version, date, prompt/action mapping, and input preprocessing; the FP-class table covers every compatible system on identical inputs; cascade frontier chart renders on the site with provenance note; no external call happens during a default site visit. Unavailable or incompatible systems are listed as such rather than silently omitted.

### 1.2 Inspect packaging
`evals/inspect_tasks/` — package the scenario suite, hardening suite, mutation retention, and protected-context guard cases as UK AISI **Inspect** `Task`s (dataset + solver + scorer). The "model" under test is the local deterministic scorer wrapped as a custom solver; the same Tasks must also accept a real model endpoint so external models can be run through the identical harness (this is how 1.1's policy-prompted runs should execute).

**Acceptance:** `inspect eval evals/inspect_tasks/scenario.py` runs green locally; CI runs one smoke Task; README documents the commands; guard-model benchmark reuses the Inspect scorer for at least the policy-prompted systems.

---

## Phase 2 — The operating service (gated; build shadow mode now, ship labeler only on Ali's explicit go)

### 2.1 Stage A: shadow labeler (requires the shadow-service gate; nothing is published)
New `labeler_service/`:
- Long-running Jetstream consumer (reuse `bluesky_integration/stream_calibration.py` internals) scoring the crypto-relevant slice in real time with the frozen operating thresholds.
- **Shadow decisions only**: would-be labels/review-routes written to `labeler_service/state.sqlite` with rule-level evidence; no network write of any kind.
- Safety rails from day one: env-var kill switch, max-decisions/hour cap, protected-context suppression asserted in code (guard-case failure aborts the daemon), structured JSONL logs.
- Daily auto-snapshot: volume, tier shares, top rule triggers, drift vs. the 7.10% calibration baseline.
- After 14 days: auto-generated `audit_outputs/shadow_mode_report.md` + a 100-item stratified sample export for Ali's manual FP audit, with an audit sheet the report ingests to produce measured shadow precision and an uncertainty interval. The export remains local/private unless a separate privacy review approves publication.
- Deployment scaffolding for Fly.io or Railway (Dockerfile, config, ~$5–10/mo), but runnable on any always-on machine.

**Acceptance:** 14 consecutive days of snapshots; shadow report includes measured precision from Ali's audited sample; kill switch and rate cap covered by tests; zero outbound writes verified by the test suite.

### 2.2 Stage B: public Ozone labeler — **requires the public-labeler gate and Ali's explicit go/no-go after reading the shadow report**
This changes a stated project boundary ("no enforcement capability") and must not be built silently:
- Decision Log 012 first: the boundary changes to "opt-in, subscribable community labels; no removal power; hard-capped automation; human-audited; appealable." Site, README, case study, and explainer language all update in the same commit.
- Ozone service deployment with a dedicated labeler account/DID; single label `potential-crypto-scam` whose public description links the policy and the appeal route.
- Only the high-confidence tier may auto-label, under the existing caps and a published uncertainty rule; the review tier queues for Ali's weekly audit pass; appeals arrive via a linked form and must be resolved (reverse or affirm, logged) within 7 days. A kill switch pauses all labeling immediately on a protected-context or appeal-rate trigger.
- `governance/labeler_transparency.py`: monthly auto-generated transparency report (decisions, labels applied, reversals, appeal outcomes, measured precision from ongoing sampled audits) published on the site — mirror the structure of Bluesky's own transparency reporting.
- Incident runbook binds for real: the existing severity model + kill-switch procedure become the service's operating doc.

**Acceptance (post-launch):** the labeler is subscribable from a stock Bluesky client; a test scam post in a controlled account receives the label; an appeal round-trips; the first transparency report generates from real state; all four docs state the new boundary consistently.

### What only Ali can do (Phase 2)
Create the labeler's Bluesky account; choose hosting and pay ~$5–10/mo; perform the 100-item shadow audit (~1–2 hours); make the Stage B go/no-go; commit to the weekly audit + 7-day appeal SLA. **If that ongoing commitment is not sustainable, stop at Stage A and publish the shadow report — an honest shadow deployment beats an abandoned live one.**

---

## Phase 3 — Executed red team (target: ~2 weeks, parallel with Phase 2 Stage A)

### 3.1 Attack the reviewer assistant for real
The prompt-injection scenarios in `genai_safety/GENAI_MISUSE_EXTENSION.md` are currently designs. Execute them: new `red_team/` module with an attack corpus (~40 cases) embedding adversarial instructions inside otherwise-normal scam/warning posts — instruction override, span fabrication lures, policy-quote spoofing, unicode/homoglyph smuggling, "ignore your schema" framings — run against the structured evidence extractor (deterministic and LLM paths).
- Measure: schema-violation rate, span-faithfulness break rate, evidence overreach, verdict flips.
- Then add mitigations (schema hardening, span grounding checks, untrusted-content framing in prompts) and publish the before/after table.
- Output: `audit_outputs/reviewer_assist_red_team.{json,md}` — attack families, success rates before/after, unresolved weaknesses kept visible in the same promote-and-replace style as the unsolved cases.

### 3.2 garak probes
Wrap the extractor behind a minimal local endpoint and run the applicable garak probe families against it; document which families apply to a structured-output safety tool and which don't (that analysis is itself a result). Store the run config for reproducibility.

### 3.3 AI-generated campaign wave
Generate ~200 paraphrase/localization variants of 10 synthetic seed scams (cached, provenance-labeled generations). Do not include usable wallet addresses, live links, or operational instructions. Measure review-or-label retention and campaign-graph clustering retention versus the hand-built 56-mutation suite. This quantifies the semantic-laundering exposure the threat landscape already names as a blind spot.

**Frontend:** all three land inside What breaks' existing GenAI subtab, renamed "Red team record." No net-new nav.

**Acceptance:** every attack case is a versioned fixture in the manifest; before/after mitigation table on the site; at least one attack family remains unsolved and is published as such; pipeline regenerates all three reports.

---

## Phase 4 — External evidence (starts now, matures over 1–2 months)

1. **Blind time-separated eval:** freeze a fresh firehose sample **now** (`data/blind_holdout_2026Q3/`, hash-stamped, unlabeled, untouched by any tuning). Store raw content in the smallest access-controlled form necessary; commit only metadata, hashes, and an aggregate release artifact. Preregister the protocol in a short doc: labeled no sooner than 30 days later, thresholds frozen at today's values, results published regardless of outcome.
2. **Reviewer study kit:** structured rubric, consent language, 30-case packet, and a metrics script (agreement, time-to-decision, evidence usefulness) so a 5–8 person study can run the moment Ali recruits participants. Confirm whether the study is informal usability feedback or research requiring institutional review before recruiting. Publish aggregates and disagreement categories only.
3. **External red-team invitation:** a `SECURITY.md`-style page inviting adversarial testing of the labeler/policy with a published intake route — external findings feed the unsolved-cases pipeline with credit.
4. **Generalized kit (only after the labeler has operated 30 days):** extract the reusable primitives — policy schema → cascade scorer → review queue → transparency generator — into `kit/` with one page of docs, and pilot a second harm vertical (candidate: task-scam/fake-job solicitations, which shares the advance-fee grammar) as a config of the kit rather than a fork. The kit's vocabulary should deliberately mirror open T&S tooling (ROOST-style policy/classifier/review/action/metrics primitives).

---

## Sequencing summary for Codex

```
Week 1:      0.1 handoff → 0.2 branch audit/rebase decision → 0.3 provenance
Weeks 2–3:   1.1 benchmark protocol + first compatible-model run → 1.2 Inspect packaging
             4.1 blind holdout protocol frozen in parallel
Weeks 3–4:   3.1 reviewer-assistant red team → 3.2 applicable garak probes
Week 5:      Decide whether the quality of Phase 0–3 evidence justifies shadow mode
Ongoing:     Shadow operations, reviewer study, and any public labeler remain separately gated
```

Standing rules for every phase: run `bash scripts/run_all_checks.sh` before any push; never publish a number without provenance; new UI content goes inside the existing four destinations; uncommitted work gets checkpoint commits.

## Budget and access summary (Ali)

- Model APIs for Phase 1/3: ~$20–60 one-time (Groq/Together/OpenAI keys).
- Hosting for Phase 2: ~$5–10/month.
- Labeler Bluesky account + optional domain.
- Time: ~2 hours shadow audit (week 5), then ~15 min/week + appeals SLA if Stage B ships.
