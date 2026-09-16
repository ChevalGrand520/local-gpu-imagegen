"""Independent CPU execution oracle for research fault cases."""

from __future__ import annotations

import copy


class ExecutionOracle:
    """Record backend lifecycle events without deriving execution from POST count."""

    def __init__(self, case_id: str) -> None:
        self.case_id = case_id
        self._events: list[dict[str, object]] = []
        self._execution_counter = 0

    def request_received(self, operation_id: str, job_id: str, prompt_id: str | None = None) -> None:
        self._record("request_received", operation_id, job_id, prompt_id)

    def queue_item_created(self, operation_id: str, job_id: str, prompt_id: str | None = None) -> None:
        self._record("queue_item_created", operation_id, job_id, prompt_id)

    def execution_started(self, operation_id: str, job_id: str, prompt_id: str | None = None) -> str:
        self._execution_counter += 1
        execution_id = f"{self.case_id}:execution-{self._execution_counter:04d}"
        self._record("execution_started", operation_id, job_id, prompt_id, execution_id)
        return execution_id

    def execution_finished(
        self,
        execution_instance_id: str,
        *,
        outcome: str = "succeeded",
    ) -> None:
        if outcome not in {"succeeded", "failed"}:
            raise ValueError("execution outcome must be succeeded or failed")
        self._events.append({
            "event": "execution_finished",
            "execution_instance_id": execution_instance_id,
            "outcome": outcome,
        })

    def snapshot(self) -> dict[str, object]:
        started = [event for event in self._events if event["event"] == "execution_started"]
        finished = [event for event in self._events if event["event"] == "execution_finished"]
        requests = [event for event in self._events if event["event"] == "request_received"]
        queued = [event for event in self._events if event["event"] == "queue_item_created"]
        started_ids = {
            event.get("execution_instance_id")
            for event in started
        }
        finished_ids = {
            event.get("execution_instance_id")
            for event in finished
        }
        if not started:
            execution_state = "not_started"
        elif len(finished) != len(started) or started_ids != finished_ids:
            execution_state = "unknown"
        elif any(event.get("outcome") == "failed" for event in finished):
            execution_state = "failed"
        else:
            execution_state = "succeeded"
        job_ids = []
        for event in requests:
            job_id = event.get("job_id")
            if job_id not in job_ids:
                job_ids.append(job_id)
        return {
            "oracle_type": "independent_cpu_execution_oracle_v1",
            "case_id": self.case_id,
            "execution_state": execution_state,
            "oracle_evaluable": len(finished) == len(started) and started_ids == finished_ids,
            "request_received": len(requests),
            "queue_item_created": len(queued),
            "execution_started": len(started),
            "execution_finished": len(finished),
            "execution_instances": [
                event["execution_instance_id"] for event in started
            ],
            "job_ids": job_ids,
            "events": copy.deepcopy(self._events),
        }

    def _record(
        self,
        event: str,
        operation_id: str,
        job_id: str,
        prompt_id: str | None,
        execution_instance_id: str | None = None,
    ) -> None:
        value: dict[str, object] = {
            "event": event,
            "operation_id": operation_id,
            "job_id": job_id,
            "prompt_id": prompt_id,
        }
        if execution_instance_id is not None:
            value["execution_instance_id"] = execution_instance_id
        self._events.append(value)


def run_oracle_self_checks() -> list[dict[str, object]]:
    """Run the four minimum checks required before execution metrics are used."""
    checks: list[dict[str, object]] = []

    zero = ExecutionOracle("self-two-post-zero")
    for _ in range(2):
        zero.request_received("op", "job-a", "prompt-a")
        zero.queue_item_created("op", "job-a", "prompt-a")
    zero_result = zero.snapshot()
    _assert_counts(zero_result, requests=2, started=0, finished=0)
    checks.append({"name": "two_post_zero_execution", "passed": True, "snapshot": zero_result})

    one = ExecutionOracle("self-two-post-one")
    for index in range(2):
        one.request_received("op", f"job-{index}", "prompt-a")
        one.queue_item_created("op", f"job-{index}", "prompt-a")
    execution_id = one.execution_started("op", "job-1", "prompt-a")
    one.execution_finished(execution_id)
    one_result = one.snapshot()
    _assert_counts(one_result, requests=2, started=1, finished=1)
    checks.append({"name": "two_post_one_execution", "passed": True, "snapshot": one_result})

    same_prompt = ExecutionOracle("self-same-prompt-two-executions")
    for job_id in ("job-1", "job-2"):
        same_prompt.request_received("op", job_id, "prompt-same")
        same_prompt.queue_item_created("op", job_id, "prompt-same")
        execution_id = same_prompt.execution_started("op", job_id, "prompt-same")
        same_prompt.execution_finished(execution_id)
    same_prompt_result = same_prompt.snapshot()
    _assert_counts(same_prompt_result, requests=2, started=2, finished=2)
    if len(same_prompt_result["execution_instances"]) != 2:
        raise AssertionError("same prompt ID executions did not receive distinct instance IDs")
    checks.append({"name": "same_prompt_id_two_executions", "passed": True, "snapshot": same_prompt_result})

    dropped = ExecutionOracle("self-started-completion-lost")
    dropped.request_received("op", "job-lost", "prompt-lost")
    dropped.queue_item_created("op", "job-lost", "prompt-lost")
    dropped.execution_started("op", "job-lost", "prompt-lost")
    dropped_result = dropped.snapshot()
    _assert_counts(dropped_result, requests=1, started=1, finished=0)
    if dropped_result["execution_state"] != "unknown" or dropped_result["oracle_evaluable"] is not False:
        raise AssertionError("missing completion signal was not classified as unknown")
    checks.append({"name": "started_completion_signal_lost", "passed": True, "snapshot": dropped_result})
    return checks


def _assert_counts(
    value: dict[str, object],
    *,
    requests: int,
    started: int,
    finished: int,
) -> None:
    if (
        value["request_received"] != requests
        or value["execution_started"] != started
        or value["execution_finished"] != finished
    ):
        raise AssertionError(f"unexpected oracle counts: {value}")
