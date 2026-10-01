"""One synthetic operation against an exact archived B2/W3 product tree.

The dispatch adapter calls public engine entry points, not MCP stdio. Backend
HTTP, response loss and PNG validation are real CPU paths; the worker/model are
synthetic. No product state is edited by the research caller.
"""
from __future__ import annotations

import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch


def run(root: Path, strategy: str, fault: str, capture: Path, probe: str | None):
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "scripts"))
    # Load the product fixture before importing the current research harness.
    import tests.test_asset_run_engine as product_fixture
    from local_gpu_imagegen.backends.base import BoundedJsonClient
    from local_gpu_imagegen.errors import AssetEngineError
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.research import f02_product_client as caller
    from scripts.research.execution_oracle import ExecutionOracle
    from scripts.research.f02_loopback import OneShotLoopbackFaultProxy
    from scripts.research.run_paired_fault_matrix import LocalhostJsonServer
    from scripts.research.paired_ambiguity import (
        PROTOCOL, PRODUCTS, lifecycle_count, prompt_metrics, run_schedule, semantic_digest,
    )
    from scripts.research.f02_capture import write_private_json

    imported_product_files = {}
    for name, module in tuple(sys.modules.items()):
        if name.startswith("local_gpu_imagegen") and getattr(module, "__file__", None):
            location = Path(module.__file__).resolve()
            if not location.is_relative_to(root.resolve()):
                raise RuntimeError("product import escaped archived pinned tree")
            imported_product_files[str(location.relative_to(root))] = sha256(location.read_bytes()).hexdigest()

    fixture = product_fixture.AssetRunEngineTests("runTest")
    fixture.setUp()
    oracle = ExecutionOracle(f"cpu-{strategy}-{fault}-{probe or 'same-run'}")
    pending, generated_arguments, snapshots, worker_artifacts = {}, [], [], []
    delegate = product_fixture.FakeBackendRunner()
    backend_requests = []

    def accept(value):
        request = pending.pop(value["request_token"])
        job = f"cpu-job-{len(backend_requests) + 1}"
        backend_requests.append(copy.deepcopy(value))
        key = str(request["idempotency_key"])
        oracle.request_received(key, job, key)
        oracle.queue_item_created(key, job, key)
        execution = oracle.execution_started(key, job, key)
        result = delegate(request)
        artifact = Path(result["path"]).read_bytes()
        retained = capture / f"{job}.png"
        retained.write_bytes(artifact)  # Product failure cleanup may delete its pending output.
        digest = sha256(artifact).hexdigest()
        worker_artifacts.append({"job_id": job, "sha256": digest, "bytes": len(artifact),
                                 "retained_file": retained.name})
        oracle.execution_finished(execution, artifact_hash=digest)
        return {"prompt_id": job, "result": result}, False

    class EngineDispatch:
        def __init__(self, _root, _env):
            pass

        def call(self, name, arguments):
            try:
                if name == "local_gpu_start_run":
                    return fixture.start(max_rounds=1)
                if name == "local_gpu_get_run":
                    return fixture.engine.get_run(arguments)
                if name == "local_gpu_generate_round":
                    generated_arguments.append(copy.deepcopy(arguments))
                    data, _preview = fixture.engine.generate_round(arguments)
                    return data  # Same unpacking as the product MCP dispatcher.
                raise AssertionError(name)
            except AssetEngineError as error:
                raise caller.ProductClientError(error.code) from error

        def close(self):
            pass

    try:
        with LocalhostJsonServer(accept) as upstream, OneShotLoopbackFaultProxy(
            upstream.url, fault_mode=fault, stage_log_path=capture / "proxy-stages.jsonl",
        ) as proxy:
            http = BoundedJsonClient(proxy.base_url, timeout=3.0)

            def backend(request):
                token = f"request-{len(pending) + len(backend_requests) + 1}"
                pending[token] = request
                value = {"request_token": token,
                         **{k: request.get(k) for k in ("seed", "width", "height", "mode", "positive_prompt", "negative_prompt")}}
                return http.post_json("/prompt", value)["result"]

            fixture.engine.backend_runner = backend
            boundary = {"profile": "standalone-illustration", "model_choice": product_fixture.TEST_MODEL_ID,
                        "backend": "webui", "authorization_scope": "private", "route_token": "cpu-fixture"}

            def build_plan(request, seed):
                plan = fixture.plan(max_rounds=1, route=request["route"])
                plan["parameters"]["seed"] = seed
                return plan

            with patch.object(caller, "StdioMcp", EngineDispatch), patch.object(caller, "_initialise"), \
                 patch.object(caller, "_discover_route", return_value={"boundary": boundary}), \
                 patch.object(caller, "_build_plan", side_effect=build_plan):
                kwargs = dict(case_id=f"{strategy}_{fault}", operation_key="paired-cpu-fixed-key",
                              output_root=str(fixture.output_root), capture_root=capture / "client",
                              protocol=PROTOCOL)

                def invoke(index, remaining):
                    if remaining <= 0:
                        raise TimeoutError("CPU operation expired")
                    result = caller.run_same_run(root, call_index=index, **kwargs)
                    snapshots.append(oracle.snapshot())
                    return result

                if probe is None:
                    calls, schedule_reason = run_schedule(invoke, fault=fault, strategy=strategy,
                                                         deadline=time.monotonic() + 20)
                else:
                    calls = [invoke(1, 20)]
                    session = json.loads((capture / "client/session.json").read_text())
                    args = copy.deepcopy(session["generate_arguments"])
                    if probe == "healthy-replay":
                        calls.append(invoke(2, 20))
                    else:
                        if probe == "unknown-new-key":
                            args["idempotency_key"] = "new-key-after-unknown"
                        elif probe == "unknown-new-run":
                            started = fixture.start(max_rounds=1)
                            args = fixture.generate_arguments(started["run_id"], seed=4101, max_rounds=1)
                            args["plan"]["parameters"]["seed"] = 4101
                        else:
                            raise ValueError(probe)
                        write_private_json(capture, "scope-request.json", args)
                        try:
                            value = EngineDispatch(root, {}).call("local_gpu_generate_round", args)
                            calls.append({"reported_state": "resolved" if value["state"] == "generated" else "unresolved",
                                          "generation_rpc_entered": True})
                        except caller.ProductClientError as error:
                            calls.append({"client_error_code": error.stable_code, "client_error_stage": "generate_round",
                                          "generation_rpc_entered": True, "reported_state": "unresolved"})
                        snapshots.append(oracle.snapshot())
                    schedule_reason = "scope_probe"

            session = json.loads((capture / "client/session.json").read_text())
            original = fixture.engine.get_run({"run_id": session["run_id"]})
            write_private_json(capture, "original-run-final.json", original)
            write_private_json(capture, "proxy-receipts.json", proxy.evidence())
            write_private_json(capture, "worker-snapshots.json", snapshots)
            write_private_json(capture, "worker-artifacts.json", worker_artifacts)
            write_private_json(capture, "actual-generation-arguments.json", generated_arguments)
            metrics = prompt_metrics(proxy.evidence(), proxy.stages)
            bound = lifecycle_count(snapshots)
            for artifact in worker_artifacts:
                actual = (capture / artifact["retained_file"]).read_bytes()
                if sha256(actual).hexdigest() != artifact["sha256"] or len(actual) != artifact["bytes"]:
                    raise AssertionError("retained artifact bytes differ from worker output")
            digests = [semantic_digest(a) for a in generated_arguments]
            result = {"protocol": PROTOCOL, "evidence_class": "synthetic_cpu_public_engine_dispatch",
                      "strategy": strategy, "product_revision": PRODUCTS["B2" if strategy == "P-stop" else strategy],
                      "fault": fault, "scope_probe": probe, "schedule_reason": schedule_reason,
                      "calls": calls, "original_run_state": original["state"],
                      "client_completion": original["state"] == "generated",
                      "metrics": {**metrics, "E_bound_cpu": bound}, "semantic_digests": digests,
                      "generation_call_count": len(generated_arguments), "worker_request_count": len(backend_requests),
                      "worker_artifacts": worker_artifacts,
                      "retained_artifact_bytes_revalidated": True,
                      "fpre_first_not_sent": (fault == "FPRE" and any(s["stage"] == "fault_injected_before_upstream"
                          and s["request_sequence"] == 1 for s in proxy.stages)
                          and not any(s["stage"] == "upstream_send_started" and s["request_sequence"] == 1 for s in proxy.stages)),
                      "product_manifest_writes_by_research": False,
                      "imported_product_file_sha256": imported_product_files,
                      "mcp_stdio_exercised": False, "gpu_exercised": False}
            if probe != "unknown-new-run" and len(set(digests)) != 1:
                raise AssertionError("generation semantics differ within operation")
            write_private_json(capture, "result.json", result)
            return result
    finally:
        fixture.tearDown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-root", type=Path, required=True)
    parser.add_argument("--strategy", choices=["B2", "W3", "P-stop"], required=True)
    parser.add_argument("--fault", choices=["F00", "F02", "FPRE"], required=True)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--probe", choices=["healthy-replay", "unknown-new-key", "unknown-new-run"])
    args = parser.parse_args()
    print(json.dumps(run(args.product_root, args.strategy, args.fault, args.capture, args.probe), sort_keys=True))


if __name__ == "__main__":
    main()
