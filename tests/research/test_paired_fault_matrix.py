from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.run_paired_fault_matrix import (  # noqa: E402
    compare_results,
    run_matrix,
    write_json_exclusive,
)


class PairedFaultMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = run_matrix(system_label="CURRENT", source_sha="1" * 40)
        cls.cases = {case["case_id"]: case for case in cls.matrix["cases"]}

    def test_protocol_identity_and_denominators_are_explicit(self) -> None:
        self.assertEqual(self.matrix["protocol_version"], "paired-ambiguous-submit-v2")
        self.assertEqual(self.matrix["system_label"], "CURRENT")
        self.assertEqual(self.matrix["source_sha"], "1" * 40)
        runtime = self.matrix["runtime_identity"]
        self.assertEqual(len(runtime["checkout_head"]), 40)
        self.assertTrue(runtime["python_version"])
        self.assertEqual(runtime["output_root_policy"], "isolated_temporary_run_root_per_case")
        self.assertEqual(
            set(runtime["harness_sha256"]),
            {"execution_oracle.py", "run_paired_fault_matrix.py", "test_paired_fault_matrix.py"},
        )
        self.assertTrue(all(len(value) == 64 for value in runtime["harness_sha256"].values()))
        self.assertEqual(self.matrix["denominators"]["control_cases"]["scheduled"], 2)
        self.assertEqual(self.matrix["denominators"]["fault_cases"]["scheduled"], 4)
        self.assertNotIn("injection-confirmed", self.matrix["denominators"]["control_cases"])
        self.assertEqual(self.matrix["denominators"]["fault_cases"]["injection-confirmed"], 4)
        self.assertEqual(len(self.matrix["oracle_self_checks"]), 4)

    def test_f00_controls_complete_without_product_error(self) -> None:
        for path_kind in ("single-stage", "two-stage"):
            with self.subTest(path_kind=path_kind):
                case = self.cases[f"F00-{path_kind}"]
                self.assertIsNone(case["first_error_code"])
                self.assertTrue(case["valid_completion"])
                self.assertEqual(case["recovery"]["state"], "not_needed")
                self.assertEqual(case["backend_submission_count"], 1)
                self.assertEqual(case["oracle_execution_count"], 1)

    def test_f02_uses_transport_marker_and_worker_observations_consistently(self) -> None:
        marker = self.matrix["transport_preflight"]["submission_outcome_unknown"]
        self.assertIs(type(marker), bool)
        for path_kind in ("single-stage", "two-stage"):
            with self.subTest(path_kind=path_kind):
                case = self.cases[f"F02-{path_kind}"]
                self.assertEqual(case["first_error_code"], "backend_request_failed")
                self.assertEqual(case["first_error_barrier"], "after_execution_before_job_id_response")
                self.assertEqual(case["first_error_submission_outcome"], "unknown" if marker else None)
                self.assertTrue(case["injection_confirmed"])
                self.assertTrue(case["oracle_evaluable"])
                if marker:
                    self.assertEqual(case["backend_submission_count"], 1)
                    self.assertEqual(case["oracle_execution_count"], 1)
                    self.assertEqual(case["recovery"]["state"], "outcome_unknown_blocked")
                    self.assertEqual(case["second_error_code"], "submission_outcome_unknown")
                elif path_kind == "single-stage":
                    self.assertEqual(case["backend_submission_count"], 2)
                    self.assertEqual(case["oracle_execution_count"], 2)
                    self.assertEqual(case["recovery"]["state"], "new_submission_after_fault")
                else:
                    self.assertEqual(case["backend_submission_count"], 1)
                    self.assertEqual(case["oracle_execution_count"], 1)
                    self.assertEqual(case["recovery"]["state"], "outcome_unknown")
                    self.assertEqual(case["second_error_code"], "two_stage_run_partial")

    def test_f03_two_stage_recovers_same_job_without_worker_reentry(self) -> None:
        case = self.cases["F03-two-stage"]
        self.assertEqual(case["first_error_code"], "comfyui_job_timed_out")
        self.assertEqual(case["first_error_barrier"], "after_job_id_known_before_completion_response")
        self.assertEqual(case["backend_submission_count"], 1)
        self.assertEqual(case["oracle_execution_count"], 1)
        self.assertEqual(case["recovery"]["state"], "same_job_reconciled")
        self.assertEqual(case["recovery"]["recovery_invocation_count"], 1)
        self.assertEqual(case["worker_execution_entry_count"], 1)

    def test_comparison_joins_all_rows_without_claiming_a_rate(self) -> None:
        b2 = json.loads(json.dumps(self.matrix))
        b2["system_label"] = "B2"
        w3 = json.loads(json.dumps(self.matrix))
        w3["system_label"] = "W3"
        comparison = compare_results(b2, w3)
        self.assertEqual(len(comparison["pairs"]), 6)
        self.assertEqual(comparison["paired_case_count"], 6)
        self.assertTrue(comparison["deterministic_coverage_not_deployment_rate"])
        self.assertNotIn("duplicate_execution_rate", comparison)

    def test_result_writer_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            write_json_exclusive(output, {"first": True})
            with self.assertRaises(FileExistsError):
                write_json_exclusive(output, {"second": True})


if __name__ == "__main__":
    unittest.main()
