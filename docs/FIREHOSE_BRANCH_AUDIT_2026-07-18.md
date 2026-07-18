# Firehose Branch Audit — 2026-07-18

**Scope:** one-day, source-and-artifact audit of
`origin/scale/live-firehose-radar` at `b0a01d5`. This is not a merge approval.
Its purpose is to determine whether the branch's July 11 stream-calibration
claim is supportable and what must change before the branch is rebased.

## Decision

The branch's **7.10%** figure is supportable only as the share of the **8,210
English/Spanish posts scored** that received the intermediate
`send_to_human_review` routing decision in a 240-second sample. It must not
be described as platform prevalence, a performance estimate, all-firehose
traffic, or total reviewer demand.

For staffing, the correct aggregate is **7.31%**: all 600 posts routed to a
human-operated action (`583` review + `14` candidate-label + `3`
high-confidence escalation) divided by 8,210 scored posts. Candidate labels
and escalations require reviewer confirmation under Decision Log 004.

No rerun is required to preserve the narrow 7.10% routing measurement. A
rerun is required before any claim that the result represents all languages,
all posts observed by Jetstream, or an ongoing rate.

## Evidence reviewed

| Check | Finding | Status |
| --- | --- | --- |
| Collection window | `stream_calibration.py` accepts an explicit window; the committed report records 240.0 seconds, generated 2026-07-11 22:34Z | Pass, bounded but brief |
| Sampling logic | Processes `app.bsky.feed.post` create records with non-empty text; scores only the first declared `langs` value when it is `en` or `es` | Pass, with language-scope caveat |
| Denominator | Report records 11,353 non-empty posts observed, 8,210 EN/ES posts scored, and all action counts sum to 8,210 | Pass |
| Review-tier definition | 7.10% is only `send_to_human_review` (`583 / 8,210`); labels/escalations are separate human-confirmed actions | Correctable reporting issue |
| Retention | Calibration script deletes in-memory text before output and writes aggregate data only | Pass |
| Terms posture | Public Jetstream endpoint is named, but no terms/acceptable-use review date is recorded | Must add before a future collection |
| Reproducibility | Code and aggregate artifact are committed, but report lacks exact code/model hashes and UTC start/end times | Must add before a future collection |
| Public demo privacy | Radar is designed to display aggregate counters only; branch must be rechecked after editorial rebase with `rg -i "did:|handle" crypto-scam-lab/app.js` | Pending rebase |

## Required rebase changes

1. Rename the calibration metric to **"intermediate human-review routing
   share among scored EN/ES posts"** wherever 7.10% appears.
2. Add **"human-operated queue share"** (`7.31%` for this sample) for
   staffing surfaces, or explicitly state that label/escalation confirmation
   work is excluded.
3. Replace phrases such as "real firehose traffic" with "a 240-second public
   Jetstream EN/ES-screened snapshot".
4. Record exact collection start/end UTC times, code commit, SHA-256 model
   artifact, terms-review date, named operator, retention decision, and
   kill-switch owner in future outputs.
5. Keep the live radar inside **Try it**, below the tester, with no post text,
   handle, DID, URI, or per-post data in the public path.
6. Add the stream entry to the data card and do not merge generated branch
   artifacts that are stale or unrelated to the radar work.

## Non-findings

The aggregate report does not claim fraud prevalence, and its action counts
are internally consistent. The 7.10% result therefore does not require a
corrected rerun solely because it differs from the synthetic scale simulation.
That difference is useful calibration evidence; it becomes misleading only
when the scoped routing measure is presented as a broader operational fact.

## Merge gate

Rebase is allowed after the six changes above are implemented and verified.
Publication of any new stream result remains separately gated by the data card,
zero-write tests, rate cap, kill switch, named operator, and the shadow-mode
requirements in `LAB_ROADMAP_2026H2.md`.
