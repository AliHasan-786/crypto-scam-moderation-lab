import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from model_comparison.shared_action_v2 import ROOT
from model_comparison.v2_transport import (
    TransportResponse,
    V2AccessDenied,
    V2AttemptStore,
    canonical_json,
    execute_prepared,
    load_spec,
    replay_attempt_inventory,
    sha256,
    shared_action_prompt,
    validate_spec_identities,
)


class FakeTransport:
    def __init__(self, *, fail: bool = False):
        self.calls = 0
        self.fail = fail

    def estimate_cost_usd(self, *, text: str, model_id: str) -> float:
        return 0.01

    def invoke(self, *, text: str, model_id: str, prompt: str) -> TransportResponse:
        self.calls += 1
        if self.fail:
            raise RuntimeError("fixture transport failure")
        return TransportResponse(
            raw_output={
                "action": "human_review",
                "speaker_originated_evidence": [],
                "risk_indicators": ["crypto_transfer_request"],
                "protected_context": [],
                "rationale": "fixture-only response",
            },
            resolved_model_id=model_id,
            usage={"input_tokens": 5, "output_tokens": 5, "total_tokens": 10},
            latency_ms=1.25,
            cost_usd=0.01,
        )


def write_context(path: Path, spec: dict, *, budget: float = 1.0) -> None:
    path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "benchmarkNamespace": spec["benchmarkNamespace"],
                "providerCallsAuthorized": True,
                "credentialsAuthorized": True,
                "issuedOn": date.today().isoformat(),
                "expiresOn": (date.today() + timedelta(days=1)).isoformat(),
                "budgetCapUsd": budget,
                "testSha256": spec["testSha256"],
                "promptSha256": spec["promptSha256"],
                "policySha256": spec["policySha256"],
                "allowedModelIds": list(spec["systems"].values()),
            }
        ),
        encoding="utf-8",
    )


class V2TransportTests(unittest.TestCase):
    def test_missing_context_blocks_before_transport_access(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(V2AccessDenied):
                execute_prepared(
                    access_context_path=Path(directory) / "missing.json",
                    store=V2AttemptStore(Path(directory) / "cache", spec_hash),
                    transports={next(iter(spec["systems"].values())): transport},
                    model_ids=[next(iter(spec["systems"].values()))],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 0)

    def test_fake_transport_writes_atomic_v2_attempt_with_provenance(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            store = V2AttemptStore(directory_path / "cache", spec_hash)
            paths = execute_prepared(
                access_context_path=context_path,
                store=store,
                transports={model_id: transport},
                model_ids=[model_id],
                max_cases_per_model=1,
            )
            record = json.loads(paths[0].read_text(encoding="utf-8"))
            inventory = replay_attempt_inventory(store, spec)
        self.assertEqual(transport.calls, 1)
        self.assertEqual(record["benchmarkNamespace"], "crypto-scam-v2-shared-actions")
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["promptSha256"], sha256(shared_action_prompt().encode("utf-8")))
        self.assertEqual(record["policySha256"], spec["policySha256"])
        self.assertEqual(record["usage"]["total_tokens"], 10)
        self.assertIsNone(record["error"])
        self.assertEqual(inventory["completedAttempts"], 1)
        self.assertEqual(inventory["transportErrors"], 0)
        self.assertEqual(inventory["mode"], "v2_cache_inventory_not_measured")

    def test_tampered_prompt_identity_is_rejected_before_transport_setup(self):
        spec = load_spec()
        spec["promptSha256"] = "0" * 64
        with self.assertRaisesRegex(Exception, "prompt hash"):
            validate_spec_identities(spec, ROOT / "test.csv")

    def test_expired_context_blocks_before_transport_access(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            context = json.loads(context_path.read_text(encoding="utf-8"))
            context["issuedOn"] = "2020-01-01"
            context["expiresOn"] = "2020-01-02"
            context_path.write_text(json.dumps(context), encoding="utf-8")
            with self.assertRaises(V2AccessDenied):
                execute_prepared(
                    access_context_path=context_path,
                    store=V2AttemptStore(directory_path / "cache", spec_hash),
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 0)

    def test_transport_error_is_atomically_recorded_for_resume(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            paths = execute_prepared(
                access_context_path=context_path,
                store=V2AttemptStore(directory_path / "cache", spec_hash),
                transports={model_id: FakeTransport(fail=True)},
                model_ids=[model_id],
                max_cases_per_model=1,
            )
            record = json.loads(paths[0].read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "transport_error")
        self.assertEqual(record["error"]["type"], "RuntimeError")
        self.assertIsNone(record["rawOutput"])


if __name__ == "__main__":
    unittest.main()
