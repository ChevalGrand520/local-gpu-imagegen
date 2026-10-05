"""Native Windows owner-liveness regression; no backend or GPU access."""

import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from local_gpu_imagegen.run_store import is_process_alive


@unittest.skipUnless(os.name == "nt", "Requires native Windows process handles")
class WindowsOwnerLivenessTests(unittest.TestCase):
    def test_exited_child_with_retained_handle_is_not_alive(self):
        child = subprocess.Popen(
            [sys.executable, "-c", "import sys; sys.stdin.readline()"],
            stdin=subprocess.PIPE,
        )
        try:
            self.assertTrue(is_process_alive(child.pid))
            child.communicate(b"exit\n", timeout=10)
            self.assertEqual(child.returncode, 0)
            # Popen retains its Windows process handle until object destruction.
            # OpenProcess can still succeed: it does not establish liveness.
            self.assertFalse(is_process_alive(child.pid))
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
