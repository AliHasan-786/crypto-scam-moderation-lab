# Crypto Scam Incident Response Runbook

This runbook covers coordinated crypto-scam or wallet-drainer incidents on a Bluesky-style social platform.

## Operating Principles

- Protect users quickly without over-labeling legitimate speech.
- Preserve evidence before changing broad enforcement rules.
- Prefer human review when source context, link destination, or speaker intent is incomplete.
- Treat repeated domains, wallets, phrases, and handles as investigation leads, not automatic proof.
- Convert every incident into policy guidance, eval cases, reviewer calibration examples, or product mitigations.

## Severity Tiers

| Severity | Description | Response |
|---|---|---|
| `sev1` | Active, high-scale fraud causing immediate user loss or account compromise | Dedicated incident lead, hourly updates, emergency mitigations, exec/legal awareness |
| `sev2` | Coordinated campaign with strong evidence and rising exposure | Incident lead, same-day mitigation plan, campaign tracking, reviewer priority |
| `sev3` | Localized spike, false-positive issue, OCR ambiguity, or emerging pattern | Triage owner, sample review, eval/calibration update, normal product review |
| `sev4` | Single case or weak signal | Queue review and trend monitoring |

## First 30 Minutes

1. Identify the trigger: user reports, queue spike, shared entity, model alert, appeal spike, or external report.
2. Pull representative samples and preserve URIs, text, author metadata, entities, timestamps, and reviewer notes.
3. Decide severity using scale, confidence, user harm, false-positive risk, and regulatory/compliance exposure.
4. Assign owner: Incident Lead, Ops Reviewer, Policy Lead, Product/Eng Contact, Comms/Legal if needed.
5. Choose the safest immediate action:
   - public labels for clear fraud with strong evidence
   - human review for ambiguous or missing-context cases
   - warning friction for risky domains pending review
   - no action for protected context or weak evidence

## Evidence Checklist

- Exact text and normalized text.
- Scam-policy rules matched.
- Public-label rules matched.
- Contextual guardrails: warning, satire, research, developer, help-seeking.
- URL evidence: domain, shortener, suspicious TLD, defanged form, claim/wallet path.
- Entity evidence: domain, wallet, handle, brand, risk phrase.
- Campaign links: repeated entity, duplicate count, shared author behavior.
- Reviewer decision and notes.
- User-impact estimate and false-positive risk.

## Escalation Criteria

Escalate from queue review to incident response when any are true:

- repeated suspicious domain or wallet appears across multiple posts
- campaign is spreading through new accounts or coordinated handles
- confirmed wallet-drainer or payment request is present
- high-risk content is paired with brand/public-figure impersonation
- appeal or dismissal rate indicates possible over-enforcement
- media/OCR reports contain QR codes or cropped links at meaningful volume

## Mitigation Menu

Low-risk mitigations:

- reviewer priority boost
- warning friction before link click
- domain/entity watchlist
- user education notice
- temporary review queue routing

Higher-risk mitigations:

- public Potential Crypto Fraud label
- account-level escalation
- rate limits
- domain-level block or interstitial
- enforcement expansion across campaign cluster

High-risk mitigations require stronger evidence and appeal paths.

## Comms Template

Internal update:

```text
Incident:
Severity:
Current user risk:
Evidence:
False-positive risk:
Immediate mitigation:
Open decision:
Owner:
Next update:
```

Reviewer instruction:

```text
Review posts matching [entity/pattern].
Apply public labels only when [required evidence].
Route to human review when [ambiguity].
Do not label [protected contexts].
Escalate examples with [criteria].
```

## Postmortem Template

```text
Incident summary:
Timeline:
Detection source:
What worked:
What failed:
User impact:
False-positive impact:
Reviewer impact:
Policy changes:
Eval additions:
Tooling changes:
Owner and deadlines:
```

## Tabletop Scenarios

See `incident_scenarios.json` and the generated `audit_outputs/incident_response_tabletop.md`.
