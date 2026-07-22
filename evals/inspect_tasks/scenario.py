"""Optional UK AISI Inspect task wrapper for the frozen scenario suite."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
try:
    from inspect_ai import Task, task
    from inspect_ai.dataset import Sample
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install optional dependency: pip install inspect-ai") from exc

@task
def crypto_scam_scenarios() -> Task:
    cases = json.loads((ROOT / "scenario_eval_cases.json").read_text(encoding="utf-8"))
    return Task(dataset=[Sample(input=item["text"], target=item["expected_min_action"], id=item["id"]) for item in cases])
