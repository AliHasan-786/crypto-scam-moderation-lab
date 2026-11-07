"""Inspect V2 attempt provenance from the V2-only cache; never calls a provider."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .v2_transport import V2AttemptStore, canonical_json, load_spec, replay_attempt_inventory, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("model_comparison/v2_cache"))
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    spec = load_spec()
    store = V2AttemptStore(args.cache, sha256(canonical_json(spec).encode("utf-8")))
    report = replay_attempt_inventory(store, spec)
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
