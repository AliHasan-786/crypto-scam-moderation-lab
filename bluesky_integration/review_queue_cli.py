from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bluesky_integration.campaign_graph import export_campaign_graph  # noqa: E402
from bluesky_integration.review_store import (  # noqa: E402
    export_lab_queue,
    init_db,
    list_items,
    update_review_decision,
    upsert_many,
)


DEFAULT_DB = ROOT / "audit_outputs" / "live_review_queue.sqlite"
DEFAULT_EXPORT = ROOT / "crypto-scam-lab" / "data" / "liveReviewQueue.js"
DEFAULT_GRAPH_JSON = ROOT / "audit_outputs" / "campaign_graph.json"
DEFAULT_GRAPH_EXPORT = ROOT / "crypto-scam-lab" / "data" / "campaignGraph.js"
DEFAULT_MODEL = ROOT / "audit_outputs" / "fraud_labeler_v2.joblib"

DEMO_WALLET = "0x5afe00000000000000000000000000000000feed"


DEMO_POSTS = [
    {
        "uri": "demo://crypto-scam-lab/high-confidence-airdrop",
        "cid": "demo-airdrop",
        "did": "did:example:demo-airdrop",
        "author": {"handle": "btc-rewards-demo.bsky.social", "did": "did:example:demo-airdrop"},
        "createdAt": "2026-06-07T00:00:00Z",
        "text": (
            "Official Bitcoin airdrop: connect your wallet at secure-btc-airdrop[.]xyz "
            f"to claim free BTC before the window closes. Support wallet: {DEMO_WALLET}."
        ),
    },
    {
        "uri": "demo://crypto-scam-lab/mirror-airdrop",
        "cid": "demo-mirror-airdrop",
        "did": "did:example:demo-mirror-airdrop",
        "author": {"handle": "btc-claims-demo.bsky.social", "did": "did:example:demo-mirror-airdrop"},
        "createdAt": "2026-06-07T00:03:00Z",
        "text": (
            "Verified BTC rewards round is closing. Claim at secure-btc-airdrop[.]xyz "
            "and connect wallet before the final warning."
        ),
    },
    {
        "uri": "demo://crypto-scam-lab/reused-wallet",
        "cid": "demo-reused-wallet",
        "did": "did:example:demo-reused-wallet",
        "author": {"handle": "token-support-demo.bsky.social", "did": "did:example:demo-reused-wallet"},
        "createdAt": "2026-06-07T00:06:00Z",
        "text": (
            "Tesla crypto event support says deposits to "
            f"{DEMO_WALLET} are required before the bonus release fee clears."
        ),
    },
    {
        "uri": "demo://crypto-scam-lab/recovery-review",
        "cid": "demo-recovery",
        "did": "did:example:demo-recovery",
        "author": {"handle": "wallet-help-demo.bsky.social", "did": "did:example:demo-recovery"},
        "createdAt": "2026-06-07T00:00:00Z",
        "text": "A recovery service says they charge only after funds are recovered. Has anyone used them safely?",
    },
    {
        "uri": "demo://crypto-scam-lab/consumer-warning",
        "cid": "demo-warning",
        "did": "did:example:demo-warning",
        "author": {"handle": "consumer-safety-demo.bsky.social", "did": "did:example:demo-warning"},
        "createdAt": "2026-06-07T00:00:00Z",
        "text": "Reminder: do not send crypto to people promising guaranteed returns. Social media investment scams are common.",
    },
]


def print_items(items: list[dict]) -> None:
    rows = []
    for item in items:
        rows.append(
            {
                "uri": item["uri"],
                "status": item["status"],
                "decision": item["reviewerDecision"],
                "probability": round(float(item["probability"]), 3),
                "action": item["action"],
                "source": item["source"],
                "text": item["text"][:140],
            }
        )
    print(json.dumps(rows, indent=2, ensure_ascii=False))


def seed_demo(db_path: Path, model_path: Path) -> list[str]:
    from bluesky_integration.jetstream_monitor import load_model, score_post

    model, thresholds = load_model(model_path)
    scored = [score_post(post, model, thresholds) for post in DEMO_POSTS]
    return upsert_many(db_path, scored, source="demo", source_query="seed-demo")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local SQLite reviewer queue for the Bluesky scam lab.")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize the SQLite review store.")

    list_parser = subparsers.add_parser("list", help="List review items.")
    list_parser.add_argument("--status", action="append", default=[])
    list_parser.add_argument("--limit", type=int, default=25)

    export_parser = subparsers.add_parser("export", help="Export queue data to the browser lab.")
    export_parser.add_argument("--out", default=str(DEFAULT_EXPORT))
    export_parser.add_argument("--status", action="append", default=[])
    export_parser.add_argument("--limit", type=int, default=80)

    graph_parser = subparsers.add_parser("graph", help="Export entity/campaign graph data.")
    graph_parser.add_argument("--out", default=str(DEFAULT_GRAPH_JSON))
    graph_parser.add_argument("--lab-summary", default=str(DEFAULT_GRAPH_EXPORT))
    graph_parser.add_argument("--limit", type=int, default=250)

    decide_parser = subparsers.add_parser("decide", help="Record a reviewer decision.")
    decide_parser.add_argument("--uri", required=True)
    decide_parser.add_argument(
        "--status",
        choices=["new", "review", "labeled", "escalated", "dismissed", "appealed", "reversed"],
        required=True,
    )
    decide_parser.add_argument(
        "--decision",
        choices=["fraud", "not_fraud", "needs_more_context", "appeal_upheld", "appeal_reversed"],
        required=True,
    )
    decide_parser.add_argument("--notes", default="")
    decide_parser.add_argument("--reviewer-id", default="local-reviewer")

    seed_parser = subparsers.add_parser("seed-demo", help="Seed sanitized demo queue items.")
    seed_parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    seed_parser.add_argument("--export-out", default=str(DEFAULT_EXPORT))

    args = parser.parse_args()
    db_path = Path(args.db)

    if args.command == "init":
        init_db(db_path)
        print(json.dumps({"db": str(db_path), "initialized": True}, indent=2))
    elif args.command == "list":
        print_items(list_items(db_path, statuses=args.status, limit=args.limit))
    elif args.command == "export":
        summary = export_lab_queue(db_path, args.out, statuses=args.status, limit=args.limit)
        print(json.dumps({"out": args.out, "count": summary["count"]}, indent=2))
    elif args.command == "graph":
        graph = export_campaign_graph(db_path, args.out, lab_summary_path=args.lab_summary, limit=args.limit)
        print(
            json.dumps(
                {
                    "out": args.out,
                    "labSummary": args.lab_summary,
                    "items": graph["itemCount"],
                    "entities": graph["entityCount"],
                    "campaigns": graph["campaignCount"],
                },
                indent=2,
            )
        )
    elif args.command == "decide":
        update_review_decision(
            db_path,
            args.uri,
            status=args.status,
            decision=args.decision,
            notes=args.notes,
            reviewer_id=args.reviewer_id,
        )
        print(json.dumps({"uri": args.uri, "status": args.status, "decision": args.decision}, indent=2))
    elif args.command == "seed-demo":
        uris = seed_demo(db_path, Path(args.model_path))
        summary = export_lab_queue(db_path, args.export_out)
        print(json.dumps({"seeded": uris, "exported": args.export_out, "count": summary["count"]}, indent=2))


if __name__ == "__main__":
    main()
