from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.research.execution_oracle import ExecutionOracle, run_oracle_self_checks  # noqa: E402


class ExecutionOracleTests(unittest.TestCase):
    def test_required_self_checks_pass(self) -> None:
        checks = run_oracle_self_checks()
        self.assertEqual(len(checks), 4)
        self.assertTrue(all(check["passed"] for check in checks))

    def test_post_count_is_not_execution_count(self) -> None:
        oracle = ExecutionOracle("post-only")
        oracle.request_received("op", "job-1", "prompt-1")
        oracle.queue_item_created("op", "job-1", "prompt-1")
        oracle.request_received("op", "job-2", "prompt-1")
        oracle.queue_item_created("op", "job-2", "prompt-1")
        result = oracle.snapshot()
        self.assertEqual(result["request_received"], 2)
        self.assertEqual(result["execution_started"], 0)
        self.assertEqual(result["execution_state"], "not_started")

    def test_same_prompt_id_gets_distinct_execution_instances(self) -> None:
        oracle = ExecutionOracle("duplicate-execution")
        instances = []
        for job_id in ("job-1", "job-2"):
            oracle.request_received("op", job_id, "same-prompt")
            oracle.queue_item_created("op", job_id, "same-prompt")
            execution_id = oracle.execution_started("op", job_id, "same-prompt")
            oracle.execution_finished(execution_id)
            instances.append(execution_id)
        self.assertEqual(instances[0] != instances[1], True)
        self.assertEqual(oracle.snapshot()["execution_started"], 2)

    def test_started_without_finish_is_unknown(self) -> None:
        oracle = ExecutionOracle("lost-completion")
        oracle.request_received("op", "job-1", "prompt-1")
        oracle.queue_item_created("op", "job-1", "prompt-1")
        oracle.execution_started("op", "job-1", "prompt-1")
        result = oracle.snapshot()
        self.assertEqual(result["execution_state"], "unknown")
        self.assertFalse(result["oracle_evaluable"])

    def test_finish_for_the_wrong_instance_is_unknown(self) -> None:
        oracle = ExecutionOracle("wrong-instance")
        oracle.request_received("op", "job-1", "prompt-1")
        oracle.queue_item_created("op", "job-1", "prompt-1")
        execution_id = oracle.execution_started("op", "job-1", "prompt-1")
        self.assertNotEqual(execution_id, "wrong-instance:execution-9999")
        oracle.execution_finished("wrong-instance:execution-9999")
        result = oracle.snapshot()
        self.assertEqual(result["execution_state"], "unknown")
        self.assertFalse(result["oracle_evaluable"])
