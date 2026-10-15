"""Independent journal comparison against a synthetic MCP process only."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'integrations/comfyui_mcp'
sys.path.insert(0,str(HERE))
from minimal_baseline import MinimalClient
from bridge import BridgeError


class MinimalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.events=self.root/'events'
        self.config=self.root/'config.json'
        self.config.write_text(json.dumps({'database':str(self.root/'minimal.sqlite'),
            'command':[sys.executable,str(HERE/'fake_mcp.py')], 'endpoint':'cpu-fixture',
            'graph':{'2':{'class_type':'Fixture','inputs':{'seed':42}}}}))

    def run_worker(self,action='submit',fault='',transport_fault=''):
        return subprocess.run([sys.executable,str(HERE/'fault_worker.py'),str(self.config),
            'minimal',action,fault],env={**os.environ,'BRIDGE_TEST_EVENTS':str(self.events),
            'BRIDGE_TEST_FAULT':transport_fault},capture_output=True,text=True,timeout=10)

    def calls(self):
        return [json.loads(x) for x in self.events.read_text().splitlines()] if self.events.exists() else []

    def test_known_id_restart_and_explicit_history(self):
        for action in ('submit','submit','history'):
            r=self.run_worker(action);self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual([c['name'] for c in self.calls()],['enqueue_workflow','get_history'])

    def test_all_crash_windows(self):
        for fault,exitcode,expected_calls in [('before_send',71,0),('before_binding',72,1),('after_binding',73,1)]:
            with self.subTest(fault=fault):
                (self.root/'minimal.sqlite').unlink(missing_ok=True);self.events.unlink(missing_ok=True)
                self.assertEqual(self.run_worker(fault=fault).returncode,exitcode)
                again=self.run_worker()
                self.assertEqual(again.returncode,0 if fault=='after_binding' else 2)
                self.assertEqual(len(self.calls()),expected_calls)

    def test_uncertain_reply_stops_after_restart(self):
        self.assertEqual(self.run_worker(transport_fault='no_id').returncode,2)
        self.assertEqual(self.run_worker().returncode,2)
        self.assertEqual(len(self.calls()),1)

    def test_changes_conflict_without_upstream_call(self):
        self.assertEqual(self.run_worker().returncode,0)
        for action in ('changed_key','changed_seed'):
            r=self.run_worker(action);self.assertEqual(r.returncode,2)
            self.assertIn('conflict',r.stdout)
        self.assertEqual(len(self.calls()),1)

    def test_history_failure_retry(self):
        self.assertEqual(self.run_worker().returncode,0)
        self.assertEqual(self.run_worker('history',transport_fault='history_error').returncode,2)
        self.assertEqual(self.run_worker('history').returncode,0)
        self.assertEqual([c['name'] for c in self.calls()],['enqueue_workflow','get_history','get_history'])

    def test_concurrent_independent_journal(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            results=list(pool.map(lambda _:self.run_worker(),range(3)))
        self.assertTrue(all(r.returncode in (0,2) for r in results))
        self.assertEqual([c['name'] for c in self.calls()],['enqueue_workflow'])


if __name__=='__main__':unittest.main()
