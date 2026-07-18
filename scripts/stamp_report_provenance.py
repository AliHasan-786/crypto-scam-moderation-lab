"""Attach immutable input provenance to every generated JSON audit report."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="evals/MANIFEST.json")
    parser.add_argument("--reports-dir", default="audit_outputs")
    args = parser.parse_args()

    manifest_path = ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance: dict[str, Any] = {
        "stampedAt": datetime.now(timezone.utc).isoformat(),
        "manifest": {
            "path": args.manifest,
            "manifestVersion": manifest["manifestVersion"],
            "sha256": sha256(manifest_path),
        },
        "dataset_hashes": {
            item["id"]: item["sha256"] for item in manifest.get("datasets", [])
        },
        "suite_versions": {
            item["id"]: {
                "semanticVersion": item["semanticVersion"],
                "sha256": item["sha256"],
                "caseCount": item["caseCount"],
            }
            for item in manifest.get("suites", [])
        },
    }

    stamped = 0
    for report_path in sorted((ROOT / args.reports_dir).glob("*.json")):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(report, dict):
            continue
        report["provenance"] = provenance
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        stamped += 1

    print(json.dumps({"stampedReports": stamped, "manifestVersion": manifest["manifestVersion"]}, indent=2))


if __name__ == "__main__":
    main()
