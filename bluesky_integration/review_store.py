from __future__ import annotations

import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from bluesky_integration.entity_extractors import ExtractedEntity, entity_id, extract_entities


VALID_STATUSES = {
    "new",
    "review",
    "labeled",
    "escalated",
    "dismissed",
    "appealed",
    "reversed",
}

VALID_DECISIONS = {
    "fraud",
    "not_fraud",
    "needs_more_context",
    "appeal_upheld",
    "appeal_reversed",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def init_db(db_path: str | Path) -> None:
    with connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS review_items (
                uri TEXT PRIMARY KEY,
                cid TEXT,
                source TEXT NOT NULL,
                source_query TEXT,
                author_handle TEXT,
                author_did TEXT,
                author_display_name TEXT,
                created_at TEXT,
                indexed_at TEXT,
                ingested_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                text TEXT NOT NULL,
                probability REAL NOT NULL,
                action TEXT NOT NULL,
                thresholds_json TEXT NOT NULL,
                policy_evidence_json TEXT NOT NULL,
                public_label_evidence_json TEXT NOT NULL,
                contextual_safety_evidence_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                reviewer_decision TEXT,
                reviewer_notes TEXT,
                reviewer_id TEXT,
                reviewed_at TEXT,
                duplicate_count INTEGER NOT NULL DEFAULT 1
            );

            CREATE INDEX IF NOT EXISTS idx_review_items_status
                ON review_items(status, probability DESC);

            CREATE INDEX IF NOT EXISTS idx_review_items_source
                ON review_items(source, ingested_at DESC);

            CREATE TABLE IF NOT EXISTS review_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uri TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(uri) REFERENCES review_items(uri) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS review_entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                value TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                observation_count INTEGER NOT NULL DEFAULT 1,
                max_risk_weight REAL NOT NULL DEFAULT 0,
                UNIQUE(entity_type, value)
            );

            CREATE INDEX IF NOT EXISTS idx_review_entities_type_value
                ON review_entities(entity_type, value);

            CREATE TABLE IF NOT EXISTS review_item_entities (
                uri TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                raw_value TEXT,
                source TEXT NOT NULL,
                risk_weight REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                PRIMARY KEY(uri, entity_id),
                FOREIGN KEY(uri) REFERENCES review_items(uri) ON DELETE CASCADE,
                FOREIGN KEY(entity_id) REFERENCES review_entities(entity_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_review_item_entities_entity
                ON review_item_entities(entity_id, uri);
            """
        )


def json_dumps(value: object) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True)


def stable_uri(scored: dict) -> str:
    uri = scored.get("uri")
    if uri:
        return str(uri)
    cid = scored.get("cid")
    if cid:
        return f"cid:{cid}"
    text = str(scored.get("text", ""))
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"local:{digest}"


def author_fields(scored: dict) -> dict[str, str | None]:
    author = scored.get("author") if isinstance(scored.get("author"), dict) else {}
    return {
        "author_handle": author.get("handle"),
        "author_did": author.get("did") or scored.get("did"),
        "author_display_name": author.get("displayName"),
    }


def extract_scored_entities(scored: dict, author: dict[str, str | None]) -> list[ExtractedEntity]:
    return extract_entities(
        scored.get("text", ""),
        author_handle=author.get("author_handle"),
        author_did=author.get("author_did"),
        author_display_name=author.get("author_display_name"),
    )


def replace_item_entities(
    connection: sqlite3.Connection,
    uri: str,
    entities: Iterable[ExtractedEntity],
    now: str,
    *,
    count_observation: bool = True,
) -> None:
    connection.execute("DELETE FROM review_item_entities WHERE uri = ?", (uri,))
    for entity in entities:
        eid = entity_id(entity.entity_type, entity.value)
        connection.execute(
            """
            INSERT INTO review_entities (
                entity_id, entity_type, value, first_seen, last_seen,
                observation_count, max_risk_weight
            )
            VALUES (?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(entity_id) DO UPDATE SET
                last_seen = excluded.last_seen,
                observation_count = review_entities.observation_count + ?,
                max_risk_weight = MAX(review_entities.max_risk_weight, excluded.max_risk_weight)
            """,
            (
                eid,
                entity.entity_type,
                entity.value,
                now,
                now,
                entity.risk_weight,
                1 if count_observation else 0,
            ),
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO review_item_entities (
                uri, entity_id, raw_value, source, risk_weight, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (uri, eid, entity.raw, entity.source, entity.risk_weight, now),
        )


def refresh_item_entities(db_path: str | Path, *, limit: int | None = None) -> int:
    init_db(db_path)
    query = "SELECT * FROM review_items ORDER BY ingested_at DESC"
    params: tuple[object, ...] = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)
    refreshed = 0
    now = utc_now()
    with connect(db_path) as connection:
        rows = connection.execute(query, params).fetchall()
        for row in rows:
            author = {
                "author_handle": row["author_handle"],
                "author_did": row["author_did"],
                "author_display_name": row["author_display_name"],
            }
            entities = extract_entities(
                row["text"],
                author_handle=author["author_handle"],
                author_did=author["author_did"],
                author_display_name=author["author_display_name"],
            )
            replace_item_entities(connection, row["uri"], entities, now, count_observation=False)
            refreshed += 1
    return refreshed


def upsert_scored_item(
    db_path: str | Path,
    scored: dict,
    *,
    source: str,
    source_query: str = "",
    status: str = "new",
) -> str:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status {status!r}; expected one of {sorted(VALID_STATUSES)}")
    init_db(db_path)
    now = utc_now()
    uri = stable_uri(scored)
    author = author_fields(scored)
    created_at = scored.get("createdAt")
    indexed_at = scored.get("indexedAt") or scored.get("scoredAt")
    payload = {
        "uri": uri,
        "cid": scored.get("cid"),
        "source": source,
        "source_query": source_query,
        **author,
        "created_at": created_at,
        "indexed_at": indexed_at,
        "ingested_at": now,
        "updated_at": now,
        "text": scored.get("text", ""),
        "probability": float(scored.get("probability", 0.0)),
        "action": scored.get("action", "no_label"),
        "thresholds_json": json_dumps(scored.get("thresholds")),
        "policy_evidence_json": json_dumps(scored.get("policy_evidence")),
        "public_label_evidence_json": json_dumps(scored.get("public_label_evidence")),
        "contextual_safety_evidence_json": json_dumps(scored.get("contextual_safety_evidence")),
        "status": status,
    }
    entities = extract_scored_entities(scored, author)
    with connect(db_path) as connection:
        exists = connection.execute(
            "SELECT uri FROM review_items WHERE uri = ?",
            (uri,),
        ).fetchone()
        if exists:
            connection.execute(
                """
                UPDATE review_items
                SET cid = :cid,
                    source = :source,
                    source_query = :source_query,
                    author_handle = :author_handle,
                    author_did = :author_did,
                    author_display_name = :author_display_name,
                    created_at = :created_at,
                    indexed_at = :indexed_at,
                    updated_at = :updated_at,
                    text = :text,
                    probability = :probability,
                    action = :action,
                    thresholds_json = :thresholds_json,
                    policy_evidence_json = :policy_evidence_json,
                    public_label_evidence_json = :public_label_evidence_json,
                    contextual_safety_evidence_json = :contextual_safety_evidence_json,
                    duplicate_count = duplicate_count + 1
                WHERE uri = :uri
                """,
                payload,
            )
            event_type = "upsert_duplicate"
        else:
            connection.execute(
                """
                INSERT INTO review_items (
                    uri, cid, source, source_query, author_handle, author_did,
                    author_display_name, created_at, indexed_at, ingested_at, updated_at,
                    text, probability, action, thresholds_json, policy_evidence_json,
                    public_label_evidence_json, contextual_safety_evidence_json, status
                )
                VALUES (
                    :uri, :cid, :source, :source_query, :author_handle, :author_did,
                    :author_display_name, :created_at, :indexed_at, :ingested_at, :updated_at,
                    :text, :probability, :action, :thresholds_json, :policy_evidence_json,
                    :public_label_evidence_json, :contextual_safety_evidence_json, :status
                )
                """,
                payload,
            )
            event_type = "ingested"
        connection.execute(
            """
            INSERT INTO review_events(uri, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (uri, event_type, json_dumps({"source": source, "source_query": source_query}), now),
        )
        replace_item_entities(connection, uri, entities, now)
    return uri


def upsert_many(
    db_path: str | Path,
    scored_items: Iterable[dict],
    *,
    source: str,
    source_query: str = "",
    status: str = "new",
) -> list[str]:
    return [
        upsert_scored_item(db_path, item, source=source, source_query=source_query, status=status)
        for item in scored_items
    ]


def update_review_decision(
    db_path: str | Path,
    uri: str,
    *,
    status: str,
    decision: str,
    notes: str = "",
    reviewer_id: str = "local-reviewer",
) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status {status!r}; expected one of {sorted(VALID_STATUSES)}")
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid decision {decision!r}; expected one of {sorted(VALID_DECISIONS)}")
    now = utc_now()
    with connect(db_path) as connection:
        row = connection.execute("SELECT uri FROM review_items WHERE uri = ?", (uri,)).fetchone()
        if not row:
            raise KeyError(f"No review item found for URI: {uri}")
        connection.execute(
            """
            UPDATE review_items
            SET status = ?,
                reviewer_decision = ?,
                reviewer_notes = ?,
                reviewer_id = ?,
                reviewed_at = ?,
                updated_at = ?
            WHERE uri = ?
            """,
            (status, decision, notes, reviewer_id, now, now, uri),
        )
        connection.execute(
            """
            INSERT INTO review_events(uri, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                uri,
                "review_decision",
                json_dumps(
                    {
                        "status": status,
                        "decision": decision,
                        "notes": notes,
                        "reviewer_id": reviewer_id,
                    }
                ),
                now,
            ),
        )


def parse_row(row: sqlite3.Row) -> dict:
    return {
        "uri": row["uri"],
        "cid": row["cid"],
        "source": row["source"],
        "sourceQuery": row["source_query"],
        "author": {
            "handle": row["author_handle"],
            "did": row["author_did"],
            "displayName": row["author_display_name"],
        },
        "createdAt": row["created_at"],
        "indexedAt": row["indexed_at"],
        "ingestedAt": row["ingested_at"],
        "updatedAt": row["updated_at"],
        "text": row["text"],
        "probability": row["probability"],
        "action": row["action"],
        "thresholds": json.loads(row["thresholds_json"]),
        "policyEvidence": json.loads(row["policy_evidence_json"]),
        "publicLabelEvidence": json.loads(row["public_label_evidence_json"]),
        "contextualSafetyEvidence": json.loads(row["contextual_safety_evidence_json"]),
        "status": row["status"],
        "reviewerDecision": row["reviewer_decision"],
        "reviewerNotes": row["reviewer_notes"],
        "reviewerId": row["reviewer_id"],
        "reviewedAt": row["reviewed_at"],
        "duplicateCount": row["duplicate_count"],
        "entities": [],
    }


def attach_item_entities(connection: sqlite3.Connection, items: list[dict]) -> list[dict]:
    if not items:
        return items
    uris = [item["uri"] for item in items]
    placeholders = ",".join("?" for _ in uris)
    rows = connection.execute(
        f"""
        SELECT
            rie.uri,
            re.entity_id,
            re.entity_type,
            re.value,
            rie.raw_value,
            rie.source,
            rie.risk_weight,
            re.observation_count,
            re.max_risk_weight
        FROM review_item_entities AS rie
        JOIN review_entities AS re ON re.entity_id = rie.entity_id
        WHERE rie.uri IN ({placeholders})
        ORDER BY rie.risk_weight DESC, re.entity_type, re.value
        """,
        uris,
    ).fetchall()
    by_uri: dict[str, list[dict]] = {uri: [] for uri in uris}
    for row in rows:
        by_uri[row["uri"]].append(
            {
                "id": row["entity_id"],
                "type": row["entity_type"],
                "value": row["value"],
                "raw": row["raw_value"],
                "source": row["source"],
                "riskWeight": row["risk_weight"],
                "observationCount": row["observation_count"],
                "maxRiskWeight": row["max_risk_weight"],
            }
        )
    for item in items:
        item["entities"] = by_uri.get(item["uri"], [])
    return items


def list_items(
    db_path: str | Path,
    *,
    statuses: Iterable[str] | None = None,
    limit: int = 50,
) -> list[dict]:
    init_db(db_path)
    status_list = [status for status in (statuses or []) if status]
    with connect(db_path) as connection:
        if status_list:
            placeholders = ",".join("?" for _ in status_list)
            rows = connection.execute(
                f"""
                SELECT * FROM review_items
                WHERE status IN ({placeholders})
                ORDER BY probability DESC, ingested_at DESC
                LIMIT ?
                """,
                (*status_list, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT * FROM review_items
                ORDER BY probability DESC, ingested_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        items = [parse_row(row) for row in rows]
        attach_item_entities(connection, items)
    return items


def status_counts(db_path: str | Path) -> dict[str, int]:
    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT status, COUNT(*) AS count FROM review_items GROUP BY status ORDER BY status"
        ).fetchall()
    return {row["status"]: int(row["count"]) for row in rows}


def export_lab_queue(
    db_path: str | Path,
    out_path: str | Path,
    *,
    limit: int = 80,
    statuses: Iterable[str] | None = None,
) -> dict:
    items = list_items(db_path, statuses=statuses, limit=limit)
    summary = {
        "generatedAt": utc_now(),
        "dbPath": str(db_path),
        "count": len(items),
        "statusCounts": status_counts(db_path),
        "items": items,
    }
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    out.write_text(f"export const liveReviewQueue = {rendered};\n", encoding="utf-8")
    return summary
