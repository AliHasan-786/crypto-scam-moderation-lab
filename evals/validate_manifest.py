"""Validate versioned evaluation inputs and detect unversioned suite changes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case_count(path: Path) -> int:
    if path.suffix == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return sum(1 for _ in csv.DictReader(handle))
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return len(data)
    for key in ("cases", "scenarios", "items"):
        if isinstance(data.get(key), list):
            return len(data[key])
    raise ValueError(f"Cannot determine case count for {path}")


def git_show(ref: str, path: str) -> dict[str, Any] | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return json.loads(result.stdout) if result.returncode == 0 else None


def changed_since(ref: str, path: str) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", ref, "HEAD", "--", path],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 1


def validate_version_bumps(manifest: dict[str, Any], compare_ref: str | None) -> list[str]:
    if not compare_ref:
        return []
    previous = git_show(compare_ref, "evals/MANIFEST.json")
    if previous is None:
        return []
    old_by_id = {suite["id"]: suite for suite in previous.get("suites", [])}
    failures = []
    for suite in manifest.get("suites", []):
        old = old_by_id.get(suite["id"])
        if old and changed_since(compare_ref, suite["path"]):
            if suite["semanticVersion"] == old.get("semanticVersion"):
                failures.append(
                    f"{suite['id']}: source changed since {compare_ref} without a semanticVersion bump"
                )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="evals/MANIFEST.json")
    parser.add_argument(
        "--compare-ref",
        default=os.environ.get("EVAL_MANIFEST_BASE_REF", ""),
        help="Optional git base ref used to require a version bump for changed suites.",
    )
    args = parser.parse_args()

    manifest_path = ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for group in ("suites", "datasets"):
        for item in manifest.get(group, []):
            path = ROOT / item["path"]
            if not path.exists():
                failures.append(f"{item['id']}: missing {item['path']}")
                continue
            if sha256(path) != item["sha256"]:
                failures.append(f"{item['id']}: SHA-256 mismatch for {item['path']}")
            expected_count = item.get("caseCount", item.get("rows"))
            if expected_count is not None and case_count(path) != expected_count:
                failures.append(f"{item['id']}: count mismatch for {item['path']}")

    failures.extend(validate_version_bumps(manifest, args.compare_ref or None))
    summary = {
        "passed": not failures,
        "manifestVersion": manifest.get("manifestVersion"),
        "suiteCount": len(manifest.get("suites", [])),
        "datasetCount": len(manifest.get("datasets", [])),
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
