# Safety Workflow API Spec

This is a product/API contract for a production-oriented version of the lab. It stays intentionally lightweight so the system boundary remains inspectable.

## Principles

- The API supports reviewer workflow; it does not autonomously enforce public labels.
- Scoring, evidence, review state, appeals, and campaign intelligence are separate surfaces.
- Every automated recommendation must expose evidence and uncertainty.
- All write endpoints need audit events.

## Endpoints

### `POST /score`

Scores a candidate post.

Request:

```json
{
  "text": "Final airdrop window. Connect your wallet...",
  "author": {
    "handle": "example.bsky.social",
    "did": "did:plc:example"
  },
  "source": "local_review"
}
```

Response:

```json
{
  "probability": 0.81,
  "recommendedAction": "high_confidence_escalation",
  "publicLabel": true,
  "reviewOrLabel": true,
  "policyEvidence": ["crypto_transfer_request", "suspicious_giveaway"],
  "contextualGuardrails": {
    "publicLabelSuppressed": false,
    "reviewPreferred": false
  }
}
```

### `POST /review-items`

Stores a scored candidate in the local review queue.

### `PATCH /review-items/{uri}/decision`

Records reviewer decision, notes, reviewer id, status, and audit event.

### `GET /review-items`

Lists queue items by status, action tier, source, entity, or probability range.

### `GET /entities`

Returns domains, wallets, handles, brands, and risk phrases observed in the queue.

### `GET /campaigns`

Returns shared-entity clusters for fraud-intelligence review.

### `POST /appeals`

Records appeal scenario or user appeal.

### `GET /ops-metrics`

Returns queue health, review coverage, backlog, action distribution, dismissal rate, and entity leads.

### `POST /eval-gates/run`

Runs scenario, hardening, adversarial, evidence, calibration, incident, and ops checks before launch.

## Design Rationale

The API keeps scoring, evidence, reviewer state, operations metrics, appeals, and eval gates separate instead of collapsing every decision into a single classifier endpoint.
