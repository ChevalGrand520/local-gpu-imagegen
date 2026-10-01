"""Research-only MCP product caller for the bounded Windows F02 campaign.

Each invocation owns one fresh MCP stdio process. The default caller performs
discovery -> route -> start -> read -> generate. The opt-in same-run mode
reuses privately captured generation arguments for its second invocation.
Neither mode automatically retries within an invocation, starts a backend,
finalizes a run, or performs visual review.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


MODEL_ID = "local:79ab0d76d73036128e376c4c"
BACKEND_MODEL_ID = "sd_xl_base_1.0.safetensors"
MODEL_SHA256 = "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"
MODEL_IDENTITY_TOKEN = "model:98abab88231b757090f23f0930c1df9e32b98e3df5f7c711abed99c85a689d82"
WORKFLOW_SHA256 = "05f942291676182d08446b8855d6353a96e10fa3b059703a9f6d41e16d36000e"
COMPONENT_BUNDLE_SHA256 = "51499905db860367af4ad6fd8685abf2a08ae90566efe400c7a883fdb0b663df"
VALIDATOR_VERSION = "product-validate-v1"
PROFILE = "standalone-illustration"
SUBTYPE = "environment"
INTENT = (
    "A solitary white lighthouse on a black basalt sea stack at blue hour, "
    "complete structure visible, no people or lettering."
)
POSITIVE_PROMPT = INTENT
NEGATIVE_PROMPT = "people, text, watermark, cropped lighthouse, duplicate tower"
WIDTH = 1024
HEIGHT = 1024
CONSTRAINTS = {
    "width": WIDTH,
    "height": HEIGHT,
}
INPUT_DIGEST = hashlib.sha256(b"no-input").hexdigest()
ROUTE_VRAM_CEILING_GB = 12.0
_STABLE_ERROR_CODE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class ProductClientError(RuntimeError):
    @property
    def stable_code(self) -> str:
        candidate = str(self).split(":", 1)[0]
        return candidate if _STABLE_ERROR_CODE.fullmatch(candidate) else "product_client_error"


def _safe_exception_code(error: BaseException) -> str:
    if isinstance(error, ProductClientError):
        return error.stable_code
    if isinstance(error, json.JSONDecodeError):
        return "invalid_json"
    if isinstance(error, OSError):
        code = f"oserror_{type(error).__name__}"
        return code if _STABLE_ERROR_CODE.fullmatch(code) else "oserror"
    code = f"unexpected_{type(error).__name__}"
    return code if _STABLE_ERROR_CODE.fullmatch(code) else "unexpected_error"


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _structured(response: dict[str, Any]) -> dict[str, Any]:
    if "error" in response:
        raise ProductClientError("jsonrpc_error")
    result = response.get("result")
    if not isinstance(result, dict):
        raise ProductClientError("missing_result")
    if result.get("isError"):
        structured = result.get("structuredContent")
        error = structured.get("error") if isinstance(structured, dict) else None
        code = error.get("code") if isinstance(error, dict) else None
        if not isinstance(code, str) or not _STABLE_ERROR_CODE.fullmatch(code):
            code = "tool_error"
        raise ProductClientError(code)
    value = result.get("structuredContent")
    if isinstance(value, dict):
        return value
    for block in result.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            try:
                parsed = json.loads(str(block.get("text", "")))
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    raise ProductClientError("missing_structured_content")


class StdioMcp:
    def __init__(self, root: Path, env: dict[str, str]) -> None:
        self.root = root
        server = root / "scripts" / "mcp_server.py"
        if not server.is_file():
            raise ProductClientError(f"missing_server:{server}")
        launcher = Path(__file__).with_name("f02_transport_launcher.py")
        command = (
            [sys.executable, str(launcher), str(server)]
            if env.get("LOCAL_GPU_IMAGEGEN_RESEARCH_PROMPT_PROXY_URL")
            else [sys.executable, str(server)]
        )
        self.process = subprocess.Popen(
            command,
            cwd=root,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.sequence = 0

    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.process.stdin is None or self.process.stdout is None:
            raise ProductClientError("stdio_not_open")
        self.sequence += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.sequence,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        self.process.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
        self.process.stdin.flush()
        while True:
            line = self.process.stdout.readline()
            if not line:
                raise ProductClientError("server_eof")
            response = json.loads(line)
            if response.get("id") == self.sequence:
                return _structured(response)

    def close(self) -> None:
        if self.process.stdin is not None:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)


def _initialise(client: StdioMcp) -> None:
    # The server accepts an empty initialize parameter object, matching the
    # repository's verify_mcp.py transport check.
    client.sequence += 1
    assert client.process.stdin is not None and client.process.stdout is not None
    request = {"jsonrpc": "2.0", "id": client.sequence, "method": "initialize", "params": {}}
    client.process.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
    client.process.stdin.flush()
    while True:
        line = client.process.stdout.readline()
        if not line:
            raise ProductClientError("initialize_eof")
        response = json.loads(line)
        if response.get("id") == client.sequence:
            if "error" in response:
                raise ProductClientError(f"initialize_error:{response['error']}")
            return


def _discover_route(client: StdioMcp) -> dict[str, Any]:
    model_path_text = os.environ.get("LOCAL_GPU_IMAGEGEN_RESEARCH_MODEL_PATH")
    if not model_path_text:
        raise ProductClientError("pinned_model_path_missing")
    model_path = Path(model_path_text)
    planned = client.call(
        "local_gpu_discover_models",
        {"phase": "plan", "mode": "api_only", "stage": "index", "backends": ["comfyui"]},
    )
    execute = {
        "phase": "execute",
        "mode": "api_only",
        "stage": "index",
        "backends": ["comfyui"],
        "plan_id": planned["plan_id"],
    }
    for field in ("confirmation", "network_confirmation"):
        if planned.get(field):
            execute[field] = planned[field]
    discovered = client.call("local_gpu_discover_models", execute)
    candidates = discovered.get("candidates")
    if not isinstance(candidates, list):
        raise ProductClientError("discovery_candidates_missing")
    candidate = next(
        (
            item for item in candidates
            if isinstance(item, dict) and item.get("backend_model_id") == BACKEND_MODEL_ID
        ),
        None,
    )
    if not isinstance(candidate, dict):
        raise ProductClientError("pinned_model_not_found")
    metadata = candidate.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("loader_class") != "CheckpointLoaderSimple" or metadata.get("loader_input") != "ckpt_name":
        raise ProductClientError("pinned_backend_loader_drifted")

    # Fresh MCP processes do not retain the portable ComfyUI checkpoint in the
    # default scan roots, so re-index and fingerprint only the exact pinned
    # file before resolving its already-approved private catalog record.
    if not model_path.is_file() or model_path.name != BACKEND_MODEL_ID:
        raise ProductClientError("pinned_checkpoint_missing")
    model_root = str(model_path.parent)
    index_plan = client.call(
        "local_gpu_discover_models",
        {
            "phase": "plan",
            "mode": "selected_folders",
            "stage": "index",
            "roots": [model_root],
            "explicit_includes": [str(model_path)],
        },
    )
    index_arguments = {
        "phase": "execute",
        "mode": "selected_folders",
        "stage": "index",
        "roots": [model_root],
        "explicit_includes": [str(model_path)],
        "plan_id": index_plan["plan_id"],
    }
    if index_plan.get("confirmation"):
        index_arguments["confirmation"] = index_plan["confirmation"]
    indexed = client.call("local_gpu_discover_models", index_arguments)
    indexed_candidates = indexed.get("candidates")
    if not isinstance(indexed_candidates, list):
        raise ProductClientError("filesystem_candidates_missing")
    file_candidates = [
        item for item in indexed_candidates
        if isinstance(item, dict) and item.get("filename") == BACKEND_MODEL_ID
    ]
    if len(file_candidates) != 1 or not isinstance(file_candidates[0].get("candidate_id"), str):
        raise ProductClientError("pinned_filesystem_candidate_not_unique")
    fingerprint_plan = client.call(
        "local_gpu_discover_models",
        {
            "phase": "plan",
            "mode": "selected_folders",
            "stage": "fingerprint",
            "roots": [model_root],
            "selected_candidates": [file_candidates[0]["candidate_id"]],
        },
    )
    fingerprint_arguments = {
        "phase": "execute",
        "mode": "selected_folders",
        "stage": "fingerprint",
        "roots": [model_root],
        "selected_candidates": [file_candidates[0]["candidate_id"]],
        "plan_id": fingerprint_plan["plan_id"],
    }
    if fingerprint_plan.get("confirmation"):
        fingerprint_arguments["confirmation"] = fingerprint_plan["confirmation"]
    fingerprinted = client.call("local_gpu_discover_models", fingerprint_arguments)
    fingerprint_candidates = fingerprinted.get("candidates")
    if not isinstance(fingerprint_candidates, list):
        raise ProductClientError("fingerprint_candidates_missing")
    fingerprints = [
        item for item in fingerprint_candidates
        if isinstance(item, dict) and item.get("filename") == BACKEND_MODEL_ID
    ]
    if len(fingerprints) != 1:
        raise ProductClientError("pinned_fingerprint_not_unique")
    fingerprint = fingerprints[0]
    if fingerprint.get("sha256") != MODEL_SHA256 or fingerprint.get("identity_token") != MODEL_IDENTITY_TOKEN:
        raise ProductClientError("pinned_model_identity_drifted")

    private_catalog = client.call("local_gpu_list_profiles", {"authorization_scope": "private"})
    models = private_catalog.get("models")
    model = models.get(MODEL_ID) if isinstance(models, dict) else None
    bundle = model.get("component_bundle") if isinstance(model, dict) else None
    workflow = bundle.get("workflow") if isinstance(bundle, dict) else None
    if (
        not isinstance(model, dict)
        or model.get("backend") != "comfyui"
        or model.get("backend_model_id") != BACKEND_MODEL_ID
        or model.get("endpoint_identity") != candidate.get("endpoint_identity")
        or model.get("sha256") != MODEL_SHA256
        or model.get("trust_identity_token") != MODEL_IDENTITY_TOKEN
        or model.get("component_bundle_sha256") != COMPONENT_BUNDLE_SHA256
        or model.get("workflow_template_id") != "sdxl-txt2img"
        or not isinstance(bundle, dict)
        or bundle.get("bundle_sha256") != model.get("component_bundle_sha256")
        or not isinstance(workflow, dict)
        or workflow.get("sha256") != WORKFLOW_SHA256
        or workflow.get("template_id") != "sdxl-txt2img"
        or workflow.get("template_version") != 1
    ):
        raise ProductClientError("approved_private_catalog_entry_mismatch")

    recommendation = client.call(
        "local_gpu_recommend_models",
        {
            "authorization_scope": "private",
            "operation": "txt2img",
            "profile": PROFILE,
            "style": None,
            "width": WIDTH,
            "height": HEIGHT,
            "affinity_tags": [],
            "required_vram_gb": ROUTE_VRAM_CEILING_GB,
            "preferred_model_id": MODEL_ID,
        },
    )
    routes = recommendation.get("routes")
    if not isinstance(routes, list) or not routes:
        raise ProductClientError("recommendation_route_missing")
    route = routes[0]
    if not isinstance(route, dict) or not isinstance(route.get("start_run_boundary"), dict):
        raise ProductClientError("start_run_boundary_missing")
    boundary = route["start_run_boundary"]
    if (
        boundary.get("backend") != "comfyui"
        or boundary.get("model_choice") != MODEL_ID
        or boundary.get("authorization_scope") != "private"
    ):
        raise ProductClientError("recommended_route_drifted")
    return {
        "candidate": candidate,
        "filesystem_identity": fingerprint,
        "private_model": model,
        "recommendation": recommendation,
        "boundary": boundary,
    }


def _build_plan(request: dict[str, Any], seed: int) -> dict[str, Any]:
    route = request["route"]
    plan = {
        "profile": request["profile"],
        "style": request["style"],
        "intent": request["intent"],
        "positive_prompt": POSITIVE_PROMPT,
        "negative_prompt": NEGATIVE_PROMPT,
        "constraints": dict(request["constraints"]),
        "parameters": {
            "mode": "txt2img",
            "width": WIDTH,
            "height": HEIGHT,
            "steps": 30,
            "guidance_scale": 7.0,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "seed": seed,
        },
        "max_rounds": request["max_rounds"],
        "upscale_policy": request["upscale_policy"],
    }
    for field in (
        "authorization_scope", "route_token", "model_choice", "backend",
        "endpoint_identity", "model_identity_token", "identity_strength",
        "workflow_template_id", "workflow_template_version",
        "prompt_compiler_id", "prompt_compiler_version",
    ):
        plan[field] = request.get(field, route.get(field))
    return plan


def _request_digests(request: dict[str, Any], plan: dict[str, Any], route: dict[str, Any]) -> dict[str, str]:
    canonical_request = {
        "intent": request["intent"],
        "profile": request["profile"],
        "subtype": request.get("subtype"),
        "style": request["style"],
        "constraints": request["constraints"],
        "max_rounds": request["max_rounds"],
        "upscale_policy": request["upscale_policy"],
        "model_choice": request["model_choice"],
        "backend": request["backend"],
        "authorization_scope": request["authorization_scope"],
        "route_token": request["route_token"],
    }
    return {
        "canonical_request_digest": _digest(canonical_request),
        "compiled_prompt_digest": _digest({"positive_prompt": POSITIVE_PROMPT, "negative_prompt": NEGATIVE_PROMPT}),
        "workflow_graph_digest": str(route.get("workflow_sha256") or WORKFLOW_SHA256),
        "input_digest": INPUT_DIGEST,
        "route_identity": str(request.get("route_token") or route.get("route_token")),
        "validator_version": VALIDATOR_VERSION,
    }


def probe(root: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("LOCAL_GPU_IMAGEGEN_COMFYUI_URL", "http://127.0.0.1:8202")
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_MANAGED"] = "0"
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_STARTUP_WAIT_SECONDS"] = "0"
    client = StdioMcp(root, env)
    try:
        _initialise(client)
        route_info = _discover_route(client)
        profiles = client.call("local_gpu_list_profiles", {"authorization_scope": "private"})
        boundary = route_info["boundary"]
        pseudo_request = {
            "intent": INTENT,
            "profile": boundary["profile"],
            "subtype": SUBTYPE,
            "style": boundary.get("style"),
            "constraints": dict(CONSTRAINTS),
            "max_rounds": 1,
            "upscale_policy": "off",
            "model_choice": boundary["model_choice"],
            "backend": boundary["backend"],
            "authorization_scope": boundary["authorization_scope"],
            "route_token": boundary["route_token"],
            "route": boundary,
        }
        plan = _build_plan(pseudo_request, 4101)
        return {
            "route": boundary,
            "digests": _request_digests(pseudo_request, plan, boundary),
            "catalog_models": profiles.get("models"),
            "model_id": MODEL_ID,
            "model_sha256": MODEL_SHA256,
            "workflow_sha256": WORKFLOW_SHA256,
        }
    finally:
        client.close()


def catalog(root: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("LOCAL_GPU_IMAGEGEN_COMFYUI_URL", "http://127.0.0.1:8202")
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_MANAGED"] = "0"
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_STARTUP_WAIT_SECONDS"] = "0"
    client = StdioMcp(root, env)
    try:
        _initialise(client)
        private = client.call("local_gpu_list_profiles", {"authorization_scope": "private"})
        public = client.call("local_gpu_list_profiles", {"authorization_scope": "public_evidence"})
        return {
            "private_models": private.get("models"),
            "public_models": public.get("models"),
        }
    finally:
        client.close()


def _artifact_hashes(result: dict[str, Any], root: Path) -> list[str]:
    paths: list[str] = []
    full_path = result.get("full_image_path")
    if isinstance(full_path, str):
        paths.append(full_path)
    round_value = result.get("round")
    if isinstance(round_value, dict):
        image = round_value.get("image")
        if isinstance(image, dict) and isinstance(image.get("path"), str):
            paths.append(image["path"])
    hashes: list[str] = []
    for value in paths:
        path = Path(value)
        if not path.is_absolute():
            path = root / value
        digest = _file_sha256(path)
        if digest is not None and digest not in hashes:
            hashes.append(digest)
    return hashes


def run(root: Path, *, case_id: str, operation_key: str, output_root: str, call_index: int) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("LOCAL_GPU_IMAGEGEN_COMFYUI_URL", "http://127.0.0.1:8202")
    env["LOCAL_GPU_IMAGEGEN_OUTPUT_DIR"] = output_root
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_MANAGED"] = "0"
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_STARTUP_WAIT_SECONDS"] = "0"
    client = StdioMcp(root, env)
    stage = "initialize"
    try:
        _initialise(client)
        stage = "private_catalog"
        client.call("local_gpu_list_profiles", {"authorization_scope": "private"})
        stage = "model_route"
        route_info = _discover_route(client)
        boundary = route_info["boundary"]
        start_arguments = {
            "intent": INTENT,
            "profile": boundary["profile"],
            "subtype": SUBTYPE,
            "style": boundary.get("style"),
            "constraints": dict(CONSTRAINTS),
            "model_choice": boundary["model_choice"],
            "backend": boundary["backend"],
            "authorization_scope": boundary["authorization_scope"],
            "route_token": boundary["route_token"],
            "max_rounds": 1,
            "upscale_policy": "off",
        }
        stage = "start_run"
        started = client.call("local_gpu_start_run", start_arguments)
        run_id = started.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ProductClientError("run_id_missing")
        stage = "read_run"
        manifest = client.call("local_gpu_get_run", {"run_id": run_id})
        seed = 4100 + call_index
        plan = _build_plan(manifest["request"], seed)
        stage = "generate_round"
        generated = client.call(
            "local_gpu_generate_round",
            {
                "run_id": run_id,
                "idempotency_key": operation_key,
                "action": "initial",
                "edit_mode": "txt2img",
                "plan": plan,
                "seed": seed,
                "change_summary": f"Bounded F02 research case {case_id}, call {call_index}.",
            },
        )
        route = manifest["request"]["route"]
        digests = _request_digests(manifest["request"], plan, route)
        artifact_hashes = _artifact_hashes(generated, root)
        stage = "artifact_validation"
        if not artifact_hashes:
            raise ProductClientError("artifact_hash_missing")
        return {
            **digests,
            "operation_key": operation_key,
            "reported_state": "resolved" if generated.get("state") == "generated" else "unresolved",
            "artifact_hashes": artifact_hashes,
            "run_id_sha256": hashlib.sha256(run_id.encode("utf-8")).hexdigest(),
            "case_id": case_id,
            "call_index": call_index,
            "backend_model_id": BACKEND_MODEL_ID,
            "workflow_template_id": route.get("workflow_template_id"),
        }
    except ProductClientError as exc:
        # A response-loss error after the backend has accepted /prompt is an
        # unresolved product result; the independent proxy/oracle decides
        # whether execution occurred.  The controller never treats this as a
        # backend execution failure by itself.
        return {
            "operation_key": operation_key,
            "reported_state": "unresolved",
            "artifact_hashes": [],
            "client_error_schema_version": 1,
            "client_error_code": exc.stable_code,
            "client_error_stage": stage,
            "case_id": case_id,
            "call_index": call_index,
        }
    finally:
        client.close()


def run_same_run(
    root: Path, *, case_id: str, operation_key: str, output_root: str,
    call_index: int, capture_root: Path,
) -> dict[str, Any]:
    """One invocation of an explicit, privately captured same-run protocol.

    Call 1 freezes the complete generation arguments before submission. Call 2
    reuses them verbatim and refuses to proceed unless the original manifest
    still contains the matching unknown/no-job unresolved attempt.
    """
    from scripts.research.f02_capture import manifest_summary, unknown_submission, write_private_json

    if call_index not in (1, 2):
        raise ProductClientError("same_run_call_index_invalid")
    env = os.environ.copy()
    env.setdefault("LOCAL_GPU_IMAGEGEN_COMFYUI_URL", "http://127.0.0.1:8202")
    env["LOCAL_GPU_IMAGEGEN_OUTPUT_DIR"] = output_root
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_MANAGED"] = "0"
    env["LOCAL_GPU_IMAGEGEN_COMFYUI_STARTUP_WAIT_SECONDS"] = "0"
    context = {
        "case_id": case_id, "operation_key": operation_key, "output_root": output_root,
        "product_root": str(root.resolve()),
        "backend_url": env["LOCAL_GPU_IMAGEGEN_COMFYUI_URL"],
        "proxy_url": env.get("LOCAL_GPU_IMAGEGEN_RESEARCH_PROMPT_PROXY_URL"),
    }
    session: dict[str, Any] = {}
    if call_index == 1:
        capture_root.mkdir(mode=0o700)  # Existing captures cannot be reused accidentally.
    else:
        session = json.loads((capture_root / "session.json").read_text(encoding="utf-8"))
        if not isinstance(session, dict) or not isinstance(session.get("request_digests"), dict):
            raise ProductClientError("same_run_session_shape_invalid")
        if session.get("context") != context or session.get("schema") != "f02-same-run-session-v1":
            raise ProductClientError("same_run_session_context_mismatch")
        if session.get("generate_arguments_sha256") != _digest(session.get("generate_arguments")):
            raise ProductClientError("same_run_arguments_digest_mismatch")
        arguments = session.get("generate_arguments")
        if (not isinstance(arguments, dict) or arguments.get("run_id") != session.get("run_id")
                or arguments.get("idempotency_key") != operation_key):
            raise ProductClientError("same_run_arguments_identity_mismatch")
        first_result = json.loads((capture_root / "call-1-result.json").read_text(encoding="utf-8"))
        if (not isinstance(first_result, dict)
                or first_result.get("generate_arguments_sha256") != session.get("generate_arguments_sha256")
                or first_result.get("run_id_sha256") != hashlib.sha256(str(session.get("run_id")).encode()).hexdigest()):
            raise ProductClientError("same_run_session_changed_since_first_call")
    # Claim this invocation before opening a product process; never replay it.
    write_private_json(capture_root, f"call-{call_index}-invocation.json", {"context": context, "call_index": call_index})
    client = StdioMcp(root, env)
    stage = "initialize"
    run_id: str | None = None
    result: dict[str, Any] = {"case_id": case_id, "call_index": call_index,
                              "retry_scope": "same_run", "operation_key": operation_key,
                              "artifact_hashes": []}
    try:
        _initialise(client)
        if call_index == 1:
            stage = "model_route"
            boundary = _discover_route(client)["boundary"]
            stage = "start_run"
            started = client.call("local_gpu_start_run", {
                "intent": INTENT, "profile": boundary["profile"], "subtype": SUBTYPE,
                "style": boundary.get("style"), "constraints": dict(CONSTRAINTS),
                "model_choice": boundary["model_choice"], "backend": boundary["backend"],
                "authorization_scope": boundary["authorization_scope"],
                "route_token": boundary["route_token"], "max_rounds": 1, "upscale_policy": "off",
            })
            run_id = started.get("run_id")
        else:
            run_id = session.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ProductClientError("run_id_missing")
        result["run_id_sha256"] = hashlib.sha256(run_id.encode("utf-8")).hexdigest()
        stage = "read_run"
        manifest = client.call("local_gpu_get_run", {"run_id": run_id})
        result["manifest_before_sha256"] = write_private_json(capture_root, f"call-{call_index}-before.json", manifest)
        if manifest.get("run_id") != run_id:
            raise ProductClientError("same_run_manifest_identity_mismatch")
        if not isinstance(manifest.get("request"), dict):
            raise ProductClientError("same_run_manifest_request_missing")
        if call_index == 1:
            seed = 4101
            plan = _build_plan(manifest["request"], seed)
            arguments = {
                "run_id": run_id, "idempotency_key": operation_key,
                "action": "initial", "edit_mode": "txt2img", "plan": plan, "seed": seed,
                "change_summary": f"Bounded same-run F02 research case {case_id}.",
            }
            session = {
                "schema": "f02-same-run-session-v1", "context": context, "run_id": run_id,
                "request_sha256": _digest(manifest["request"]), "generate_arguments": arguments,
                "generate_arguments_sha256": _digest(arguments),
                "request_digests": _request_digests(manifest["request"], plan, manifest["request"]["route"]),
            }
            write_private_json(capture_root, "session.json", session)
        result.update(session["request_digests"])
        result["generate_arguments_sha256"] = session["generate_arguments_sha256"]
        if call_index == 2:
            if _digest(manifest.get("request")) != session["request_sha256"]:
                raise ProductClientError("same_run_request_changed")
            if not unknown_submission(manifest, operation_key):
                raise ProductClientError("same_run_unknown_submission_missing")
        stage = "generate_round"
        generated = client.call("local_gpu_generate_round", session["generate_arguments"])
        stage = "artifact_validation"
        hashes = _artifact_hashes(generated, root)
        if not hashes:
            raise ProductClientError("artifact_hash_missing")
        result.update({"reported_state": "resolved" if generated.get("state") == "generated" else "unresolved",
                       "artifact_hashes": hashes})
    except ProductClientError as exc:
        result.update({"reported_state": "unresolved", "client_error_schema_version": 1,
                       "client_error_code": exc.stable_code, "client_error_stage": stage})
    finally:
        try:
            if run_id is not None:
                after = client.call("local_gpu_get_run", {"run_id": run_id})
                result["manifest_after_sha256"] = write_private_json(capture_root, f"call-{call_index}-after.json", after)
                result.update(manifest_summary(after))
        except (ProductClientError, OSError) as exc:
            result["capture_error_code"] = _safe_exception_code(exc)
        finally:
            client.close()
    write_private_json(capture_root, f"call-{call_index}-result.json", result)
    return result


def main() -> int:
    probe_argument = len(sys.argv) > 1 and sys.argv[1] == "--probe"
    catalog_argument = len(sys.argv) > 1 and sys.argv[1] == "--catalog"
    root_argument = sys.argv[2] if (probe_argument or catalog_argument) and len(sys.argv) > 2 else os.environ.get("LOCAL_GPU_IMAGEGEN_CLIENT_ROOT")
    root = Path(root_argument or str(Path.cwd()))
    case_id = os.environ.get("LOCAL_GPU_IMAGEGEN_F02_CASE_ID", "unknown")
    operation_key = os.environ.get("LOCAL_GPU_IMAGEGEN_F02_OPERATION_KEY", "f02-fixed-request-v1")
    output_root = os.environ.get("LOCAL_GPU_IMAGEGEN_OUTPUT_ROOT", "")
    call_index = int(os.environ.get("LOCAL_GPU_IMAGEGEN_F02_CALL_INDEX", "1"))
    if probe_argument or os.environ.get("LOCAL_GPU_IMAGEGEN_F02_PROBE") == "1":
        try:
            print(json.dumps(probe(root), sort_keys=True, separators=(",", ":")))
            return 0
        except (OSError, ProductClientError, json.JSONDecodeError) as exc:
            print(json.dumps({"reported_state": "failed", "client_error_schema_version": 1, "client_error_code": _safe_exception_code(exc), "client_error_stage": "route_probe"}, sort_keys=True))
            return 2
    if catalog_argument:
        try:
            print(json.dumps(catalog(root), sort_keys=True, separators=(",", ":")))
            return 0
        except (OSError, ProductClientError, json.JSONDecodeError) as exc:
            print(json.dumps({"reported_state": "failed", "client_error_schema_version": 1, "client_error_code": _safe_exception_code(exc), "client_error_stage": "catalog_probe"}, sort_keys=True))
            return 2
    if not output_root:
        print(json.dumps({"reported_state": "failed", "client_error_schema_version": 1, "client_error_code": "output_root_missing", "client_error_stage": "launch"}, sort_keys=True))
        return 2
    scope = os.environ.get("LOCAL_GPU_IMAGEGEN_F02_RETRY_SCOPE", "fresh_run")
    if scope == "same_run":
        capture = os.environ.get("LOCAL_GPU_IMAGEGEN_F02_PRIVATE_CAPTURE_DIR")
        if not capture:
            print(json.dumps({"reported_state": "failed", "client_error_code": "private_capture_missing"}))
            return 2
        try:
            result = run_same_run(root, case_id=case_id, operation_key=operation_key,
                                  output_root=output_root, call_index=call_index, capture_root=Path(capture))
        except (ProductClientError, OSError, ValueError) as exc:
            result = {"reported_state": "failed", "client_error_schema_version": 1,
                      "client_error_code": _safe_exception_code(exc), "client_error_stage": "launch"}
    elif scope == "fresh_run":
        result = run(root, case_id=case_id, operation_key=operation_key, output_root=output_root, call_index=call_index)
    else:
        result = {"reported_state": "failed", "client_error_code": "retry_scope_invalid"}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result.get("reported_state") != "failed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
