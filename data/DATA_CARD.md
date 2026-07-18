# Data Card

## Purpose and scope

This repository is a portfolio-grade Trust & Safety research system, not a
production moderation service. Its public artifacts use sanitized coursework
data or authored evaluation cases. The optional Bluesky stream work is
aggregate-only measurement; it is not a source of training data and cannot
take platform action.

## Primary labeled corpora

| Asset | Rows | Purpose | Label source | SHA-256 |
| --- | ---: | --- | --- | --- |
| `data.csv` | 147 | Training the reproducible v2 baseline | Coursework labels inherited from the original project; not independently re-adjudicated | `575947d4629cddecde2023128fc6bfe1cbaae81eac936ff2f4624d94cb5111be` |
| `test.csv` | 168 | Frozen held-out v2 evaluation and standing error analysis | Coursework labels inherited from the original project; never used for v2 threshold selection | `b886ac28c805e6ed8cabb74f6fa24551467bb2d7bdba5cfda2ecec0392685a14` |

Row counts are parser-level examples, not physical file lines; quoted post
content can span multiple lines. Both files contain post-like text and binary crypto-fraud labels. They are
small, mostly English, and reflect the coverage and annotation choices of the
coursework project. They are not a prevalence sample, a representative sample
of Bluesky, or evidence of production performance. The original labeler's
selection and leakage problems are documented in
[`audit_outputs/original_labeler_audit.json`](../audit_outputs/original_labeler_audit.json).

## Authored evaluation suites

| Asset | Purpose | SHA-256 |
| --- | --- | --- |
| `evals/scenario_eval_cases.json` | Explicit policy-boundary cases | `d7de6a0c132977c454925c5d009e934fa8c75b45464b39e18c4f5da7eb4df28d` |
| `evals/hardening_eval_cases.json` | URL, canonicalization, OCR, multilingual, and protected-context tests | `3660e09caadac6221113a42df82170ebd6fa7745a74417d12152214df0e40a86` |
| `evals/unsolved_cases.json` | Published hard cases that deliberately remain failing | `28c16a63faa7e097bad608dabed1e1f2bca01f664b58a03ecf6bd7213bbde397` |
| `quality/calibration_cases.json` | Reviewer-calibration answer key | `789a4b83322828442613b0bd3cc5af6bc253bcba1f6aff6c193c55168b5a73f0` |
| `governance/appeal_scenarios.json` | Authored notice, appeal, and reversal scenarios | `34c642164b90934dc7fdff56c65f28a90d9d8612ccdb1fb38fb101c2de4608f8` |
| `incident_response/incident_scenarios.json` | Synthetic incident tabletop scenarios | `59ba0ff5d3474499007a9d4386e337cbca6c5ec900f2d252f8a3003f312159e9` |

These are authored tests, not independent benchmarks. They test whether the
implemented policy boundary holds and must be read alongside the held-out error
analysis and published unsolved cases. A suite change requires a manifest
version bump once `evals/MANIFEST.json` lands (roadmap Phase 0.3).

## Live Bluesky stream calibration candidate

The branch `origin/scale/live-firehose-radar` contains one aggregate-only
calibration artifact, reviewed on 2026-07-18 before any rebase or merge.

| Field | Recorded value |
| --- | --- |
| Collection source | Public Bluesky Jetstream relay, `app.bsky.feed.post` create events |
| Collection window | 240 seconds; report generated 2026-07-11 22:34Z |
| Non-empty posts observed | 11,353 |
| Posts scored | 8,210, limited to records whose first declared language was English or Spanish |
| Excluded from scoring | 3,143 non-English/Spanish records; empty/non-create events are outside the recorded denominator |
| Model artifact hash | `d23e28d61f3982d3ae659ead59ae63d333b82516689a8fd760acd1b8aa588c6c` |
| Aggregate report hash | `670d0d5dbe661c112987f6c51280db8cf3bb7295e0bf61f7265a2e641d21b2a6` |
| Raw retention | None in the calibration script: text is scored in memory, then discarded; no text, handles, DIDs, URIs, or per-post rows are written |

This candidate artifact supports two narrowly defined measurements at the
shipped July 11 thresholds:

- **7.10%** (`583 / 8,210`) received the *intermediate*
  `send_to_human_review` action.
- **7.31%** (`600 / 8,210`) were human-operated queue eligible when the 14
  candidate-label and 3 high-confidence-escalation posts are included. The
  policy requires human confirmation for both actions, so this is the relevant
  share for staffing.

It does **not** measure fraud prevalence, performance, precision, recall, or
the queue share for all Bluesky traffic. It is a four-minute, EN/ES-screened,
time-bound snapshot of model routing. The audit record is
[`docs/FIREHOSE_BRANCH_AUDIT_2026-07-18.md`](../docs/FIREHOSE_BRANCH_AUDIT_2026-07-18.md).

## Privacy, access, and retention

- The public lab contains sanitized/author-authored content only and has no
  publishing, reporting, or account-action path.
- The aggregate calibration path is permitted to retain counts and score
  distributions only. Raw live content must never be committed or served by
  the public demo.
- The pre-existing local Jetstream monitor is a separate research utility that
  can write identifiable review samples. It remains local-only and out of
  scope for the public lab until a retention schedule, access controls,
  deletion procedure, and human-review governance are explicitly approved.
- Any future live collection must record the exact UTC start/end time, relay
  endpoint, language filter, model and code hashes, terms/acceptable-use
  review date, operator, retention decision, and kill-switch owner.

## Known biases and limits

The base data is small and inherited; the tests are authored; the stream
sample is brief, language-filtered, and unlabeled; and all reported model
behavior is time- and version-specific. No artifact here justifies automated
public enforcement. These constraints are part of the result, not footnotes.
