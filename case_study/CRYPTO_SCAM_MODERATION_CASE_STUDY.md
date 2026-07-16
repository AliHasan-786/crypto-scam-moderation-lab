# Case Study: Crypto Scam Moderation Lab

## The one-sentence version

I took a coursework crypto-scam classifier, audited my own model and found its evaluation flaws, and rebuilt it solo into a full-stack Trust & Safety system — policy, tiered enforcement, human review, campaign intelligence, incident response, appeals, LLM assistance, scale economics — that publishes its own failures instead of hiding them.

[Open the live lab](https://crypto-scam-lab.vercel.app) · [Repository](https://github.com/AliHasan-786/crypto-scam-moderation-lab)

## The problem worth solving

Crypto investment scams cost Americans $5.8B in reported losses in 2024 (FBI IC3) — the largest category of crypto crime. But the detection problem is not "find scam words." Scammers, journalists warning about scams, researchers studying them, comedians mocking them, and victims asking for help all use the *same vocabulary*. A classifier that optimizes for catch rate silences the platform's best allies: the warners and the victims.

So the product question I built around: **when is evidence strong enough for a public fraud accusation, when does uncertainty belong with a human, and when should the platform leave speech alone?**

## What I actually did (in order)

**1. Audited my own coursework model — and published the audit.** The original classifier looked impressive and had real problems: model-selection hygiene and leakage risks. Instead of quietly fixing it, I wrote `audit_original_labeler.py`, documented the issues in a versioned artifact, and kept the flawed original in the repo as provenance. Rebuilding trust in a metric starts with distrusting your own.

**2. Wrote the policy like a policy team would.** A platform-style policy document with in/out-of-scope definitions, six protected contexts enforced in code, an enforcement matrix (violation × severity × minimum evidence × action), and a dated decision log where every threshold and tradeoff has an owner, a rationale, and a revisit trigger. The moment worth highlighting: the decision that **no confidence level ever auto-publishes a label** — automation ends at "candidate," humans confirm, users appeal.

**3. Split evaluation into promises the product actually makes.** Aggregate F1 is one number for two different failure modes with wildly different costs. I separated public-label precision (a wrong label is platform-inflicted harm) from review-or-label recall (did risky content at least reach a human?), added protected-context suppression tests, adversarial mutation retention, and wired it all into a CI release gate that fails the build on regression.

**4. Built the failure-honesty layer — the part I'm proudest of.** Authored eval suites passing at 100% are indistinguishable from suites written to pass. So the system maintains a standing error analysis: the 8 real false positives at the operating point, categorized (6 of 8 are people *skeptically describing* scams — the system's biggest real weakness, found by this analysis), plus 9 authored hard cases where 5 still fail — warning-wrapper evasion, doubt-language camouflage, anonymous-authority claims — published with the reason each is hard. When one starts passing, it gets promoted to the regression suite and replaced with something harder. Failures are the roadmap.

**5. Priced the thresholds in people and payroll.** A scale simulation runs the same model over a synthetic 50,000-post day (1.5% scam prevalence — knowable because synthetic; in production that number requires labeled sampling, and the report says so). Result: the 0.40 review-threshold policy floor costs ~37 reviewers/day; dropping to 0.30 roughly doubles payroll for ~1 point of review-net recall. It also surfaced a new finding: ~6% of legitimate posts reach the label-candidate stage, overwhelmingly the skeptical-reportage class — quantifying at scale exactly what the error analysis found in miniature.

**6. Made the LLM earn its seat.** A hosted-LLM evidence adapter (cached, provenance-labeled outputs for the static demo; live regeneration script included) runs against the same policy prompt and the same span-faithfulness gate as the deterministic extractor. The comparison is honest: the baseline wins on cost by orders of magnitude; the LLM reads *stance* — who is speaking and why — which is precisely the dimension behind the baseline's worst false-positive class. One scored disagreement (the suite expects review for a help-seeking post; the LLM declined to burden a victim) is preserved unresolved, because it is a live policy question.

**7. Built the operational shell real systems need.** Reviewer calibration with answer keys, ops analytics with SQL, campaign graphs over reused wallets/domains/phrasing, incident tabletops with severity tiers, appeals with reversal tracking, a transparency report, Santa Clara / NIST RMF mapping, and a DSA statement-of-reasons sample populated from actual pipeline outputs.

**8. Rebuilt the front door for humans.** The public experience is now an interactive case study rather than a simulated operations console: the story and policy boundary come first, the stance-aware post interaction proves the core idea, published failures form the climax, and the operating artifacts live in an explicit appendix. Visitors can paste a post — or switch among a scam, warning, joke, and skeptical question — and watch the decision and evidence change.

## Key numbers

Baseline: precision 0.882 / recall 1.000 / F1 0.938 on the held-out test set — all 8 false positives published with commentary. Mutation testing: 100% review-or-label retention across 56 variants (82.1% public-label retention; the downgrade is designed, not a defect). Evidence: 100% span faithfulness for both extractors. Scale: full threshold-to-staffing curve at 50k posts/day. Pipeline: 15 steps, one command, same in CI.

## What I'd change at 100× scale

Honest answers to the "what breaks at 5M posts/day" question:

**The classifier stops being the interesting part.** At scale, the baseline becomes a cheap first-pass triage and the real detection moves to campaign level: near-duplicate clustering, account-history features, infrastructure reuse velocity. Single-post scoring cannot see pig butchering — the highest-loss typology — because its recruitment surface is deliberately mild. I'd invest in the graph, not the post model.

**Burst capacity beats steady state.** The 12-week simulation shows campaign waves tripling queue load. Static staffing fails; I'd build surge protocols (the incident runbook's temporary interstitials, pre-authorized threshold shifts with automatic expiry, cross-trained reviewer pools) rather than hiring to peak.

**The review queue needs stratified sampling, not just risk ranking.** Pure risk-descending review starves measurement. I'd reserve a fixed slice of reviewer capacity for random sampling to get true prevalence and calibration drift — the numbers transparency reports are supposed to contain.

**LLM assistance goes where stance matters.** Not first-pass filtering (cost), not final decisions (accountability) — but drafting evidence summaries on the review slice and flagging stance mismatches ("this reads as reportage, not solicitation") where the baseline is systematically weak.

**Appeals become the primary feedback loop.** At scale, reversal categories are the highest-signal data the policy team gets. I'd wire reversal taxonomies directly into eval-case generation — every overturned decision should become a regression test within the week.

## Limitations

The dataset is small and mostly English. The suites are authored (the error-analysis surface exists precisely because of this). Campaign examples are sanitized and deterministic. OCR, live URL resolution, and account-history enrichment are simulated or future work. The public demo cannot take any platform action, by design. None of this is hidden — the failure page is a top-level navigation item.

## Screenshots

![Landing page](assets/lab-desktop-overview.png)

![Governance panel](assets/lab-governance-panel.png)

![Mobile view](assets/lab-mobile-review.png)
