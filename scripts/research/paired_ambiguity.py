"""Shared paired-v1 retry schedule and measurement helpers (no GPU launcher)."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import time

PROTOCOL = "paired-ambiguity-v1"
PRODUCTS = {"B2": "da65d57047b5a59e3403b49adf4605a1c0497c58",
            "W3": "d45173af75d404ad79dc14568edd4c45f654abd2"}
WINDOWS_ORDER = (("B2", "F00"), ("W3", "F00"), ("W3", "F02"),
                 ("B2", "F02"), ("B2", "FPRE"), ("W3", "FPRE"))
RETRY_DELAY_SECONDS = 1.0


def semantic_digest(arguments):
    """Generation semantics including seed; retain raw arguments separately.

    Exclusions are run/key identities, change-summary prose and locked route
    identity tokens. Model, workflow/compiler identities and parameters remain.
    """
    value = copy.deepcopy(arguments)
    for key in ("run_id", "idempotency_key", "change_summary"):
        value.pop(key, None)
    plan = value.get("plan", {})
    for key in ("route_token", "endpoint_identity"):
        plan.pop(key, None)
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def caller_unknown(result):
    # Frozen before measurement: this transport error gives no acceptance
    # receipt. Both native products expose the same code to the research caller.
    return (result.get("client_error_stage") == "generate_round"
            and result.get("client_error_code") == "backend_request_failed")


def run_schedule(invoke, *, fault, strategy, deadline, clock=time.monotonic,
                 sleep=time.sleep):
    """Invoke on return+1s, without consulting an observer or backend truth.

    `invoke(index, remaining_seconds)` must impose its own hard call timeout.
    This helper never interrupts a product process from another thread.
    """
    if fault not in {"F00", "F02", "FPRE"} or strategy not in {"B2", "W3", "P-stop"}:
        raise ValueError("invalid paired condition")
    if deadline <= clock():
        raise TimeoutError("operation deadline expired before first call")
    first = invoke(1, deadline - clock())
    returned_at = clock()
    calls = [first]
    if fault == "F00":
        return calls, "control"
    if not caller_unknown(first):
        return calls, "first_call_not_unknown"
    if strategy == "P-stop":
        return calls, "caller_stop_after_unknown"
    due = returned_at + RETRY_DELAY_SECONDS
    if due >= deadline:
        return calls, "deadline_before_retry"
    sleep(max(0.0, due - clock()))
    if clock() >= deadline:
        return calls, "deadline_before_retry"
    calls.append(invoke(2, deadline - clock()))
    return calls, "retried_same_run"


def prompt_metrics(receipts, stages):
    prompts = [r for r in receipts if r["method"] == "POST" and r["path"].split("?")[0] == "/prompt"]
    sends = {s["request_sequence"] for s in stages if s["stage"] == "upstream_send_started"
             and s["method"] == "POST" and s["path"].split("?")[0] == "/prompt"}
    accepted = {r["accepted_job_id"] for r in prompts if r["accepted_job_id"] is not None
                and r["upstream_status"] is not None and 200 <= r["upstream_status"] < 300}
    return {"S_proxy": len(prompts), "S_upstream": len(sends), "A": len(accepted)}


def lifecycle_count(snapshots):
    """Deduplicate cumulative CPU snapshots; incomplete accepted jobs stay unknown."""
    events = {}
    for snapshot in snapshots:
        for event in snapshot["events"]:
            key = json.dumps(event, sort_keys=True)
            events[key] = event
    starts = {e["execution_instance_id"] for e in events.values() if e["event"] == "execution_started"}
    ends = {e["execution_instance_id"] for e in events.values() if e["event"] == "execution_finished"}
    jobs = {e["job_id"] for e in events.values() if e["event"] == "request_received"}
    started_jobs = {e["job_id"] for e in events.values() if e["event"] == "execution_started"}
    return len(starts) if starts == ends and jobs == started_jobs else None
