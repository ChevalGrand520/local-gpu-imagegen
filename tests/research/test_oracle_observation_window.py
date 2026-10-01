"""Real local socket witnesses for quiet intervals and partial frame delivery."""
import json
import socket
import threading
import time
import unittest
from unittest.mock import patch

from scripts.research.f02_oracle import ComfyUIEventOracle


def frame(kind, data):
    body = json.dumps({"type": kind, "data": data}).encode()
    return bytes([0x81, len(body)]) + body


class ObservationWindowTests(unittest.TestCase):
    def test_silence_and_delayed_frame_body_do_not_end_window(self):
        reader, writer = socket.socketpair()
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity="fixture", observer_id="fixture", timeout_seconds=.05)
        oracle._socket = reader
        errors = []

        def send():
            try:
                writer.sendall(frame("execution_start", {"prompt_id": "job"}))
                time.sleep(1.15)
                terminal = frame("executing", {"prompt_id": "job", "node": None})
                writer.sendall(terminal[:3])
                time.sleep(.15)
                writer.sendall(terminal[3:])
            except Exception as error:
                errors.append(error)

        thread = threading.Thread(target=send)
        thread.start()
        try:
            with patch.object(oracle, "_history", return_value={"job": {"status": {"status_str": "success"}, "outputs": {}}}):
                decision = oracle.observe_until(["job"], deadline_monotonic=time.monotonic()+3)
            self.assertTrue(decision.oracle_evaluable)
            self.assertEqual(len(decision.bindings), 1)
        finally:
            thread.join(timeout=3)
            reader.close()
            writer.close()
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])

    def test_silent_socket_waits_until_fixed_deadline(self):
        reader, writer = socket.socketpair()
        oracle = ComfyUIEventOracle("http://127.0.0.1:8202", backend_boot_identity="fixture", observer_id="fixture", timeout_seconds=.02)
        oracle._socket = reader
        started = time.monotonic()
        try:
            with patch.object(oracle, "_history", return_value={}):
                decision = oracle.observe_until(["job"], deadline_monotonic=started+.12)
            self.assertGreaterEqual(time.monotonic()-started, .10)
            self.assertFalse(decision.oracle_evaluable)
        finally:
            reader.close()
            writer.close()
