"""Executable build-only controls for the shadow-service gate."""
from __future__ import annotations

import ast
import os
import tempfile
import unittest
from pathlib import Path

from labeler_service.shadow_daemon import process_fixture_events


def scorer(text: str) -> dict:
    if "warning" in text.lower():
        return {"score": 0.1, "action": "no_label", "matched_rules": []}
    return {"score": 0.9, "action": "send_to_human_review", "matched_rules": ["transfer_ask"]}


class ShadowControlsTest(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["SHADOW_ENABLED"] = "true"
        os.environ.pop("SHADOW_KILL_SWITCH", None)
        self.events = [{"event_id": "fixture-1", "text": "Send a fee now"}, {"event_id": "fixture-2", "text": "Send another fee now"}]

    def tearDown(self) -> None:
        os.environ.pop("SHADOW_ENABLED", None)
        os.environ.pop("SHADOW_KILL_SWITCH", None)

    def test_rate_cap_and_no_text_retention(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = process_fixture_events(self.events, state_path=Path(directory) / "state.sqlite", max_decisions_per_hour=1, score=scorer, protected_context_guard=lambda: True)
            self.assertTrue(result["capped"])
            self.assertEqual(result["processed"], 1)
            self.assertNotIn("Send a fee now", (Path(directory) / "state.sqlite").read_bytes().decode("latin1"))

    def test_kill_switch_stops_before_processing(self) -> None:
        os.environ["SHADOW_KILL_SWITCH"] = "true"
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                process_fixture_events(self.events, state_path=Path(directory) / "state.sqlite", max_decisions_per_hour=1, score=scorer, protected_context_guard=lambda: True)

    def test_failed_protected_context_guard_aborts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "Protected-context guard failed"):
                process_fixture_events(self.events, state_path=Path(directory) / "state.sqlite", max_decisions_per_hour=1, score=scorer, protected_context_guard=lambda: False)

    def test_no_outbound_write_clients_imported(self) -> None:
        tree = ast.parse((Path(__file__).parent / "shadow_daemon.py").read_text(encoding="utf-8"))
        imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
        self.assertFalse(imports & {"requests", "httpx", "urllib", "atproto", "websockets"})


if __name__ == "__main__":
    unittest.main()
