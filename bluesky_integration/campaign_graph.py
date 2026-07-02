from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from bluesky_integration.review_store import list_items, refresh_item_entities


CLUSTER_ENTITY_TYPES = {"domain", "wallet", "url_shortener", "handle"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def entity_label(entity_type: str, value: str) -> str:
    if entity_type == "risk_phrase":
        return value.replace("_", " ")
    return value


def build_entity_index(items: list[dict]) -> tuple[dict[str, dict], dict[str, set[str]]]:
    records: dict[str, dict] = {}
    item_sets: dict[str, set[str]] = defaultdict(set)
    for item in items:
        for entity in item.get("entities", []):
            entity_id = entity["id"]
            item_sets[entity_id].add(item["uri"])
            current = records.get(entity_id)
            risk_weight = float(entity.get("riskWeight") or 0)
            if current is None:
                records[entity_id] = {
                    "id": entity_id,
                    "type": entity["type"],
                    "value": entity["value"],
                    "label": entity_label(entity["type"], entity["value"]),
                    "riskWeight": risk_weight,
                    "rawExamples": [entity.get("raw") or entity["value"]],
                    "sources": sorted({entity.get("source") or "unknown"}),
                }
            else:
                current["riskWeight"] = max(float(current["riskWeight"]), risk_weight)
                raw = entity.get("raw") or entity["value"]
                if raw not in current["rawExamples"] and len(current["rawExamples"]) < 4:
                    current["rawExamples"].append(raw)
                current["sources"] = sorted(set(current["sources"]) | {entity.get("source") or "unknown"})
    return records, item_sets


def summarize_entities(records: dict[str, dict], item_sets: dict[str, set[str]]) -> list[dict]:
    summaries = []
    for entity_id, record in records.items():
        item_count = len(item_sets[entity_id])
        summaries.append(
            {
                **record,
                "itemCount": item_count,
                "shared": item_count > 1,
            }
        )
    return sorted(
        summaries,
        key=lambda item: (item["itemCount"], item["riskWeight"], item["type"], item["value"]),
        reverse=True,
    )


class UnionFind:
    def __init__(self, values: list[str]) -> None:
        self.parents = {value: value for value in values}

    def find(self, value: str) -> str:
        parent = self.parents[value]
        if parent != value:
            self.parents[value] = self.find(parent)
        return self.parents[value]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parents[right_root] = left_root


def build_campaigns(items: list[dict], entity_summaries: list[dict], item_sets: dict[str, set[str]]) -> list[dict]:
    items_by_uri = {item["uri"]: item for item in items}
    union_find = UnionFind(list(items_by_uri))
    shared_cluster_entities = [
        entity
        for entity in entity_summaries
        if entity["shared"] and entity["type"] in CLUSTER_ENTITY_TYPES
    ]
    for entity in shared_cluster_entities:
        uris = list(item_sets[entity["id"]])
        for uri in uris[1:]:
            union_find.union(uris[0], uri)

    components: dict[str, list[str]] = defaultdict(list)
    for uri in items_by_uri:
        components[union_find.find(uri)].append(uri)

    campaigns = []
    for index, uris in enumerate((values for values in components.values() if len(values) > 1), start=1):
        uri_set = set(uris)
        cluster_entities = [
            entity
            for entity in entity_summaries
            if len(item_sets[entity["id"]] & uri_set) > 1
        ]
        cluster_entities = sorted(
            cluster_entities,
            key=lambda item: (item["type"] in CLUSTER_ENTITY_TYPES, item["itemCount"], item["riskWeight"]),
            reverse=True,
        )
        cluster_items = [items_by_uri[uri] for uri in uris]
        avg_probability = sum(float(item.get("probability") or 0) for item in cluster_items) / len(cluster_items)
        statuses = Counter(item.get("status") or "unknown" for item in cluster_items)
        strong_shared_entities = sum(
            1
            for entity in cluster_entities
            if entity["type"] in CLUSTER_ENTITY_TYPES and float(entity["riskWeight"]) >= 0.55
        )
        risk_score = min(
            1.0,
            (avg_probability * 0.5)
            + min(0.3, strong_shared_entities * 0.12)
            + min(0.2, max(0, len(cluster_items) - 1) * 0.08),
        )
        campaigns.append(
            {
                "id": f"campaign-{index}",
                "itemCount": len(cluster_items),
                "avgProbability": round(avg_probability, 3),
                "riskScore": round(risk_score, 3),
                "statusCounts": dict(sorted(statuses.items())),
                "topEntities": cluster_entities[:8],
                "sampleItems": [
                    {
                        "uri": item["uri"],
                        "author": item.get("author") or {},
                        "status": item.get("status"),
                        "probability": item.get("probability"),
                        "action": item.get("action"),
                        "text": item.get("text", "")[:220],
                    }
                    for item in sorted(cluster_items, key=lambda row: float(row.get("probability") or 0), reverse=True)[:5]
                ],
            }
        )
    return sorted(campaigns, key=lambda item: (item["riskScore"], item["itemCount"]), reverse=True)


def build_campaign_graph(db_path: str | Path, *, limit: int = 250, refresh_entities: bool = True) -> dict:
    if refresh_entities:
        refresh_item_entities(db_path, limit=limit)
    items = list_items(db_path, limit=limit)
    records, item_sets = build_entity_index(items)
    entity_summaries = summarize_entities(records, item_sets)
    campaigns = build_campaigns(items, entity_summaries, item_sets)
    type_counts = Counter(entity["type"] for entity in entity_summaries)
    shared_type_counts = Counter(entity["type"] for entity in entity_summaries if entity["shared"])
    linked_items = sum(1 for item in items if item.get("entities"))

    shared_entities = [entity for entity in entity_summaries if entity["shared"]]
    edges = []
    for entity in shared_entities[:40]:
        for uri in sorted(item_sets[entity["id"]])[:12]:
            edges.append({"source": entity["id"], "target": uri, "type": "entity_observed_in_item"})

    return {
        "generatedAt": utc_now(),
        "dbPath": str(db_path),
        "itemCount": len(items),
        "linkedItemCount": linked_items,
        "entityCount": len(entity_summaries),
        "sharedEntityCount": len(shared_entities),
        "campaignCount": len(campaigns),
        "entityTypeCounts": dict(sorted(type_counts.items())),
        "sharedEntityTypeCounts": dict(sorted(shared_type_counts.items())),
        "topEntities": entity_summaries[:14],
        "sharedEntities": shared_entities[:20],
        "campaigns": campaigns[:8],
        "edges": edges,
    }


def export_campaign_graph(
    db_path: str | Path,
    out_path: str | Path,
    *,
    lab_summary_path: str | Path | None = None,
    limit: int = 250,
) -> dict:
    graph = build_campaign_graph(db_path, limit=limit)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(graph, ensure_ascii=False, indent=2)
    out.write_text(rendered + "\n", encoding="utf-8")
    if lab_summary_path:
        lab_out = Path(lab_summary_path)
        lab_out.parent.mkdir(parents=True, exist_ok=True)
        lab_out.write_text(f"export const campaignGraph = {rendered};\n", encoding="utf-8")
    return graph
