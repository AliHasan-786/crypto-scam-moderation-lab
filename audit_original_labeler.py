from __future__ import annotations

import csv
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / "policy_proposal_labeler.py"
TRAIN = ROOT / "data.csv"
TEST = ROOT / "test.csv"


def normalize_text(text: str) -> str:
    text = text.lower().strip().strip('"')
    return re.sub(r"\s+", " ", text)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_diagnostics(path: Path) -> dict[str, object]:
    rows = read_rows(path)
    labels = Counter(str(row.get("Ground Truth Label", "")).strip() for row in rows)
    normalized = [normalize_text(row.get("Post Content", "")) for row in rows]
    lengths = [len(text.split()) for text in normalized if text]
    return {
        "rows": len(rows),
        "label_counts": dict(labels),
        "empty_text_rows": sum(1 for text in normalized if not text),
        "duplicates_within_file": len(normalized) - len(set(normalized)),
        "word_count": {
            "min": min(lengths) if lengths else 0,
            "mean": round(sum(lengths) / len(lengths), 2) if lengths else 0,
            "max": max(lengths) if lengths else 0,
        },
    }


def dependency_diagnostics() -> dict[str, bool]:
    packages = [
        "pandas",
        "numpy",
        "sklearn",
        "sentence_transformers",
        "xgboost",
        "joblib",
        "matplotlib",
        "nltk",
    ]
    return {package: importlib.util.find_spec(package) is not None for package in packages}


def line_no(source: str, needle: str) -> int | None:
    for index, line in enumerate(source.splitlines(), start=1):
        if needle in line:
            return index
    return None


def static_findings(source: str) -> list[dict[str, object]]:
    findings = []

    def add(severity: str, title: str, evidence: str, implication: str) -> None:
        findings.append(
            {
                "severity": severity,
                "title": title,
                "line": line_no(source, evidence),
                "evidence": evidence,
                "implication": implication,
            }
        )

    add(
        "high",
        "Original script cannot run in a minimal environment without XGBoost",
        "import xgboost as xgb",
        "The dependency is imported unconditionally, so even lightweight feature or rule tests fail when xgboost is unavailable.",
    )
    add(
        "high",
        "Test set is used during model development and model selection",
        "df_test = pd.read_csv(test_csv_path)",
        "The training function repeatedly evaluates models on test.csv and then chooses the final model, making the final test metrics optimistic.",
    )
    add(
        "high",
        "Prediction API changes behavior when probabilities are requested",
        "if return_probability and _LOADED_NGRAM_MODEL is not None",
        "predict_post(text) uses the saved base classifier, while predict_post(text, return_probability=True) combines in the n-gram model and can return a different label.",
    )
    add(
        "medium",
        "Warnings are globally suppressed",
        "warnings.filterwarnings('ignore')",
        "Convergence warnings and data warnings are hidden, which matters because some models are configured with very low iteration limits.",
    )
    add(
        "medium",
        "Reported Logistic Regression baseline is artificially weak",
        "max_iter=10",
        "The baseline uses tiny max_iter, extreme regularization, and loose tolerance. This can make the ensemble comparison look stronger than it is.",
    )
    add(
        "medium",
        "Baseline Random Forest and ensemble Random Forest are not comparable",
        "n_estimators=10",
        "The standalone RF is shallow and unbalanced, while the ensemble RF later uses 200 trees, deeper depth, and balanced class weights.",
    )
    add(
        "medium",
        "N-gram ensemble is evaluated but not saved as final model",
        "clf = base_ensemble",
        "The report discusses a final/enhanced ensemble, but the saved classifier is the traditional ensemble; later probability calls silently mix n-grams back in.",
    )
    add(
        "medium",
        "Hard-coded test.csv path limits reproducibility",
        'test_csv_path = "test.csv"',
        "The function cannot cleanly evaluate alternate splits or cross-validation folds without editing code or overwriting files.",
    )
    add(
        "low",
        "Unused imports suggest iterative code drift",
        "train_test_split, cross_val_score, StratifiedKFold",
        "This is not harmful by itself, but it supports a cleanup pass before presenting the project publicly.",
    )
    return findings


def main() -> None:
    source = ORIGINAL.read_text(encoding="utf-8")
    train_norm = {normalize_text(row["Post Content"]) for row in read_rows(TRAIN)}
    test_norm = {normalize_text(row["Post Content"]) for row in read_rows(TEST)}

    result = {
        "original_file": ORIGINAL.relative_to(ROOT).as_posix(),
        "dependencies_available": dependency_diagnostics(),
        "data": {
            "train": csv_diagnostics(TRAIN),
            "test": csv_diagnostics(TEST),
            "exact_train_test_overlap": len(train_norm & test_norm),
        },
        "static_findings": static_findings(source),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
