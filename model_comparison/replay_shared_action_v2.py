"""Replay fixture-only V2 shared-action records; this command never calls a provider."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from shared_action_v2 import ROOT, baseline_preflight, load_fixture_replay, load_pinned_test_rows, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="model_comparison/fixtures/v2_shared_action_replay.json")
    parser.add_argument("--test", default="test.csv")
    parser.add_argument("--model-path", default="audit_outputs/fraud_labeler_v2.joblib")
    parser.add_argument("--out", default="audit_outputs/shared_action_v2_offline_replay.json")
    args = parser.parse_args()
    test_path = ROOT / args.test
    rows = load_pinned_test_rows(test_path)
    records = load_fixture_replay(ROOT / args.fixture, rows)
    report = {
        "schemaVersion": 1,
        "mode": "offline_fixture_replay_not_measured",
        "externalCallsMade": False,
        "interpretation": "Fixture adapter validation only. This is not a V2 hosted run and contains no provider measurement.",
        "inputs": {"testRows": len(rows), "testSha256": sha256(test_path.read_bytes())},
        "preregistration": "model_comparison/PREREGISTRATION_V2_SHARED_ACTIONS.md",
        "baselinePreflight": baseline_preflight(rows, ROOT / args.model_path),
        "fixtureRecords": [
            {**{key: value for key, value in record.items() if key != "result"}, "result": record["result"].to_dict()}
            for record in records
        ],
        "fixtureSummary": {
            "records": len(records),
            "compatible": sum(record["result"].compatible for record in records),
            "incompatible": sum(not record["result"].compatible for record in records),
        },
    }
    output = ROOT / args.out
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "mode": report["mode"], "externalCallsMade": False}, sort_keys=True))


if __name__ == "__main__":
    main()
