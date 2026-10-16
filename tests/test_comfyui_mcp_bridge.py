"""Boundary and cross-process durability tests; no actual ComfyUI/GPU."""
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'integrations/comfyui_mcp'
spec = importlib.util.spec_from_file_location('durable_bridge', DIR / 'bridge.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.events = self.root / 'events.jsonl'
        self.command = [sys.executable, str(DIR / 'fake_mcp.py')]
        self.env = patch.dict(os.environ, {'BRIDGE_TEST_EVENTS': str(self.events), 'BRIDGE_TEST_FAULT': ''})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.graph = {'3': {'class_type': 'KSampler', 'inputs': {'seed': 42}}}
        self.workflow = self.root / 'workflow.json'
        self.workflow.write_text(json.dumps(self.graph))

    def client(self, mode='full', endpoint='loopback-fixture', db=None):
        client = b.DurableClient(db or self.root / 'runs.sqlite', self.command, endpoint, mode=mode)
        self.addCleanup(client.close)
        return client

    def calls(self):
        return [json.loads(s) for s in self.events.read_text().splitlines()] if self.events.exists() else []

    def cli(self, action, mode='full', fault=''):
        return subprocess.run([sys.executable, str(DIR/'bridge.py'),
                               '--database', str(self.root/'runs.sqlite'), '--endpoint', 'loopback-fixture',
                               '--mode', mode, '--action', action, '--run-id', 'run', '--key', 'key',
                               '--workflow', str(self.workflow), '--', *self.command],
                              env={**os.environ, 'BRIDGE_TEST_FAULT': fault},
                              text=True, capture_output=True, timeout=10)

    def test_cross_process_known_id_and_read_only_reentry(self):
        first = self.cli('submit')
        self.assertEqual(first.returncode, 0, first.stderr)
        result = self.cli('submit')
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertFalse(value['completion_verified'])  # no history != generated
        self.assertEqual([c['name'] for c in self.calls()], ['enqueue_workflow', 'get_history'])
        self.assertEqual(self.calls()[1]['arguments']['prompt_id'], 'fixture-job-1')
        self.assertEqual(self.calls()[0]['arguments']['workflow'], self.graph)

    def test_stop_allows_explicit_history(self):
        client = self.client('stop')
        client.submit('run', 'key', self.graph)
        client.submit('run', 'key', self.graph)
        self.assertEqual(len(self.calls()), 1)
        client.read_history('run')
        self.assertEqual(len(self.calls()), 2)

    def test_native_reentry_submits_again_by_defined_caller_policy(self):
        client = self.client('native')
        client.submit('run', 'key', self.graph)
        client.submit('run', 'key', self.graph)
        self.assertEqual([c['name'] for c in self.calls()], ['enqueue_workflow'] * 2)
        self.assertFalse((self.root / 'runs.sqlite').exists())

    def test_unknown_reply_and_crash_block_across_processes(self):
        for fault in ['crash', 'is_error', 'no_id']:
            with self.subTest(fault=fault):
                database = self.root / 'runs.sqlite'
                database.unlink(missing_ok=True)
                self.events.unlink(missing_ok=True)
                self.assertNotEqual(self.cli('submit', fault=fault).returncode, 0)
                second = self.cli('submit')
                self.assertNotEqual(second.returncode, 0)
                self.assertIn('no automatic resubmission', second.stderr)
                self.assertEqual(len(self.calls()), 1)

    def test_conflicts_never_touch_upstream(self):
        client = self.client()
        client.submit('run', 'key', self.graph)
        for key, graph in [('new', self.graph), ('key', {'seed': 43})]:
            with self.assertRaisesRegex(b.BridgeError, 'conflict'):
                client.submit('run', key, graph)
        with self.assertRaisesRegex(b.BridgeError, 'conflict'):
            self.client(endpoint='different').submit('run', 'key', self.graph)
        with self.assertRaisesRegex(b.BridgeError, 'context conflict'):
            self.client(endpoint='different').read_history('run')
        self.assertEqual(len(self.calls()), 1)

    def test_failed_history_read_keeps_binding_and_can_retry(self):
        self.client().submit('run', 'key', self.graph)
        os.environ['BRIDGE_TEST_FAULT'] = 'history_error'
        with self.assertRaises(b.BridgeError):
            self.client().read_history('run')
        os.environ['BRIDGE_TEST_FAULT'] = ''
        self.client().read_history('run')
        self.assertEqual([c['name'] for c in self.calls()].count('enqueue_workflow'), 1)

    def test_concurrent_clients_reserve_once(self):
        def submit(_):
            try:
                client = b.DurableClient(self.root/'runs.sqlite', self.command, 'loopback-fixture')
                try:
                    return client.submit('run', 'key', self.graph)
                finally:
                    client.close()
            except b.BridgeError:
                return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(submit, range(3)))
        self.assertEqual([c['name'] for c in self.calls()].count('enqueue_workflow'), 1)

    def test_before_send_intent_false_block(self):
        client = self.client()
        binding = b.digest({'key':'key', 'workflow':self.graph, 'context':client.context_digest()})
        client.db.execute("INSERT INTO runs VALUES (?,?,'submitting',NULL,NULL,?)",
                          ('run', binding, client.context_digest()))
        client.db.commit()
        with self.assertRaises(b.BridgeError):
            client.submit('run','key',self.graph)
        self.assertEqual(self.calls(), [])
        self.assertEqual(client.inspect('run')['state'], 'unknown')

    def test_reordered_graph_hashes_same_and_invalid_numbers_do_not_reserve(self):
        client = self.client()
        with self.assertRaises(ValueError):
            client.submit('run','key',{'seed':float('nan')})
        self.assertEqual(client.db.execute('SELECT count(*) FROM runs').fetchone()[0], 0)
        self.assertEqual(b.digest({'b':2,'a':1}),b.digest({'a':1,'b':2}))


if __name__ == '__main__':
    unittest.main()
