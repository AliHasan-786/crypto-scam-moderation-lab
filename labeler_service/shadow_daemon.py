"""Offline harness for a future observation-only shadow service.

The module accepts fixture events only. It has no relay client and no outbound
write path; a live transport cannot be added without passing the shadow gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_enabled() -> None:
    if os.environ.get("SHADOW_ENABLED", "").lower() != "true":
        raise RuntimeError("Shadow processing is disabled. Set SHADOW_ENABLED=true for fixture-only testing.")
    if os.environ.get("SHADOW_KILL_SWITCH", "").lower() in {"1", "true", "on"}:
        raise RuntimeError("Shadow kill switch is active.")


def init_state(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute(
        """CREATE TABLE IF NOT EXISTS shadow_decisions (
        event_hash TEXT PRIMARY KEY, observed_at TEXT NOT NULL, action TEXT NOT NULL,
        score REAL NOT NULL, matched_rules_json TEXT NOT NULL
        )"""
    )
    return connection


def event_hash(event: dict) -> str:
    """Use a non-reversible local dedupe key; never persist content or identity."""
    material = str(event.get("event_id") or event.get("text") or "")
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def process_fixture_events(
    events: list[dict],
    *,
    state_path: Path,
    max_decisions_per_hour: int,
    score: Callable[[str], dict],
    protected_context_guard: Callable[[], bool],
) -> dict:
    """Process authored fixtures with a capped, aggregate-only local state."""
    require_enabled()
    if not protected_context_guard():
        raise RuntimeError("Protected-context guard failed; shadow processing aborted.")
    if max_decisions_per_hour <= 0:
        raise ValueError("max_decisions_per_hour must be positive")
    actions: Counter[str] = Counter()
    matched_rules: Counter[str] = Counter()
    capped = False
    processed = 0
    with init_state(state_path) as connection:
        for event in events:
            require_enabled()
            text = str(event.get("text") or "").strip()
            if not text:
                continue
            result = score(text)
            action = str(result.get("action", "no_label"))
            if action != "no_label" and sum(value for key, value in actions.items() if key != "no_label") >= max_decisions_per_hour:
                capped = True
                break
            rules = [str(rule) for rule in result.get("matched_rules", [])]
            connection.execute(
                "INSERT OR IGNORE INTO shadow_decisions VALUES (?, ?, ?, ?, ?)",
                (event_hash(event), utc_now(), action, float(result.get("score", 0.0)), json.dumps(rules)),
            )
            processed += 1
            actions[action] += 1
            matched_rules.update(rules)
    return {
        "mode": "fixture_only",
        "processed": processed,
        "capped": capped,
        "actionCounts": dict(actions),
        "topMatchedRules": dict(matched_rules.most_common(6)),
        "retention": "Hashed event key, route, score, and rule names only; no text, handles, DIDs, URIs, or network writes.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="Authored local JSON fixture; live relay input is intentionally unsupported.")
    parser.add_argument("--state", default="labeler_service/state.sqlite")
    parser.add_argument("--max-decisions-per-hour", type=int, default=20)
    args = parser.parse_args()
    events = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    if not isinstance(events, list):
        raise SystemExit("Fixture must be a JSON list")
    # A production scorer is intentionally not wired here until the gate permits it.
    raise SystemExit("Build-only harness: invoke process_fixture_events from tests with an approved scorer.")


if __name__ == "__main__":
    main()
