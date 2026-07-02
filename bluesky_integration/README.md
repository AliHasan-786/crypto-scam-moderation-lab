# Bluesky Integration Plan

This folder contains a read-only integration path for the portfolio project.

## Feasibility

### Level 1: Authenticated Read-Only Search

Feasible now. Use a normal Bluesky account plus an app password to search candidate posts and score them locally with `policy_proposal_labeler_v2.py`.

This does **not** publish labels, send reports, write posts, or alter Bluesky state.

```bash
export BSKY_HANDLE="your-handle.bsky.social"
export BSKY_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"

python3 bluesky_integration/bluesky_search_ingest.py \
  --query "crypto airdrop wallet" \
  --limit 25 \
  --out audit_outputs/live_bsky_search_sample.json \
  --db audit_outputs/live_review_queue.sqlite \
  --export-lab-data crypto-scam-lab/data/liveReviewQueue.js
```

Use a Bluesky app password, not the main account password.

### Level 2: Firehose / Jetstream Monitor

Feasible now as a bounded local prototype. `jetstream_monitor.py` subscribes to public AT Protocol post events, filters for crypto-related terms, scores matching posts locally, and writes JSONL review samples.

Example:

```bash
python3 bluesky_integration/jetstream_monitor.py \
  --max-events 1000 \
  --max-matches 25 \
  --timeout-seconds 45 \
  --out audit_outputs/live_bsky_jetstream_sample.jsonl \
  --db audit_outputs/live_review_queue.sqlite \
  --export-lab-data crypto-scam-lab/data/liveReviewQueue.js
```

Implemented local review-store support:

- SQLite persistence in `audit_outputs/live_review_queue.sqlite`.
- Deduplication by post URI/CID.
- Reviewer decision tracking.
- Entity extraction for domains, wallet-like strings, handles, brands, and high-risk policy phrases.
- Deterministic no-fetch URL evidence for defanged links, shorteners, suspicious TLDs, campaign-keyword domains, and brand-impersonation domains.
- Campaign graph export for shared-domain/shared-wallet investigation.
- Browser-lab export to `crypto-scam-lab/data/liveReviewQueue.js`.

Next engineering needs:

- Backpressure/rate handling beyond the bounded demo.
- Actor-profile, link-resolution, URL-redirect, and landing-page enrichment.
- Clear retention policy so we do not store unnecessary unrelated content.

### Level 3: Real Labeler Service

Feasible, but should come later. A true labeler is not just a script:

- Create a separate labeler account.
- Configure the account DID document and `app.bsky.labeler.service` declaration.
- Host a labeler service endpoint over HTTPS.
- Sign labels with the proper labeler key.
- Define the custom `potential-crypto-fraud` label and localized copy.
- Add reviewer/appeal controls before any public labeling.
- Avoid bulk public export of accused users or scammer lists.

The safest production route is to evaluate Ozone first, because Bluesky/AT Protocol docs describe it as a web moderation interface for running a labeler and reviewing reports.

## Current Script

`bluesky_search_ingest.py`:

- Creates an authenticated session with `com.atproto.server.createSession`.
- Calls `app.bsky.feed.searchPosts`.
- Scores returned posts with the saved v2 model artifact.
- Emits JSON containing URI, author handle/DID, text, probability, action tier, and policy evidence.

`jetstream_monitor.py`:

- Connects to Jetstream with `wantedCollections=app.bsky.feed.post`.
- Filters public posts by crypto-related keywords before scoring.
- Scores only matching posts with the saved v2 model.
- Writes bounded JSONL samples for private review and demo development.
- Can persist scored matches to the local SQLite review queue.

`review_store.py` and `review_queue_cli.py`:

- Initialize the local review queue.
- Upsert scored posts with dedupe.
- Record reviewer decisions.
- Export queue data into the browser lab.
- Persist extracted entities into `review_entities` and `review_item_entities`.
- Export campaign graph data into `audit_outputs/campaign_graph.json` and `crypto-scam-lab/data/campaignGraph.js`.

`url_evidence.py`, `entity_extractors.py`, and `campaign_graph.py`:

- Extract domains, defanged domains, URL shorteners, wallet-like strings, handles, author identifiers, brand/entity mentions, and high-risk policy phrases.
- Score text-level URL evidence without fetching pages or resolving redirects.
- Summarize shared entities across queued items.
- Build lightweight clusters by shared domain, wallet, shortener, or handle.
- Keep the logic deterministic and auditable rather than using opaque clustering as the first version.

Seed the sanitized demo queue:

```bash
python3 bluesky_integration/review_queue_cli.py \
  --db audit_outputs/live_review_queue.sqlite \
  seed-demo \
  --export-out crypto-scam-lab/data/liveReviewQueue.js
```

List local review items:

```bash
python3 bluesky_integration/review_queue_cli.py \
  --db audit_outputs/live_review_queue.sqlite \
  list --limit 10
```

Record a reviewer decision:

```bash
python3 bluesky_integration/review_queue_cli.py \
  --db audit_outputs/live_review_queue.sqlite \
  decide \
  --uri "demo://crypto-scam-lab/high-confidence-airdrop" \
  --status escalated \
  --decision fraud \
  --notes "Confirmed wallet-drainer-style airdrop evidence."
```

Export to the browser lab:

```bash
python3 bluesky_integration/review_queue_cli.py \
  --db audit_outputs/live_review_queue.sqlite \
  export \
  --out crypto-scam-lab/data/liveReviewQueue.js
```

Export the campaign graph:

```bash
python3 bluesky_integration/review_queue_cli.py \
  --db audit_outputs/live_review_queue.sqlite \
  graph \
  --out audit_outputs/campaign_graph.json \
  --lab-summary crypto-scam-lab/data/campaignGraph.js
```

The script defaults to `https://bsky.social` for both the PDS and AppView because unauthenticated public search returned `403` during local testing. These hosts can be overridden:

```bash
export BSKY_PDS="https://bsky.social"
export BSKY_APPVIEW="https://bsky.social"
```

## Safety Boundary

For now, this integration should only be used to generate private review samples. Do not publish labels or moderation reports until the review workflow, appeals path, false-positive controls, retention policy, and transparency reporting are implemented.
