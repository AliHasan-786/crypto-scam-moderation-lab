# Policy & Product Decision Log

Dated record of the judgment calls behind the system, with the tradeoff each one accepted. This is the document I would bring to a design review: every entry names what was given up, not just what was chosen.

---

### 001 — Optimize for two metrics, not one (Nov 2025)

**Context:** The coursework labeler reported a single F1. A public "Potential Crypto Fraud" label and a silent review-queue routing have completely different costs when wrong.
**Decision:** Split evaluation into public-label precision/recall and review-or-label recall, and treat them as separate product guarantees: labels must be precise; the review net must be near-exhaustive.
**Tradeoff accepted:** Headline metrics look less impressive than one cherry-picked F1, and threshold tuning is harder with two objectives.
**Revisit when:** A production deployment would add per-surface metrics (feeds vs. search vs. replies).

### 002 — Policy floor of 0.40 on the review threshold (Nov 2025)

**Context:** F1-optimal tuning pushed the review threshold to 0.39 with precision ~0.79. Below 0.40, queue volume grows faster than recall.
**Decision:** Floor the review tier at 0.40 even when raw tuning suggests lower; accept 0.9886 review recall instead of chasing 1.0.
**Tradeoff accepted:** A small slice of true scams (~1% in tuning data) scores under the floor and gets no action. The alternative — flooding reviewers — degrades every queued decision. Capacity is a safety resource.
**Revisit when:** The scale simulation (scale_sim/) shows reviewer capacity headroom, or campaign-graph signals can pre-filter the sub-floor band.

### 003 — Public-label threshold at 0.54, escalation at 0.61 (Nov 2025)

**Context:** Test-set operating point yields precision 0.882, recall 1.0, confusion matrix TN 100 / FP 8 / FN 0 / TP 60.
**Decision:** Accept 8 false-positive label candidates out of 108 legitimate posts (7.4%) at the candidate stage, because a label candidate is not a published label: reviewer confirmation, notice, and appeal sit between the model and the user.
**Tradeoff accepted:** Reviewer time is spent killing those 8 FPs; that is the designed cost of recall 1.0 on the fraud class. If reviewer confirmation were ever removed, this threshold would be indefensible — the FP rate belongs to the workflow, not just the model.
**Revisit when:** Error analysis (evals/error_analysis.py) shows FP categories that a targeted feature could remove without recall loss.

### 004 — No fully automated public labels at any confidence (Nov 2025)

**Context:** At score ≥ 0.90 the model is essentially always right on the current corpus. Tempting to auto-publish.
**Decision:** Every public label requires reviewer confirmation. Automation ends at "candidate."
**Tradeoff accepted:** Latency and reviewer cost on the most obvious cases. Rationale: the current corpus cannot estimate tail risk (adversarial drift, protected-context edge cases), and a wrong public fraud accusation is a reputational harm the platform inflicts directly. Santa Clara Principles alignment also requires meaningful human review to be more than nominal.
**Revisit when:** Prevalence-weighted FP estimates from much larger corpora exist, and even then likely only for temporary interstitials during active incidents (per the incident runbook), not standing labels.

### 005 — Protected contexts suppress labels even at high scores (Nov 2025)

**Context:** Warnings, news, satire, research, debugging, and help-seeking reuse scam vocabulary verbatim; they are lexically closer to scams than most legitimate content.
**Decision:** Context features gate public labeling regardless of score; conflicts route to review.
**Tradeoff accepted:** Adversaries can dress scams as warnings ("this airdrop is a scam — the real one is here"). That evasion class is explicitly tested in the hardening suite; the mitigation is speaker-ask detection plus link evidence, not weakening the protection. Punishing the people who warn others is the worst failure this system can produce.
**Revisit when:** Never, in principle. The mechanics (which markers count) evolve via calibration cases.

### 006 — TF-IDF + policy features as the reproducible baseline (Dec 2025)

**Context:** The original coursework model had leakage and model-selection issues (documented in audit_outputs/original_labeler_audit.json). Options: fix it quietly, or rebuild simpler and audit the original publicly.
**Decision:** Rebuild as TF-IDF + logistic regression + explicit policy features; keep the original in-repo with its audit as provenance.
**Tradeoff accepted:** A deliberately unfashionable model. The bet: for a portfolio system, a reproducible baseline whose failures are inspectable beats an impressive black box. The LLM comparison track (llm_evidence/) exists to test — not assume — where an LLM earns its cost on top of this baseline.
**Revisit when:** The baseline-vs-LLM comparison shows category-level wins that justify per-decision inference cost (see llm_comparison report).

### 007 — Mutation retention: review-or-label 100%, public-label 82.1% is by design (Jan 2026)

**Context:** Under 56 controlled obfuscation variants (leetspeak, spacing, defanged URLs, etc.), 17.9% of previously labelable posts drop below the public-label bar.
**Decision:** Accept the downgrade as correct behavior: obfuscation reduces legible evidence, and reduced evidence should demote a public accusation to human review — it should never silently drop the case, which is why review-or-label retention must stay at 100%.
**Tradeoff accepted:** Slower enforcement on obfuscated campaigns (reviewer in the loop) in exchange for not lowering the public-label evidence bar under adversarial pressure.
**Revisit when:** Canonicalization improvements recover evidence legibility without loosening the bar (two such fixes already landed via the hardening suite).

### 008 — The public demo is sanitized and cannot act (Jan 2026)

**Context:** Live Bluesky ingestion works locally read-only. Publishing labels or exposing real accounts in a portfolio demo would create real-world harm with no accountability structure.
**Decision:** Public demo ships synthetic/sanitized data only; no publish path exists in the deployed code.
**Tradeoff accepted:** The demo looks less "live." A safety project that manufactures unaccountable enforcement against real users to look impressive would refute its own premise.
**Revisit when:** Not applicable.

### 009 — Cached LLM outputs in the public demo (Jul 2026)

**Context:** The hosted LLM evidence adapter needs model outputs, but the public demo must stay static, free, and key-less.
**Decision:** Ship the adapter with cached outputs generated by Claude (clearly labeled with model and date), gated by the same span-faithfulness eval as the deterministic extractor; a regeneration script lets anyone rerun with their own key.
**Tradeoff accepted:** Cached outputs age and reflect one model's behavior at one point in time. Labeling the provenance is the mitigation; hiding it would be the failure.
**Revisit when:** Each regeneration; cache staleness is surfaced in the comparison report.

### 010 — Failure visibility as a product requirement (Jul 2026)

**Context:** Authored eval suites passing at 100% read as tests written to pass — because, absent visible failures, they are indistinguishable from that.
**Decision:** Add a standing error-analysis surface: the live false positives at the operating point, unsolved hard cases the system currently gets wrong, and the tradeoff each failure represents. Failures stay published; fixing one requires adding a harder case to replace it.
**Tradeoff accepted:** The project permanently displays its own mistakes. That is the point: an evaluation culture where 100% green is treated as a smell, not a goal.
**Revisit when:** Never — the mechanism is permanent even as individual cases rotate.

### 011 — Live traffic, aggregate-only by construction (Jul 2026)

**Context:** The lab gained two live-firehose surfaces: an in-browser radar that scores the public Bluesky Jetstream stream client-side, and an offline calibration report that runs the full model over a stream sample. Real traffic makes the system credible at scale — and creates the first surface where real users' content flows through it.
**Decision:** Both surfaces are aggregate-only by construction. Post text is scored in memory and discarded; no text, handle, DID, URI, or per-post record is ever stored, displayed, or transmitted. The radar runs entirely in the visitor's browser against a public read-only feed and has no action path. Decision 008 (the demo cannot act) extends unchanged to live data.
**Tradeoff accepted:** The radar looks less dramatic than a scrolling feed of "caught" posts would. A scrolling feed would also be a public accusation surface with no reviewer, no notice, and no appeal — the exact failure mode this project exists to prevent. Counters over content, always.
**Revisit when:** If a research use ever requires retaining stream content, it moves behind the local-only ingestion path with its existing retention rules — never into the public demo.
