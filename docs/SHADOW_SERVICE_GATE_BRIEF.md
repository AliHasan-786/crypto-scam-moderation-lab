# Shadow-Service Gate Brief

**Decision owner:** Ali Hasan  
**Status:** Not approved; no shadow collection is running  
**Scope:** Observation-only Bluesky routing measurement. This is not a public
labeler, moderation action, account action, or public data feed.

## Decision requested

Choose one path before any long-running stream consumer is started.

| Path | What Codex may do | What it does not authorize |
| --- | --- | --- |
| A. Build-only | Implement the daemon, local state schema, tests, report generator, and deployment scaffold using synthetic fixtures. | Connecting it to Jetstream, retaining live data, or deploying an always-on process. |
| B. Start shadow observation | Do all of A, then start a private, bounded Jetstream consumer after every gate below is demonstrated and Ali accepts the operating duties. | Publishing labels, writing to Bluesky or any other service, showing live content in the public lab, or progressing to the public-labeler stage. |
| C. Defer | Keep the shipped aggregate-only radar as the only live-data surface. | Any shadow-service build or live collection. |

**Recommended decision:** A now. It creates testable operating evidence without
opening a collection program. Move to B only after reviewing the implemented
controls and naming the operator.

## What shadow mode would do

The service would read `app.bsky.feed.post` create events from the public
Jetstream relay, apply the frozen local scorer, and record only its *internal*
would-be route. It would never create a label, report a user, change visibility,
or make an authenticated Bluesky request.

The only proposed private records are:

- a short-lived review sample for the manual false-positive audit;
- a SQLite decision record with rule-level evidence for that sample; and
- aggregate daily snapshots: volume, route shares, matched-rule counts, and
  drift against the July 2026 EN/ES calibration.

No raw post text, handles, DIDs, URIs, or per-post decisions may enter Git,
the public site, Vercel, logs sent to third parties, or a public report.

## Gate checklist

All items are required for path B. Completion means a committed test or a
documented owner decision, not an assertion in prose.

| Requirement | Current state | Evidence required before start |
| --- | --- | --- |
| Protected-context guard | Policy and authored cases exist; daemon assertion does not. | Daemon aborts on any failed protected-context guard case. |
| Kill switch | Calibration CLI has a named owner field; no service switch exists. | An environment-variable switch stops intake and exits before processing the next event; tested. |
| Rate cap | Browser radar has a session cap; no daemon decision cap exists. | Configured maximum would-be decisions/hour, enforced and tested. |
| Zero outbound writes | Aggregate calibration is read-only; no daemon exists. | Test suite proves no HTTP/AT Protocol write client is imported or invoked. Network access is limited to the read-only relay. |
| Private retention | No approved schedule. | Exact fields, storage location, access list, retention duration, deletion command, and verification record. |
| Terms posture | A review date is required by calibration tooling. | Ali records the relay/platform terms review date and any constraints that affect this use. |
| Named operator | Unassigned. | One person accepts incident triage, stopping the service, and the manual audit. |
| Incident response | Existing tabletop materials are informative, not bound to a daemon. | A shadow-specific runbook covering protected-context failure, unexpected volume, storage exposure, and service outage. |
| Deployment | Unchosen. | Ali selects a host and cost ceiling, or explicitly keeps the service local. No deployment before the prior controls pass. |

## Minimum operating configuration for path B

Record these values in an untracked local environment file or deployment secret
store, never in Git:

```text
SHADOW_ENABLED=true
SHADOW_OPERATOR=<name>
SHADOW_KILL_SWITCH_OWNER=<name>
SHADOW_TERMS_REVIEW_DATE=YYYY-MM-DD
SHADOW_MAX_DECISIONS_PER_HOUR=<positive integer>
SHADOW_RETENTION_DAYS=<positive integer>
SHADOW_STORAGE_PATH=<private path>
```

The process must default to disabled when any required setting is absent.
The kill switch must be usable without a code change or redeployment.

## Exit criteria and publication boundary

Shadow observation becomes useful only after 14 consecutive daily snapshots and
a private, stratified 100-item manual audit. The resulting report must state
the sampled precision estimate and uncertainty interval, retention limits, and
all collection provenance. It may publish aggregates only after a separate
privacy review.

Completing shadow mode does **not** authorize a public labeler. The separate
public-labeler gate still requires the shadow record, an end-to-end appeal
test, Ali's explicit recurring-operations commitment, and a fresh go/no-go.

## Rationale

The current model's documented false positives include warnings, satire,
reportage, research, debugging, and help-seeking. A private observation period
is valuable precisely because it can show whether those safeguards survive
outside authored cases. It is not a reason to turn uncertain classifier output
into a public accusation.

