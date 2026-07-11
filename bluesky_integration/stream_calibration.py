"""Score a live Bluesky Jetstream sample and publish aggregate calibration.

The rest of the pipeline evaluates the model on authored and synthetic
corpora. This script answers a different question: what does the score
distribution look like on REAL platform traffic, right now?

It connects to the public Jetstream firehose, collects post texts for a
bounded window, scores them with the same joblib artifact and decision layer
as every other report, and then publishes ONLY aggregates:

- posts observed, language mix, collection window;
- score histogram (model probability and deterministic policy score);
- decision-tier shares at the shipped thresholds;
- top matched policy rules by frequency.

Privacy design (Decision Log 011): post text is scored in memory and
discarded. No text, handle, DID, URI, or any per-post row is written to disk.
The only persisted values are counts and score aggregates. This mirrors the
live radar in the web lab, which applies the same rule in the visitor's
browser.

True prevalence on real traffic is NOT knowable from detection output —
this report never claims it (see METRICS_DEFINITIONS.md). Tier shares here
measure queue load, not scam prevalence.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import policy_proposal_labeler_v2 as v2  # noqa: E402

JETSTREAM_URL = (
    "wss://jetstream2.us-east.bsky.network/subscribe"
    "?wantedCollections=app.bsky.feed.post"
)
SCORED_LANGS = {"en", "es"}
HISTOGRAM_EDGES = [round(x / 10, 1) for x in range(11)]


async def collect_texts(seconds: float, max_posts: int) -> dict[str, object]:
    import websockets

    texts: list[str] = []
    lang_counts: dict[str, int] = {}
    observed = 0
    skipped_lang = 0
    started = time.monotonic()

    async with websockets.connect(JETSTREAM_URL, max_size=2**22) as socket:
        while time.monotonic() - started < seconds and len(texts) < max_posts:
            try:
                raw = await asyncio.wait_for(socket.recv(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue
            commit = event.get("commit") or {}
            if event.get("kind") != "commit" or commit.get("operation") != "create":
                continue
            record = commit.get("record") or {}
            text = str(record.get("text") or "").strip()
            if not text:
                continue
            observed += 1
            langs = record.get("langs") or ["und"]
            primary = str(langs[0] or "und").split("-")[0].lower()
            lang_counts[primary] = lang_counts.get(primary, 0) + 1
            if primary in SCORED_LANGS:
                texts.append(text)
            else:
                skipped_lang += 1

    return {
        "texts": texts,
        "observed": observed,
        "skipped_lang": skipped_lang,
        "lang_counts": lang_counts,
        "window_seconds": round(time.monotonic() - started, 1),
    }


def histogram(values: np.ndarray) -> list[dict[str, float]]:
    counts, _ = np.histogram(values, bins=HISTOGRAM_EDGES)
    total = max(1, len(values))
    return [
        {
            "bin": f"{HISTOGRAM_EDGES[i]:.1f}-{HISTOGRAM_EDGES[i + 1]:.1f}",
            "count": int(counts[i]),
            "share": round(counts[i] / total, 4),
        }
        for i in range(len(counts))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--max-posts", type=int, default=20000)
    parser.add_argument("--model-path", default="audit_outputs/fraud_labeler_v2.joblib")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown-out")
    parser.add_argument("--lab-summary")
    args = parser.parse_args()

    collected = asyncio.run(collect_texts(args.seconds, args.max_posts))
    texts: list[str] = collected.pop("texts")  # type: ignore[assignment]
    if len(texts) < 100:
        print(json.dumps({"error": "insufficient stream sample", "scored": len(texts)}))
        return 1

    artifact = joblib.load(args.model_path)
    pipeline, thresholds = artifact["model"], artifact["thresholds"]
    probabilities = pipeline.predict_proba(texts)[:, 1]

    actions: dict[str, int] = {}
    rule_counts: dict[str, int] = {}
    policy_scores = []
    for text, probability in zip(texts, probabilities):
        action = v2.decision_for_text(text, float(probability), thresholds)
        actions[action] = actions.get(action, 0) + 1
        evidence = v2.policy_evidence(text)
        policy_scores.append(evidence["score"])
        for rule in evidence["rules"]:
            if rule["matched"]:
                rule_counts[rule["name"]] = rule_counts.get(rule["name"], 0) + 1
    policy_scores_arr = np.asarray(policy_scores, dtype=float)

    # Aggregates only from here on; the raw texts leave scope unpersisted.
    del texts

    scored = int(len(probabilities))
    report = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
        "source": "Bluesky Jetstream public firehose (app.bsky.feed.post creates)",
        "privacy": (
            "Aggregates only. Post text was scored in memory and discarded; no "
            "text, handle, DID, URI, or per-post record was persisted."
        ),
        "window": {
            "seconds": collected["window_seconds"],
            "postsObserved": collected["observed"],
            "postsScored": scored,
            "scoredLanguages": sorted(SCORED_LANGS),
            "skippedOtherLanguages": collected["skipped_lang"],
            "languageMixTop": dict(
                sorted(
                    collected["lang_counts"].items(),  # type: ignore[union-attr]
                    key=lambda item: -item[1],
                )[:8]
            ),
        },
        "thresholds": {k: float(v) for k, v in thresholds.items()},
        "decisionTierShares": {
            action: {"count": count, "share": round(count / scored, 4)}
            for action, count in sorted(actions.items(), key=lambda kv: -kv[1])
        },
        "modelScore": {
            "mean": round(float(probabilities.mean()), 4),
            "p50": round(float(np.percentile(probabilities, 50)), 4),
            "p90": round(float(np.percentile(probabilities, 90)), 4),
            "p99": round(float(np.percentile(probabilities, 99)), 4),
            "histogram": histogram(probabilities),
        },
        "policyScore": {
            "mean": round(float(policy_scores_arr.mean()), 4),
            "p99": round(float(np.percentile(policy_scores_arr, 99)), 4),
            "histogram": histogram(policy_scores_arr),
        },
        "topMatchedRules": dict(
            sorted(rule_counts.items(), key=lambda kv: -kv[1])[:6]
        ),
        "interpretation": (
            "Real-traffic queue load at the shipped thresholds. The review-tier "
            "share here is measured on live posts, replacing the synthetic "
            "flagged-share assumption in the scale simulation. Tier shares are "
            "queue load, not prevalence: prevalence on real traffic requires "
            "labeled random sampling."
        ),
    }

    Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown_out:
        review_share = report["decisionTierShares"].get("send_to_human_review", {})
        lines = [
            "# Live Stream Calibration — Real Firehose, Aggregates Only",
            "",
            f"{scored:,} posts scored from {collected['observed']:,} observed in "
            f"{collected['window_seconds']:.0f}s of the public Bluesky Jetstream "
            f"firehose · generated {report['generatedAt']}",
            "",
            report["privacy"],
            "",
            "| Decision tier | Count | Share |",
            "| --- | --- | --- |",
        ]
        for action, row in report["decisionTierShares"].items():
            lines.append(f"| {action} | {row['count']:,} | {row['share']:.2%} |")
        lines += [
            "",
            f"Model score p50 {report['modelScore']['p50']:.3f} · p90 "
            f"{report['modelScore']['p90']:.3f} · p99 {report['modelScore']['p99']:.3f}. "
            f"Review-tier share {review_share.get('share', 0):.2%} of live traffic.",
            "",
            report["interpretation"],
            "",
        ]
        Path(args.markdown_out).write_text("\n".join(lines), encoding="utf-8")
    if args.lab_summary:
        Path(args.lab_summary).write_text(
            "export const liveStreamCalibration = "
            + json.dumps(report, indent=2)
            + ";\n",
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "postsObserved": collected["observed"],
                "postsScored": scored,
                "reviewTierShare": report["decisionTierShares"]
                .get("send_to_human_review", {})
                .get("share", 0),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
