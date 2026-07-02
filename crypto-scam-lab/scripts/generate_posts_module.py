from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "data" / "posts.js"


def read_rows(path: Path, split: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            text = (row.get("Post Content") or "").strip()
            raw_label = str(row.get("Ground Truth Label") or "").strip()
            if not text or raw_label not in {"0", "1"}:
                continue
            rows.append(
                {
                    "id": f"{split}-{index:03d}",
                    "split": split,
                    "text": text,
                    "groundTruth": int(raw_label),
                }
            )
    return rows


def main() -> None:
    posts = read_rows(ROOT / "data.csv", "train") + read_rows(ROOT / "test.csv", "test")
    OUT.write_text(
        "export const posts = "
        + json.dumps(posts, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(posts)} posts to {OUT}")


if __name__ == "__main__":
    main()
