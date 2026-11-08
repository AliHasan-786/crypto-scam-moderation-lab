import csv
import json
import multiprocessing
import os
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path

from model_comparison.shared_action_v2 import ROOT
from model_comparison.v2_transport import (
    TransportResponse,
    V2AccessDenied,
    V2AttemptStore,
    V2ProcessLock,
    V2ReservationJournal,
    V2TransportError,
    canonical_json,
    execute_prepared,
    load_spec,
    replay_attempt_inventory,
    sha256,
    shared_action_prompt,
    validate_spec_identities,
)


class FakeTransport:
    def __init__(
        self,
        *,
        fail: bool = False,
        estimate: object = 0.01,
        cost: object = 0.01,
        resolved_model_id: str | None = None,
    ):
        self.calls = 0
        self.fail = fail
        self.estimate = estimate
        self.cost = cost
        self.resolved_model_id = resolved_model_id

    def estimate_cost_usd(self, *, text: str, model_id: str):
        return self.estimate

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
            resolved_model_id=self.resolved_model_id or model_id,
            usage={"input_tokens": 5, "output_tokens": 5, "total_tokens": 10},
            latency_ms=1.25,
            cost_usd=self.cost,
        )


class FileCountingTransport(FakeTransport):
    def __init__(self, counter_path: str, *, delay_seconds: float = 0.0):
        super().__init__()
        self.counter_path = Path(counter_path)
        self.delay_seconds = delay_seconds

    def invoke(self, *, text: str, model_id: str, prompt: str) -> TransportResponse:
        with self.counter_path.open("a", encoding="utf-8") as handle:
            handle.write("invoke\n")
            handle.flush()
            os.fsync(handle.fileno())
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        return super().invoke(text=text, model_id=model_id, prompt=prompt)


class FailingWriteStore(V2AttemptStore):
    def write(self, record: dict) -> Path:
        raise OSError("fixture disk interruption after invocation")


def concurrent_execute_worker(
    context_path: str,
    cache_path: str,
    control_root: str,
    counter_path: str,
    model_id: str,
    result_queue: object,
) -> None:
    spec = load_spec()
    spec_hash = sha256(canonical_json(spec).encode("utf-8"))
    transport = FileCountingTransport(counter_path, delay_seconds=0.2)
    try:
        execute_prepared(
            access_context_path=Path(context_path),
            store=V2AttemptStore(Path(cache_path), spec_hash, control_root=Path(control_root)),
            transports={model_id: transport},
            model_ids=[model_id],
            max_cases_per_model=1,
        )
        result_queue.put("completed")
    except Exception as exc:  # pragma: no cover - assertion receives process result.
        result_queue.put(f"{type(exc).__name__}:{exc}")


def write_context(
    path: Path,
    spec: dict,
    *,
    budget: float = 1.0,
    maximum_liability: float = 0.01,
    authorization_id: str = "fixture-authorization-v2",
) -> None:
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
                "maxInvocationLiabilityUsd": maximum_liability,
                "authorizationId": authorization_id,
                "testSha256": spec["testSha256"],
                "promptSha256": spec["promptSha256"],
                "policySha256": spec["policySha256"],
                "allowedModelIds": list(spec["systems"].values()),
            }
        ),
        encoding="utf-8",
    )


def make_store(directory: Path, spec_hash: str, name: str = "cache") -> V2AttemptStore:
    return V2AttemptStore(directory / name, spec_hash, control_root=directory / "control")


def make_journal(context_path: Path, context: dict, spec_hash: str, store: V2AttemptStore) -> V2ReservationJournal:
    return V2ReservationJournal.for_context(context, spec_hash, store.control_root)


def first_test_text() -> str:
    with (ROOT / "test.csv").open(encoding="utf-8-sig", newline="") as handle:
        return next(csv.DictReader(handle))["Post Content"]


class V2TransportTests(unittest.TestCase):
    def test_missing_context_blocks_before_transport_access(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(V2AccessDenied):
                execute_prepared(
                    access_context_path=Path(directory) / "missing.json",
                    store=make_store(Path(directory), spec_hash),
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
            store = make_store(directory_path, spec_hash)
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
                    store=make_store(directory_path, spec_hash),
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 0)

    def test_unknown_cost_transport_error_is_recorded_and_blocks_resume(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            store = make_store(directory_path, spec_hash)
            failing = FakeTransport(fail=True)
            with self.assertRaisesRegex(V2TransportError, "manual reconciliation"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: failing},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            record = store.all_records()[0]
            resumed = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "manual reconciliation"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: resumed},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(record["status"], "transport_error")
        self.assertEqual(record["error"]["type"], "RuntimeError")
        self.assertIsNone(record["rawOutput"])
        self.assertFalse(record["costKnown"])
        self.assertEqual(failing.calls, 1)
        self.assertEqual(resumed.calls, 0)

    def test_resume_counts_prior_spend_against_the_same_cap(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01)
            store = make_store(directory_path, spec_hash)
            execute_prepared(
                access_context_path=context_path,
                store=store,
                transports={model_id: transport},
                model_ids=[model_id],
                max_cases_per_model=1,
            )
            with self.assertRaisesRegex(V2TransportError, "configured current budget"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 1)

    def test_validation_failure_preserves_received_response_and_billed_cost(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport(cost=0.01, resolved_model_id="wrong-model")
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01)
            store = make_store(directory_path, spec_hash)
            with self.assertRaisesRegex(V2TransportError, "recorded billed cost"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            record = store.all_records()[0]
            resumed = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "manual reconciliation"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: resumed},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertTrue(record["responseReceived"])
        self.assertEqual(record["resolvedModelId"], "wrong-model")
        self.assertEqual(record["usage"]["total_tokens"], 10)
        self.assertEqual(record["costUsd"], 0.01)
        self.assertTrue(record["costKnown"])
        self.assertEqual(resumed.calls, 0)

    def test_invalid_budget_and_estimated_cost_are_rejected_before_invoke(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=True)
            invalid_budget_transport = FakeTransport()
            with self.assertRaises(V2AccessDenied):
                execute_prepared(
                    access_context_path=context_path,
                    store=make_store(directory_path, spec_hash, "cache-a"),
                    transports={model_id: invalid_budget_transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            write_context(context_path, spec)
            invalid_estimate_transport = FakeTransport(estimate=True)
            with self.assertRaisesRegex(V2TransportError, "maximum invocation liability"):
                execute_prepared(
                    access_context_path=context_path,
                    store=make_store(directory_path, spec_hash, "cache-b"),
                    transports={model_id: invalid_estimate_transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(invalid_budget_transport.calls, 0)
        self.assertEqual(invalid_estimate_transport.calls, 0)

    def test_invalid_returned_cost_is_preserved_as_unknown_and_blocks_resume(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            store = make_store(directory_path, spec_hash)
            invalid_cost_transport = FakeTransport(cost=True)
            with self.assertRaisesRegex(V2TransportError, "manual reconciliation"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: invalid_cost_transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            record = store.all_records()[0]
            resumed = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "manual reconciliation"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: resumed},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertTrue(record["responseReceived"])
        self.assertFalse(record["costKnown"])
        self.assertEqual(record["returnedCostUsdRepresentation"], "True")
        self.assertEqual(resumed.calls, 0)

    def test_attempt_store_refuses_overwrite(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            store = make_store(directory_path, spec_hash)
            paths = execute_prepared(
                access_context_path=context_path,
                store=store,
                transports={model_id: FakeTransport()},
                model_ids=[model_id],
                max_cases_per_model=1,
            )
            record = json.loads(paths[0].read_text(encoding="utf-8"))
            with self.assertRaisesRegex(V2TransportError, "overwrite"):
                store.write(record)

    def test_changing_cache_path_cannot_reset_authorized_cap(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            first_store = make_store(directory_path, spec_hash, "cache-a")
            execute_prepared(
                access_context_path=context_path,
                store=first_store,
                transports={model_id: transport},
                model_ids=[model_id],
                max_cases_per_model=1,
            )
            second_store = make_store(directory_path, spec_hash, "cache-b")
            with self.assertRaisesRegex(V2TransportError, "prior reserved or in-flight"):
                execute_prepared(
                    access_context_path=context_path,
                    store=second_store,
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 1)

    def test_changing_context_path_cannot_reset_authorized_cap(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            first_context = directory_path / "context-a.json"
            second_context = directory_path / "context-b.json"
            write_context(first_context, spec, budget=0.01, maximum_liability=0.01)
            write_context(second_context, spec, budget=0.01, maximum_liability=0.01)
            first_store = make_store(directory_path, spec_hash, "cache-a")
            execute_prepared(
                access_context_path=first_context,
                store=first_store,
                transports={model_id: transport},
                model_ids=[model_id],
                max_cases_per_model=1,
            )
            with self.assertRaisesRegex(V2TransportError, "prior reserved or in-flight"):
                execute_prepared(
                    access_context_path=second_context,
                    store=make_store(directory_path, spec_hash, "cache-b"),
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 1)

    def test_changed_context_cap_conflicts_with_authorization_journal(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            store = make_store(directory_path, spec_hash)
            execute_prepared(
                access_context_path=context_path,
                store=store,
                transports={model_id: transport},
                model_ids=[model_id],
                max_cases_per_model=1,
            )
            write_context(context_path, spec, budget=0.02, maximum_liability=0.01)
            with self.assertRaisesRegex(V2TransportError, "conflicts with its journal"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: FakeTransport()},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 1)

    def test_reserved_or_in_flight_crash_state_never_retries_automatically(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            context = json.loads(context_path.read_text(encoding="utf-8"))
            store = make_store(directory_path, spec_hash)
            journal = make_journal(context_path, context, spec_hash, store)
            text = first_test_text()
            input_hash = sha256(text.encode("utf-8"))
            invocation_key = sha256("\0".join((model_id, "0", input_hash, spec_hash)).encode("utf-8"))
            with V2ProcessLock(journal.lock_path):
                journal.initialize()
                reservation = journal.reserve(
                    invocation_key=invocation_key,
                    maximum_liability_usd=0.01,
                    metadata={"modelId": model_id, "caseIndex": 0, "inputSha256": input_hash},
                )
            before_invoke = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "prior reserved or in-flight"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: before_invoke},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            with V2ProcessLock(journal.lock_path):
                journal.mark_invocation_started(reservation["reservationId"])
            after_invoke = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "prior reserved or in-flight"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: after_invoke},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(before_invoke.calls, 0)
        self.assertEqual(after_invoke.calls, 0)

    def test_restart_recovers_only_already_persisted_result_without_reinvoke(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            context = json.loads(context_path.read_text(encoding="utf-8"))
            store = make_store(directory_path, spec_hash)
            journal = make_journal(context_path, context, spec_hash, store)
            first_text = first_test_text()
            input_hash = sha256(first_text.encode("utf-8"))
            invocation_key = sha256("\0".join((model_id, "0", input_hash, spec_hash)).encode("utf-8"))
            with V2ProcessLock(journal.lock_path):
                journal.initialize()
                reservation = journal.reserve(
                    invocation_key=invocation_key,
                    maximum_liability_usd=0.01,
                    metadata={"modelId": model_id, "caseIndex": 0, "inputSha256": input_hash},
                )
                journal.mark_invocation_started(reservation["reservationId"])
            store.write(
                {
                    "benchmarkNamespace": spec["benchmarkNamespace"],
                    "specSha256": spec_hash,
                    "requestedModelId": model_id,
                    "caseIndex": 0,
                    "inputSha256": input_hash,
                    "attempt": 1,
                    "reservationId": reservation["reservationId"],
                    "status": "completed",
                    "costKnown": True,
                    "costUsd": 0.01,
                }
            )
            resumed = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "configured current budget"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: resumed},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            self.assertEqual(journal.reservations()[reservation["reservationId"]]["state"], "settled")
        self.assertEqual(resumed.calls, 0)

    def test_result_persistence_interruption_preserves_reservation_and_blocks_retry(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            interrupted_store = FailingWriteStore(
                directory_path / "cache", spec_hash, control_root=directory_path / "control"
            )
            invoked = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "result could not be persisted"):
                execute_prepared(
                    access_context_path=context_path,
                    store=interrupted_store,
                    transports={model_id: invoked},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            resumed = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "prior reserved or in-flight"):
                execute_prepared(
                    access_context_path=context_path,
                    store=make_store(directory_path, spec_hash),
                    transports={model_id: resumed},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(invoked.calls, 1)
        self.assertEqual(resumed.calls, 0)

    def test_unknown_cost_requires_immutable_reconciliation_and_still_cannot_retry(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            context = json.loads(context_path.read_text(encoding="utf-8"))
            store = make_store(directory_path, spec_hash)
            with self.assertRaisesRegex(V2TransportError, "unknown billed cost"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: FakeTransport(fail=True)},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            journal = make_journal(context_path, context, spec_hash, store)
            reservation_id = next(iter(journal.reservations()))
            with V2ProcessLock(journal.lock_path):
                journal.reconcile(reservation_id, 0.0, operator_note="Provider ledger confirmed no charge.")
            self.assertEqual(journal.reservations()[reservation_id]["state"], "reconciled")
            retried = FakeTransport()
            with self.assertRaisesRegex(V2TransportError, "manual reconciliation"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: retried},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
            self.assertGreaterEqual(len(list(journal.events_root.glob("event-*.json"))), 4)
        self.assertEqual(retried.calls, 0)

    def test_partial_journal_event_fails_closed_before_fake_transport(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            store = make_store(directory_path, spec_hash)
            context = json.loads(context_path.read_text(encoding="utf-8"))
            journal = make_journal(context_path, context, spec_hash, store)
            with V2ProcessLock(journal.lock_path):
                journal.initialize()
                journal.events_root.mkdir(parents=True, exist_ok=True)
                (journal.events_root / "event-000001-interrupted.json").write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(V2TransportError, "event is unreadable"):
                execute_prepared(
                    access_context_path=context_path,
                    store=store,
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=1,
                )
        self.assertEqual(transport.calls, 0)

    def test_two_processes_cannot_consume_the_same_reserved_cap(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            counter_path = directory_path / "invocations.txt"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            queue = multiprocessing.get_context("fork").Queue()
            worker_args = (
                str(context_path),
                str(directory_path / "cache"),
                str(directory_path / "control"),
                str(counter_path),
                model_id,
                queue,
            )
            first = multiprocessing.get_context("fork").Process(target=concurrent_execute_worker, args=worker_args)
            second = multiprocessing.get_context("fork").Process(target=concurrent_execute_worker, args=worker_args)
            first.start()
            second.start()
            first.join(timeout=10)
            second.join(timeout=10)
            self.assertEqual(first.exitcode, 0)
            self.assertEqual(second.exitcode, 0)
            outcomes = [queue.get(timeout=2), queue.get(timeout=2)]
            invocations = counter_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(invocations), 1)
        self.assertIn("completed", outcomes)
        self.assertTrue(any("configured current budget" in outcome for outcome in outcomes))

    def test_configured_liability_not_adapter_estimate_controls_capacity(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        transport = FakeTransport(estimate=0.0001, cost=0.0001)
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec, budget=0.01, maximum_liability=0.01)
            with self.assertRaisesRegex(V2TransportError, "configured current budget"):
                execute_prepared(
                    access_context_path=context_path,
                    store=make_store(directory_path, spec_hash),
                    transports={model_id: transport},
                    model_ids=[model_id],
                    max_cases_per_model=2,
                )
        self.assertEqual(transport.calls, 1)

    def test_duplicate_reservation_key_is_rejected_immutably(self):
        spec = load_spec()
        spec_hash = sha256(canonical_json(spec).encode("utf-8"))
        model_id = next(iter(spec["systems"].values()))
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            context_path = directory_path / "context.json"
            write_context(context_path, spec)
            context = json.loads(context_path.read_text(encoding="utf-8"))
            store = make_store(directory_path, spec_hash)
            journal = make_journal(context_path, context, spec_hash, store)
            with V2ProcessLock(journal.lock_path):
                journal.initialize()
                journal.reserve(
                    invocation_key="fixture-key",
                    maximum_liability_usd=0.01,
                    metadata={"modelId": model_id, "caseIndex": 0, "inputSha256": "fixture"},
                )
                with self.assertRaisesRegex(V2TransportError, "duplicate invocation key"):
                    journal.reserve(
                        invocation_key="fixture-key",
                        maximum_liability_usd=0.01,
                        metadata={"modelId": model_id, "caseIndex": 0, "inputSha256": "fixture"},
                    )


if __name__ == "__main__":
    unittest.main()
