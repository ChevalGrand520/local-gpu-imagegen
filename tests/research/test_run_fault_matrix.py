from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.run_fault_matrix import CASE_SPECS, run_matrix  # noqa: E402


class FaultMatrixSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = run_matrix()
        cls.cases = {case["case_id"]: case for case in cls.matrix["cases"]}

    def test_fault_and_control_denominators_are_separate(self) -> None:
        self.assertEqual(tuple(self.cases), tuple(case_id for case_id, _, _ in CASE_SPECS))
        self.assertEqual(self.matrix["denominators"]["control_cases"]["scheduled"], 2)
        self.assertEqual(self.matrix["denominators"]["fault_cases"]["scheduled"], 4)
        self.assertNotIn("injection-confirmed", self.matrix["denominators"]["control_cases"])
        self.assertEqual(self.matrix["deterministic_fault_coverage"]["fault_case_count"], 4)
        self.assertEqual(self.matrix["deterministic_fault_coverage"]["injection_confirmed_case_count"], 4)

    def test_each_case_has_expected_barrier_job_submission_execution_and_recovery(self) -> None:
        expected = {
            "F00-single-stage": {
                "code": None,
                "barrier": None,
                "job_id": None,
                "submissions": 1,
                "executions": 1,
                "jobs_distinct": True,
                "boundary": "resolved",
                "recovery": "not_needed",
            },
            "F00-two-stage": {
                "code": None,
                "barrier": None,
                "job_id": None,
                "submissions": 1,
                "executions": 1,
                "jobs_distinct": True,
                "boundary": "resolved",
                "recovery": "not_needed",
            },
            "F02-single-stage": {
                "code": "backend_request_failed",
                "barrier": "after_execution_before_job_id_response",
                "job_id": None,
                "submissions": 2,
                "executions": 2,
                "jobs_distinct": True,
                "boundary": "unresolved",
                "recovery": "new_submission_after_fault",
            },
            "F02-two-stage": {
                "code": "backend_request_failed",
                "barrier": "after_execution_before_job_id_response",
                "job_id": None,
                "submissions": 1,
                "executions": 1,
                "jobs_distinct": True,
                "boundary": "unresolved",
                "recovery": "outcome_unknown",
            },
            "F03-single-stage": {
                "code": "comfyui_job_timed_out",
                "barrier": "after_job_id_known_before_completion_response",
                "job_id": "present",
                "submissions": 2,
                "executions": 2,
                "jobs_distinct": True,
                "boundary": "unresolved",
                "recovery": "new_submission_after_fault",
            },
            "F03-two-stage": {
                "code": "comfyui_job_timed_out",
                "barrier": "after_job_id_known_before_completion_response",
                "job_id": "present",
                "submissions": 1,
                "executions": 1,
                "jobs_distinct": True,
                "boundary": "resolved",
                "recovery": "same_job_reconciled",
            },
        }
        for case_id, expectation in expected.items():
            with self.subTest(case_id=case_id):
                case = self.cases[case_id]
                self.assertEqual(case["first_error_code"], expectation["code"])
                self.assertEqual(case["first_error_barrier"], expectation["barrier"])
                if expectation["job_id"] == "present":
                    self.assertIsInstance(case["first_error_job_id"], str)
                    self.assertTrue(case["first_error_job_id"])
                else:
                    self.assertEqual(case["first_error_job_id"], expectation["job_id"])
                self.assertEqual(case["backend_submission_count"], expectation["submissions"])
                self.assertEqual(case["oracle_execution_count"], expectation["executions"])
                self.assertEqual(
                    len(case["submitted_job_ids"]) == len(set(case["submitted_job_ids"])),
                    expectation["jobs_distinct"],
                )
                self.assertEqual(case["boundary_classification"]["state"], expectation["boundary"])
                self.assertEqual(case["recovery"]["state"], expectation["recovery"])
                self.assertTrue(case["oracle_evaluable"])

    def test_execution_observations_are_not_failure_rates(self) -> None:
        observations = self.matrix["execution_observations"]
        self.assertTrue(observations["counts_are_not_deployment_failure_or_duplicate_execution_rates"])
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                raw_record = case["raw_and_normalized"]["raw_record"]
                reported_state = raw_record["reported_state"]
                self.assertEqual(
                    reported_state["request"]["model_choice"],
                    "research-cpu-fake-model",
                )
        self.assertEqual(
            observations["duplicate_execution_case_ids"],
            ["F02-single-stage", "F03-single-stage"],
        )
        self.assertEqual(
            self.matrix["deterministic_fault_coverage"]["resolved_case_ids"],
            ["F03-two-stage"],
        )
