"""No-GPU checks of the hard prompt and wall budgets."""
from pathlib import Path
import tempfile
import unittest

from scripts.research.spe_real_recovery import audit, check_send_budget, sends


class RealProbeBudgetTests(unittest.TestCase):
    def test_response_loss_still_consumes_budget_and_fourth_send_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "http.jsonl"
            for index in range(3):
                check_send_budget(path, 10, now=0)
                # No response record: a lost response must not refund a send.
                audit(path, {"event": "send_intent", "index": index + 1})
            self.assertEqual(sends(path), 3)
            with self.assertRaisesRegex(RuntimeError, "prompt_budget_exhausted"):
                check_send_budget(path, 10, now=0)

    def test_expired_window_blocks_even_first_send(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "wall_budget_exhausted"):
                check_send_budget(Path(directory) / "http.jsonl", 10, now=10)


if __name__ == "__main__":
    unittest.main()
