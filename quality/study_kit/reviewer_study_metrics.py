"""Summarize de-identified reviewer-study responses from a local CSV."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter, defaultdict
from statistics import mean
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, help="CSV: participant_id,case_id,action,seconds,evidence_usefulness,disagreement_category")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    rows = list(csv.DictReader(Path(args.responses).open(encoding="utf-8-sig")))
    by_case, categories = defaultdict(list), Counter()
    for row in rows:
        by_case[row["case_id"]].append(row["action"])
        if row.get("disagreement_category"): categories[row["disagreement_category"]] += 1
    consensus = [len(set(actions)) == 1 for actions in by_case.values()]
    report = {"responseCount": len(rows), "caseCount": len(by_case), "unanimousCaseRate": round(mean(consensus), 4) if consensus else None, "meanSeconds": round(mean(float(row["seconds"]) for row in rows), 2) if rows else None, "meanEvidenceUsefulness": round(mean(float(row["evidence_usefulness"]) for row in rows), 2) if rows else None, "disagreementCategories": dict(categories), "caveat": "Informal, de-identified usability/quality feedback; not a prevalence or model-performance study."}
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__": main()
