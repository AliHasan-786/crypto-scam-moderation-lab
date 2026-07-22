"""Build a randomized 30-case, sanitized reviewer-study packet locally."""
from __future__ import annotations
import argparse, csv, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("cases", [])

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="quality/study_kit/reviewer_packet.csv")
    parser.add_argument("--seed", type=int, default=20260721)
    args = parser.parse_args()
    cases = load(ROOT / "evals/scenario_eval_cases.json") + load(ROOT / "evals/hardening_eval_cases.json") + load(ROOT / "quality/calibration_cases.json")
    random.Random(args.seed).shuffle(cases)
    selected = cases[:30]
    with (ROOT / args.out).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_id", "post_text", "participant_action", "seconds", "evidence_usefulness", "disagreement_category"])
        writer.writeheader()
        for item in selected:
            writer.writerow({"case_id": item["id"], "post_text": item["text"], "participant_action": "", "seconds": "", "evidence_usefulness": "", "disagreement_category": ""})
    print(json.dumps({"packet": args.out, "caseCount": len(selected), "seed": args.seed}))

if __name__ == "__main__": main()
