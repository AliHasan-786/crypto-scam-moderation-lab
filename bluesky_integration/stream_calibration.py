"""Create an aggregate-only, provenance-stamped Bluesky routing snapshot.

Post content is scored in memory and discarded. This command never writes text,
account identifiers, URIs, or per-post decisions. It measures routing load for a
bounded language-filtered sample, not fraud prevalence or classifier accuracy.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import policy_proposal_labeler_v2 as v2  # noqa: E402

JETSTREAM_URL = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


async def collect(seconds: float, max_posts: int, languages: set[str]) -> dict:
    import websockets

    texts: list[str] = []
    language_counts: dict[str, int] = {}
    non_empty_observed = 0
    skipped_language = 0
    started = datetime.now(timezone.utc)
    deadline = time.monotonic() + seconds
    async with websockets.connect(JETSTREAM_URL, max_size=2**22) as socket:
        while time.monotonic() < deadline and len(texts) < max_posts:
            try:
                raw = await asyncio.wait_for(socket.recv(), timeout=5)
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
            non_empty_observed += 1
            language = str((record.get("langs") or ["und"])[0] or "und").split("-")[0].lower()
            language_counts[language] = language_counts.get(language, 0) + 1
            if language in languages:
                texts.append(text)
            else:
                skipped_language += 1
    ended = datetime.now(timezone.utc)
    return {
        "texts": texts,
        "startedAt": started.isoformat(),
        "endedAt": ended.isoformat(),
        "seconds": round((ended - started).total_seconds(), 1),
        "nonEmptyPostsObserved": non_empty_observed,
        "skippedOtherLanguages": skipped_language,
        "languageCounts": language_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--lab-summary")
    parser.add_argument("--seconds", type=float, default=240)
    parser.add_argument("--max-posts", type=int, default=20_000)
    parser.add_argument("--languages", default="en,es")
    parser.add_argument("--model-path", default="audit_outputs/fraud_labeler_v2.joblib")
    parser.add_argument("--operator", required=True)
    parser.add_argument("--terms-review-date", required=True, help="ISO date of public-relay terms review.")
    parser.add_argument("--kill-switch-owner", required=True)
    args = parser.parse_args()

    languages = {value.strip().lower() for value in args.languages.split(",") if value.strip()}
    collected = asyncio.run(collect(args.seconds, args.max_posts, languages))
    texts = collected.pop("texts")
    if len(texts) < 100:
        raise SystemExit(f"Insufficient scored sample: {len(texts)}")

    model_path = ROOT / args.model_path
    artifact = joblib.load(model_path)
    model, thresholds = artifact["model"], artifact["thresholds"]
    probabilities = model.predict_proba(texts)[:, 1]
    actions: dict[str, int] = {}
    rules: dict[str, int] = {}
    for text, probability in zip(texts, probabilities):
        action = v2.decision_for_text(text, float(probability), thresholds)
        actions[action] = actions.get(action, 0) + 1
        for rule in v2.policy_evidence(text)["rules"]:
            if rule["matched"]:
                rules[rule["name"]] = rules.get(rule["name"], 0) + 1
    del texts

    scored = int(len(probabilities))
    intermediate = actions.get("send_to_human_review", 0)
    human_operated = sum(count for action, count in actions.items() if action != "no_label")
    report = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
        "source": "Public Bluesky Jetstream relay, app.bsky.feed.post create events",
        "scope": "Bounded EN/ES routing snapshot; not prevalence, accuracy, or all-platform traffic.",
        "collection": {
            **collected,
            "postsScored": scored,
            "scoredLanguages": sorted(languages),
            "endpoint": JETSTREAM_URL,
            "operator": args.operator,
            "termsReviewDate": args.terms_review_date,
            "killSwitchOwner": args.kill_switch_owner,
        },
        "provenance": {
            "codeCommit": git_commit(),
            "modelSha256": sha256(model_path),
            "retention": "Aggregate report only; live text and identifiers were discarded in memory.",
        },
        "thresholds": {key: float(value) for key, value in thresholds.items()},
        "routing": {
            "actionCounts": actions,
            "intermediateReview": {"count": intermediate, "share": round(intermediate / scored, 4)},
            "humanOperatedQueue": {"count": human_operated, "share": round(human_operated / scored, 4)},
        },
        "modelScore": {
            "p50": round(float(np.percentile(probabilities, 50)), 4),
            "p90": round(float(np.percentile(probabilities, 90)), 4),
            "p99": round(float(np.percentile(probabilities, 99)), 4),
        },
        "topMatchedRules": dict(sorted(rules.items(), key=lambda item: -item[1])[:6]),
    }
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.lab_summary:
        Path(args.lab_summary).write_text(
            "export const liveStreamCalibration = " + json.dumps(report, indent=2) + ";\n",
            encoding="utf-8",
        )
    print(json.dumps({"postsScored": scored, "humanOperatedQueueShare": report["routing"]["humanOperatedQueue"]["share"]}, indent=2))


if __name__ == "__main__":
    main()
