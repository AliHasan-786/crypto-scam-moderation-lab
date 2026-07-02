from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

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
from bluesky_integration.review_store import export_lab_queue, upsert_many  # noqa: E402


DEFAULT_PDS = "https://bsky.social"
DEFAULT_APPVIEW = "https://bsky.social"
DEFAULT_MODEL = ROOT / "audit_outputs" / "fraud_labeler_v2.joblib"
DEFAULT_DB = ROOT / "audit_outputs" / "live_review_queue.sqlite"
DEFAULT_LAB_EXPORT = ROOT / "crypto-scam-lab" / "data" / "liveReviewQueue.js"


def request_json(url: str, *, method: str = "GET", token: str | None = None, body: dict | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {detail}") from exc


def create_session(handle: str, app_password: str, pds: str) -> dict:
    return request_json(
        f"{pds.rstrip('/')}/xrpc/com.atproto.server.createSession",
        method="POST",
        body={"identifier": handle, "password": app_password},
    )


def search_posts(query: str, token: str, appview: str, *, limit: int = 25, sort: str = "latest") -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "limit": limit, "sort": sort})
    data = request_json(
        f"{appview.rstrip('/')}/xrpc/app.bsky.feed.searchPosts?{params}",
        token=token,
    )
    return data.get("posts", [])


def score_posts(posts: list[dict], model_path: Path) -> list[dict]:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Missing model artifact: {model_path}. Run policy_proposal_labeler_v2.py evaluate first."
        )
    register_pickle_compatibility()
    artifact = joblib.load(model_path)
    model = artifact["model"]
    thresholds = artifact.get(
        "thresholds",
        {
            "review": artifact["threshold"],
            "label": artifact["threshold"],
            "high_confidence": artifact["threshold"],
        },
    )

    texts = [post.get("record", {}).get("text", "") for post in posts]
    probabilities = model.predict_proba(texts)[:, 1] if texts else []
    scored = []
    for post, text, probability in zip(posts, texts, probabilities):
        scored.append(
            {
                "uri": post.get("uri"),
                "cid": post.get("cid"),
                "author": {
                    "handle": post.get("author", {}).get("handle"),
                    "did": post.get("author", {}).get("did"),
                    "displayName": post.get("author", {}).get("displayName"),
                },
                "indexedAt": post.get("indexedAt"),
                "text": text,
                "probability": float(probability),
                "thresholds": thresholds,
                "action": decision_for_text(text, float(probability), thresholds),
                "policy_evidence": policy_evidence(text),
                "public_label_evidence": public_label_evidence(text),
                "contextual_safety_evidence": contextual_safety_evidence(text),
            }
        )
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Bluesky search ingestion for local scam scoring.")
    parser.add_argument("--query", default="crypto airdrop wallet")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--sort", choices=["latest", "top"], default="latest")
    parser.add_argument("--pds", default=os.environ.get("BSKY_PDS", DEFAULT_PDS))
    parser.add_argument("--appview", default=os.environ.get("BSKY_APPVIEW", DEFAULT_APPVIEW))
    parser.add_argument("--handle", default=os.environ.get("BSKY_HANDLE", ""))
    parser.add_argument("--app-password", default=os.environ.get("BSKY_APP_PASSWORD", ""))
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--out", default="")
    parser.add_argument("--db", default="")
    parser.add_argument("--export-lab-data", default="")
    args = parser.parse_args()

    if not args.handle or not args.app_password:
        raise SystemExit(
            "Set BSKY_HANDLE and BSKY_APP_PASSWORD, or pass --handle and --app-password. "
            "Use a Bluesky app password, not your main password."
        )

    session = create_session(args.handle, args.app_password, args.pds)
    posts = search_posts(args.query, session["accessJwt"], args.appview, limit=args.limit, sort=args.sort)
    scored = score_posts(posts, Path(args.model_path))
    stored_uris: list[str] = []
    if args.db:
        stored_uris = upsert_many(args.db, scored, source="search", source_query=args.query)
        if args.export_lab_data:
            export_lab_queue(args.db, args.export_lab_data)
    rendered = json.dumps(
        {
            "query": args.query,
            "count": len(scored),
            "stored_count": len(stored_uris),
            "db": args.db,
            "results": scored,
        },
        ensure_ascii=False,
        indent=2,
    )
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
