"""Cache-only guard-model comparison scaffold; never makes provider calls."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_local_env(path: Path) -> None:
    """Load only local key/value pairs; this cache-only harness never sends them."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="model_comparison/config.json")
    parser.add_argument("--test", default="test.csv")
    parser.add_argument("--model-path", default="audit_outputs/fraud_labeler_v2.joblib")
    parser.add_argument("--out", default="audit_outputs/guard_model_benchmark.json")
    parser.add_argument("--markdown-out", default="audit_outputs/guard_model_benchmark.md")
    args = parser.parse_args()
    config_path, test_path, model_path = ROOT / args.config, ROOT / args.test, ROOT / args.model_path
    load_local_env(ROOT / "model_comparison/.env")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(test_path.open(encoding="utf-8-sig")))
    artifact = joblib.load(model_path)
    labels = [int(row["Ground Truth Label"]) for row in rows]
    scores = artifact["model"].predict_proba([row["Post Content"] for row in rows])[:, 1]
    threshold = float(artifact["thresholds"]["review"])
    predictions = [int(score >= threshold) for score in scores]
    tp = sum(p == 1 and y == 1 for p, y in zip(predictions, labels))
    fp = sum(p == 1 and y == 0 for p, y in zip(predictions, labels))
    fn = sum(p == 0 and y == 1 for p, y in zip(predictions, labels))
    report = {
        "mode": "cache_only",
        "claim": "Only the local baseline was executed. External systems are explicitly unavailable pending approved, version-resolved access.",
        "inputs": {"testSha256": sha256(test_path), "rows": len(rows), "preprocessing": "original post text only"},
        "preregistration": {"path": "model_comparison/PREREGISTRATION.md", "sha256": sha256(ROOT / "model_comparison/PREREGISTRATION.md")},
        "credentialReadiness": {system["id"]: bool(os.environ.get(system["requiredEnv"])) for system in config["systems"] if system.get("requiredEnv")},
        "systems": [{"id": "lab-baseline", "status": "executed", "threshold": threshold, "tp": tp, "fp": fp, "fn": fn}] + [system for system in config["systems"] if system["id"] != "lab-baseline"],
        "notComparableYet": [system["id"] for system in config["systems"] if system["id"] != "lab-baseline"],
    }
    (ROOT / args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Guard-Model Benchmark (Cache-Only)", "", report["claim"], "", "| System | Status |", "| --- | --- |"]
    lines += [f"| {system['id']} | {system['status']} |" for system in report["systems"]]
    (ROOT / args.markdown_out).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
