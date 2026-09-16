from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.export_records import export_record  # noqa: E402


class ExportRecordTests(unittest.TestCase):
    def test_legal_input_preserves_raw_and_records_all_bindings(self) -> None:
        artifact = {"path": "result.png", "sha256": "a" * 64}
        record = {
            "record_id": "legal-1",
            "source_sha": "b" * 40,
            "request": {"prompt_id": "request-1", "seed": 7},
            "input_digest": "c" * 64,
            "backend_instance": {"backend": "comfyui", "instance": "cpu-fake-1"},
            "job_id": "job-1",
            "artifact": artifact,
            "validator_version": "validate_png-v1",
            "artifact_validation": {"status": "verified", "independent": True},
            "approval_state": "valid",
            "reported_state": {"state": "generated", "attempts": [{"status": "completed", "request_hash": "d" * 64}]},
            "oracle_state": {
                "execution_state": "succeeded",
                "execution_started": 1,
                "execution_finished": 1,
            },
        }
        original = copy.deepcopy(record)
        exported = export_record(record)
        self.assertEqual(record, original)
        self.assertEqual(exported["reported_state"], record["reported_state"])
        self.assertEqual(exported["interpreted_state"]["execution_state"], "succeeded")
        self.assertTrue(exported["interpreted_state"]["execution_verified"])
        self.assertEqual(exported["mapping_version"], "research-normalization-v1")
        self.assertEqual(exported["request_digest"], "d" * 64)
        self.assertEqual(exported["field_reasons"]["request_digest"], "provided_reported_attempts.request_hash")

    def test_missing_fields_are_explicit_unknown_or_null_with_reasons(self) -> None:
        exported = export_record({
            "record_id": "missing-1",
            "reported_state": {"state": "failed", "attempts": [{"status": "failed"}]},
        })
        self.assertIsNone(exported["source_sha"])
        self.assertIsNone(exported["request_digest"])
        self.assertIsNone(exported["input_digest"])
        self.assertIsNone(exported["backend_instance"])
        self.assertIsNone(exported["job_id"])
        self.assertEqual(exported["interpreted_state"]["execution_state"], "unknown")
        self.assertEqual(exported["field_reasons"]["source_sha"], "source_sha_missing")
        self.assertIn("reported_product_state_not_used_as_execution_truth", exported["mapping_reason"]["execution_state"])

    def test_mismatch_is_retained_and_not_reconciled(self) -> None:
        exported = export_record({
            "record_id": "mismatch-1",
            "job_id": "job-reported",
            "artifact_hash": "a" * 64,
            "reported_state": {"state": "generated"},
            "oracle_state": {
                "execution_state": "succeeded",
                "job_id": "job-oracle",
                "artifact_hash": "b" * 64,
                "execution_started": 1,
                "execution_finished": 1,
            },
            "artifact_validation": {"status": "verified", "independent": True},
        })
        self.assertEqual(exported["job_id"], "job-reported")
        self.assertEqual(exported["oracle_state"]["job_id"], "job-oracle")
        self.assertEqual(exported["interpreted_state"]["evidence_state"], "mismatch")
        self.assertIn("differs", exported["field_reasons"]["artifact_hash"])
        self.assertIn("differs", exported["mapping_reason"]["evidence_state"])

    def test_explicit_unknown_and_product_failure_do_not_become_execution_failure(self) -> None:
        exported = export_record({
            "record_id": "unknown-1",
            "source_sha": "unknown",
            "request_digest": "unknown",
            "input_digest": "unknown",
            "backend_instance": "unknown",
            "job_id": "unknown",
            "artifact_hash": "unknown",
            "validator_version": "unknown",
            "reported_state": {"state": "failed", "attempts": [{"status": "failed"}]},
            "oracle_state": {"state": "unknown", "execution_state": "unknown"},
        })
        self.assertEqual(exported["interpreted_state"]["execution_state"], "unknown")
        self.assertNotEqual(exported["interpreted_state"]["execution_state"], "failed")
        self.assertEqual(exported["interpreted_state"]["recovery_state"], "required")

    def test_cli_style_artifact_path_hash_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact = root / "input.bin"
            artifact.write_bytes(b"research-input")
            record = {
                "reported_state": {"state": "created"},
                "input": {"path": "input.bin"},
                "artifact": {"path": "input.bin"},
            }
            original = artifact.read_bytes()
            exported = export_record(record, source_path=root / "record.json")
            self.assertEqual(artifact.read_bytes(), original)
            expected = hashlib.sha256(original).hexdigest()
            self.assertEqual(exported["input_digest"], expected)
            self.assertEqual(exported["artifact_hash"], expected)
