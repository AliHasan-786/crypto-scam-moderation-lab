from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from policy_proposal_labeler_v2 import (  # noqa: E402
    contextual_safety_evidence,
    decision_for_text,
    policy_evidence,
    public_label_evidence,
    register_pickle_compatibility,
)
from bluesky_integration.review_store import export_lab_queue, upsert_scored_item  # noqa: E402


DEFAULT_ENDPOINT = "wss://jetstream2.us-east.bsky.network/subscribe"
DEFAULT_MODEL = ROOT / "audit_outputs" / "fraud_labeler_v2.joblib"
DEFAULT_DB = ROOT / "audit_outputs" / "live_review_queue.sqlite"
DEFAULT_LAB_EXPORT = ROOT / "crypto-scam-lab" / "data" / "liveReviewQueue.js"
DEFAULT_KEYWORDS = (
    "crypto,bitcoin,btc,ethereum,eth,airdrop,wallet,claim,reward,token,"
    "usdt,binance,coinbase,metamask,web3,nft,investment"
)


def load_model(model_path: Path) -> tuple[object, dict]:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Missing model artifact: {model_path}. Run policy_proposal_labeler_v2.py evaluate first."
        )
    register_pickle_compatibility()
    artifact = joblib.load(model_path)
    thresholds = artifact.get(
        "thresholds",
        {
            "review": artifact["threshold"],
            "label": artifact["threshold"],
            "high_confidence": artifact["threshold"],
        },
    )
    return artifact["model"], thresholds


def parse_keywords(raw_keywords: str) -> tuple[str, ...]:
    return tuple(keyword.strip().lower() for keyword in raw_keywords.split(",") if keyword.strip())


def text_has_keyword(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def post_uri(did: str, commit: dict) -> str | None:
    collection = commit.get("collection")
    rkey = commit.get("rkey")
    if not did or not collection or not rkey:
        return None
    return f"at://{did}/{collection}/{rkey}"


def extract_post(event: dict) -> dict | None:
    if event.get("kind") != "commit":
        return None
    commit = event.get("commit") or {}
    if commit.get("collection") != "app.bsky.feed.post":
        return None
    if commit.get("operation") != "create":
        return None
    record = commit.get("record") or {}
    text = record.get("text")
    if not isinstance(text, str) or not text.strip():
        return None
    did = event.get("did")
    return {
        "uri": post_uri(did, commit),
        "cid": commit.get("cid"),
        "did": did,
        "createdAt": record.get("createdAt"),
        "time_us": event.get("time_us"),
        "text": text,
    }


def score_post(post: dict, model: object, thresholds: dict) -> dict:
    probability = float(model.predict_proba([post["text"]])[0, 1])
    return {
        **post,
        "probability": probability,
        "thresholds": thresholds,
        "action": decision_for_text(post["text"], probability, thresholds),
        "policy_evidence": policy_evidence(post["text"]),
        "public_label_evidence": public_label_evidence(post["text"]),
        "contextual_safety_evidence": contextual_safety_evidence(post["text"]),
        "scoredAt": datetime.now(timezone.utc).isoformat(),
    }


async def monitor(args: argparse.Namespace) -> dict:
    try:
        import websockets
    except ImportError as exc:
        raise SystemExit("Install websockets to use the Jetstream monitor: pip install websockets") from exc

    model, thresholds = load_model(Path(args.model_path))
    keywords = parse_keywords(args.keywords)
    params = urlencode({"wantedCollections": "app.bsky.feed.post"})
    endpoint = f"{args.endpoint.rstrip('/')}?{params}"
    out_path = Path(args.out) if args.out else None
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    seen_events = 0
    matched_posts = 0
    scored_posts = 0
    stored_posts = 0
    started_at = datetime.now(timezone.utc)

    async with websockets.connect(endpoint, ping_interval=20, ping_timeout=20, max_queue=256) as websocket:
        while seen_events < args.max_events and scored_posts < args.max_matches:
            try:
                raw_message = await asyncio.wait_for(websocket.recv(), timeout=args.timeout_seconds)
            except asyncio.TimeoutError:
                break

            seen_events += 1
            try:
                event = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            post = extract_post(event)
            if not post:
                continue
            if keywords and not text_has_keyword(post["text"], keywords):
                continue

            matched_posts += 1
            scored = score_post(post, model, thresholds)
            scored_posts += 1
            if args.db:
                upsert_scored_item(args.db, scored, source="jetstream", source_query=args.keywords)
                stored_posts += 1
            rendered = json.dumps(scored, ensure_ascii=False)
            if out_path:
                with out_path.open("a", encoding="utf-8") as handle:
                    handle.write(rendered + "\n")
            if args.print_matches:
                print(rendered)

    if args.db and args.export_lab_data:
        export_lab_queue(args.db, args.export_lab_data)

    return {
        "startedAt": started_at.isoformat(),
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "keywords": keywords,
        "eventsSeen": seen_events,
        "keywordMatches": matched_posts,
        "scoredPosts": scored_posts,
        "storedPosts": stored_posts,
        "db": args.db,
        "out": str(out_path) if out_path else "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read-only AT Protocol Jetstream monitor for local crypto-scam scoring."
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--keywords", default=DEFAULT_KEYWORDS)
    parser.add_argument("--max-events", type=int, default=1000)
    parser.add_argument("--max-matches", type=int, default=25)
    parser.add_argument("--timeout-seconds", type=float, default=45)
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--out", default=str(ROOT / "audit_outputs" / "live_bsky_jetstream_sample.jsonl"))
    parser.add_argument("--db", default="")
    parser.add_argument("--export-lab-data", default="")
    parser.add_argument("--print-matches", action="store_true")
    args = parser.parse_args()

    summary = asyncio.run(monitor(args))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
