#!/usr/bin/env python
from __future__ import annotations

import json
import math
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from local_gpu_imagegen import __version__
from local_gpu_imagegen.bootstrap_catalog import load_bootstrap_manifest
from local_gpu_imagegen.errors import AssetEngineError
from local_gpu_imagegen.model_identity import build_component_bundle, identity_token
from local_gpu_imagegen.paths import default_output_root, resolve_resource_root
from local_gpu_imagegen.postprocess import SUPPORTED_MODELS
from local_gpu_imagegen.two_stage_layout import (
    TWO_STAGE_LAYOUT_MODE,
    TWO_STAGE_TEMPLATE_ID,
    build_control_identity,
    validate_two_stage_layout,
)
from local_gpu_imagegen.workflow_templates import (
    MODEL_LOADER_INPUTS,
    workflow_component_bindings,
)
from local_gpu_imagegen.visual_review import STAGE_CHECK_NAMES


from _constants import (
    DEFAULT_COMMAND_TIMEOUT_SECONDS,
    MAX_DISCOVERY_METADATA_STRING_CHARS,
    MAX_PREVIEW_BASE64_CHARS,
    PYTHON,
    ROOT,
    SCRIPTS,
    SERVER_VERSION,
)
_asset_engine: Any | None = None
_runtime_services: Any | None = None


from _protocol import (
    command_error,
    jsonrpc_error,
    run_script,
    script_json_result,
    send,
    text_content,
    tool_error,
    tool_success,
)


def get_capabilities() -> dict[str, object]:
    code, stdout, _stderr = run_script("check_gpu.py", [])
    if code != 0:
        return {
            "ready": False,
            "backends": {},
            "warnings": ["capability_check_failed"],
        }
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "ready": False,
            "backends": {},
            "warnings": ["capability_check_invalid_json"],
        }
    if not isinstance(value, dict):
        return {
            "ready": False,
            "backends": {},
            "warnings": ["capability_check_invalid_result"],
        }
    available_backends = []
    if value.get("webui_ready") is True:
        available_backends.append("webui")
    if value.get("diffusers_ready") is True:
        available_backends.append("diffusers")
    if value.get("comfyui_ready") is True:
        available_backends.append("comfyui")
    return {**value, "available_backends": available_backends}


def bootstrap_guidance(readiness: dict[str, object]) -> dict[str, object]:
    """Describe the explicit CLI bootstrap without planning or mutating state."""
    manifest = load_bootstrap_manifest(
        ROOT / "profiles" / "bootstrap" / "windows-nvidia.json"
    )
    cuda = readiness.get("cuda") if isinstance(readiness.get("cuda"), dict) else {}
    reason_codes: list[str] = []
    architecture = platform.machine().lower()
    normalized_architecture = "amd64" if architecture in {"amd64", "x86_64"} else architecture
    windows_version = getattr(sys, "getwindowsversion", None)
    try:
        windows_build = int(windows_version().build) if callable(windows_version) else None
    except (AttributeError, TypeError, ValueError):
        windows_build = None
    if sys.platform != manifest.platform:
        support_status = "unsupported"
        reason_codes.append("unsupported_platform")
    elif normalized_architecture != manifest.architecture:
        support_status = "unsupported"
        reason_codes.append("unsupported_architecture")
    elif windows_build is None:
        support_status = "unknown"
        reason_codes.append("windows_build_unknown")
    elif windows_build < manifest.minimum_windows_build:
        support_status = "unsupported"
        reason_codes.append("unsupported_windows_build")
    elif cuda.get("available") is not True:
        support_status = "unknown"
        reason_codes.append("cuda_unavailable")
    else:
        support_status = "supported"
    if readiness.get("comfyui_ready") is not True:
        reason_codes.append("comfyui_not_ready")
    if readiness.get("webui_ready") is not True:
        reason_codes.append("webui_not_ready")
    if readiness.get("diffusers_ready") is not True:
        reason_codes.append("diffusers_not_ready")
    return {
        "support_status": support_status,
        "reason_codes": reason_codes,
        "estimated_download_bytes": manifest.required_download_bytes,
        "estimated_disk_bytes": manifest.minimum_free_disk_bytes,
        "next_action": "local-gpu-imagegen bootstrap plan --client codex",
    }


def _diffusers_runner(request: dict[str, object]) -> dict[str, object]:
    model = request.get("model")
    if not isinstance(model, dict):
        raise AssetEngineError("invalid_backend_request", "Diffusers model identity is missing.", "validation")
    args = [
        "--prompt", str(request["positive_prompt"]),
        "--negative-prompt", str(request["negative_prompt"]),
        "--backend", "diffusers",
        "--mode", str(request["mode"]),
        "--model", str(model["backend_model_id"]),
        "--width", str(request["width"]),
        "--height", str(request["height"]),
        "--steps", str(request["steps"]),
        "--guidance-scale", str(request["guidance_scale"]),
        "--seed", str(request["seed"]),
        "--output-dir", str(Path(str(request["output_path"])).parent),
        "--filename", Path(str(request["output_path"])).name,
    ]
    for field, flag in (
        ("source_path", "--input-image"),
        ("mask_path", "--mask-image"),
        ("strength", "--strength"),
    ):
        if request.get(field) is not None:
            args.extend((flag, str(request[field])))
    code, stdout, stderr = run_script("generate_image.py", args)
    if code != 0:
        raise AssetEngineError(
            "backend_command_failed",
            "Diffusers compatibility backend failed.",
            "backend",
            {"exit_code": code, "stderr": stderr},
        )
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise AssetEngineError(
            "invalid_backend_result",
            "Diffusers compatibility backend returned invalid JSON.",
            "artifact",
        ) from error
    if not isinstance(value, dict):
        raise AssetEngineError("invalid_backend_result", "Diffusers result must be an object.", "artifact")
    return {
        **value,
        "backend": "diffusers",
        "model": model["backend_model_id"],
        "endpoint_identity": model["endpoint_identity"],
        "model_identity_token": model["identity_token"],
        "identity_strength": model["identity_strength"],
        "workflow_template_id": None,
        "workflow_template_version": None,
        "prompt_compiler_id": request["prompt_compiler_id"],
        "prompt_compiler_version": request["prompt_compiler_version"],
    }


def get_runtime_services() -> Any:
    global _asset_engine, _runtime_services
    if _runtime_services is None:
        from local_gpu_imagegen.services import build_services
        from local_gpu_imagegen.trust_registry import default_state_dir

        _runtime_services = build_services(
            ROOT,
            Path(os.environ.get("LOCAL_GPU_IMAGEGEN_OUTPUT_DIR", default_output_root(ROOT))),
            default_state_dir(),
            get_capabilities,
            _diffusers_runner,
        )
        _asset_engine = _runtime_services.engine
    return _runtime_services


def get_asset_engine() -> Any:
    return get_runtime_services().engine


# Re-exported so existing callers (and the test suite) keep their module-level
# access to schema and validation helpers after the decomposition.
from _schema import (
    _approved_model_ids,
    _object_schema,
    _output_schema,
    _registered_profile_ids,
    _registered_style_ids,
    _registered_subtype_ids,
    _shipped_workflow_template_ids,
    _workflow_template_is_public,
    tool_schema,
)
from _validation import (
    _validate_nested_object,
    schema_type_matches,
    validate_tool_arguments,
)


def _successful_engine_data(value: dict[str, Any]) -> dict[str, Any]:
    data = dict(value)
    data.setdefault("ok", True)
    warnings = data.get("warnings")
    if not isinstance(warnings, list):
        data["warnings"] = []
    return data


def _bounded_discovery_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _bounded_discovery_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_bounded_discovery_value(item) for item in value]
    if isinstance(value, str):
        if value.lstrip().lower().startswith("data:"):
            return f"[omitted data URI; original_chars={len(value)}]"
        if len(value) > MAX_DISCOVERY_METADATA_STRING_CHARS:
            return f"[omitted oversized string; original_chars={len(value)}]"
    return value


def _bounded_discovery_data(value: dict[str, Any]) -> dict[str, Any]:
    return _bounded_discovery_value(value)


def _preview_block(preview: object) -> dict[str, str] | None:
    data = getattr(preview, "data_base64", None)
    mime_type = getattr(preview, "mime_type", None)
    if (
        isinstance(data, str)
        and data
        and len(data) <= MAX_PREVIEW_BASE64_CHARS
        and mime_type == "image/jpeg"
    ):
        return {"data": data, "mimeType": "image/jpeg"}
    return None


def _asset_error(error: AssetEngineError) -> dict[str, Any]:
    result = tool_error(error.code, error.category, str(error.args[0]), dict(error.details))
    result["structuredContent"]["error"]["details"] = dict(error.details)
    return result


def _discovery_call(services: Any, arguments: dict[str, Any]) -> dict[str, object]:
    if arguments["phase"] == "plan":
        request = {
            field: arguments[field]
            for field in (
                "mode", "stage", "backends", "roots", "explicit_includes", "selected_candidates",
                "expected_backend_model_id", "authorization_id",
            )
            if field in arguments
        }
        return services.discovery.plan(request)
    return services.discovery.execute(
        arguments["plan_id"],
        arguments.get("confirmation"),
        network_confirmation=arguments.get("network_confirmation"),
    )


def _inventory_identity(services: Any, token: str) -> dict[str, object]:
    matches = []
    for record in services.discovery.inventory():
        if not isinstance(record, dict):
            continue
        try:
            current_token = identity_token(record)
        except AssetEngineError:
            continue
        if current_token == token:
            matches.append(record)
    if len(matches) != 1:
        raise AssetEngineError(
            "model_identity_not_current",
            "Trust changes require one exact identity from the current inventory.",
            "validation",
        )
    return matches[0]


def _workflow_component_bundle(
    services: Any,
    record: dict[str, object],
    graph: object,
    registration: dict[str, object],
    component_identity_tokens: list[str],
) -> tuple[dict[str, object], dict[str, object]]:
    if record.get("backend") != "filesystem" or record.get("identity_strength") != "cryptographic":
        raise AssetEngineError(
            "component_primary_identity_required",
            "Component binding requires the primary cryptographic filesystem identity.",
            "validation",
        )
    if (
        not isinstance(component_identity_tokens, list)
        or not component_identity_tokens
        or len(set(component_identity_tokens)) != len(component_identity_tokens)
    ):
        raise AssetEngineError(
            "invalid_component_bundle",
            "Selected component identity tokens must be a non-empty unique array.",
            "validation",
        )
    inventory = services.discovery.inventory()
    selected = [_inventory_identity(services, token) for token in component_identity_tokens]
    if any(
        item.get("backend") != "filesystem"
        or item.get("identity_strength") != "cryptographic"
        or not isinstance(item.get("sha256"), str)
        or type(item.get("byte_size")) is not int
        for item in selected
    ):
        raise AssetEngineError(
            "invalid_component_bundle",
            "Every selected workflow component must be a cryptographic filesystem identity.",
            "validation",
        )
    bindings = workflow_component_bindings(graph)
    if len(bindings) != len(selected):
        raise AssetEngineError(
            "invalid_component_bundle",
            "Selected component count does not match the reviewed workflow.",
            "validation",
        )
    components: list[dict[str, object]] = []
    primary_api: dict[str, object] | None = None
    endpoint: str | None = None
    for binding in bindings:
        filesystem_matches = [
            item
            for item in selected
            if _filesystem_component_name_matches(
                str(item.get("backend_model_id", "")),
                binding["backend_model_id"],
            )
        ]
        if len(filesystem_matches) != 1:
            raise AssetEngineError(
                "workflow_component_binding_ambiguous",
                "Each workflow loader must match one selected filesystem identity.",
                "validation",
            )
        filesystem = filesystem_matches[0]
        api_matches = [
            item
            for item in inventory
            if isinstance(item, dict)
            and item.get("backend") == "comfyui"
            and item.get("backend_model_id") == binding["backend_model_id"]
            and isinstance(item.get("metadata"), dict)
            and item["metadata"].get("loader_class") == binding["loader_class"]
            and item["metadata"].get("loader_input") == binding["loader_input"]
        ]
        if len(api_matches) != 1:
            raise AssetEngineError(
                "workflow_component_binding_ambiguous",
                "Each workflow loader must match one exact current ComfyUI identity.",
                "validation",
            )
        api = api_matches[0]
        if endpoint is None:
            endpoint = str(api["endpoint_identity"])
        elif api.get("endpoint_identity") != endpoint:
            raise AssetEngineError(
                "workflow_component_endpoint_mismatch",
                "Workflow components must belong to one ComfyUI endpoint.",
                "validation",
            )
        filesystem_token = identity_token(filesystem)
        if binding["role"] == "primary_model":
            if filesystem_token != identity_token(record):
                raise AssetEngineError(
                    "component_primary_identity_mismatch",
                    "The trust identity must be the selected primary workflow component.",
                    "validation",
                )
            primary_api = api
        components.append({
            **binding,
            "filesystem_identity_token": filesystem_token,
            "sha256": filesystem["sha256"],
            "byte_size": filesystem["byte_size"],
        })
    if primary_api is None:
        raise AssetEngineError(
            "invalid_component_bundle",
            "Reviewed workflow does not expose one primary component.",
            "validation",
        )
    bundle = build_component_bundle(
        components,
        {
            "template_id": registration["template_id"],
            "template_version": registration["template_version"],
            "sha256": registration["workflow_sha256"],
        },
    )
    return primary_api, bundle


def _filesystem_component_name_matches(candidate: str, backend_name: str) -> bool:
    normalized_candidate = candidate.replace("\\", "/").strip("/").casefold()
    normalized_backend = backend_name.replace("\\", "/").strip("/").casefold()
    return (
        normalized_candidate == normalized_backend
        or normalized_candidate.endswith("/" + normalized_backend)
    )


def _registered_workflow_binding(
    services: Any,
    record: dict[str, object],
    path: str,
    binding: dict[str, object],
    component_identity_tokens: list[str] | None = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object] | None]:
    inventory = services.discovery.inventory()
    comfy_records = [
        item for item in inventory
        if isinstance(item, dict) and item.get("backend") == "comfyui"
    ]
    registered = services.onboarding.prepare_trust_binding(Path(path), binding)
    graph = registered.get("graph")
    loader_bindings = []
    if isinstance(graph, dict):
        for node in graph.values():
            if not isinstance(node, dict):
                continue
            loader_class = node.get("class_type")
            loader_input = MODEL_LOADER_INPUTS.get(loader_class)
            inputs = node.get("inputs")
            if loader_input is not None and isinstance(inputs, dict):
                loader_bindings.append((loader_class, loader_input, inputs.get(loader_input)))
    component_bundle = None
    if component_identity_tokens is not None:
        selected, component_bundle = _workflow_component_bundle(
            services,
            record,
            graph,
            registered,
            component_identity_tokens,
        )
    else:
        matches = [
            item for item in comfy_records
            if any(
                item.get("backend_model_id") == model_name
                and isinstance(item.get("metadata"), dict)
                and item["metadata"].get("loader_class") == loader_class
                and item["metadata"].get("loader_input") == loader_input
                for loader_class, loader_input, model_name in loader_bindings
            )
        ]
        if record.get("backend") == "comfyui":
            matches = [item for item in matches if identity_token(item) == identity_token(record)]
        if len(matches) != 1:
            raise AssetEngineError(
                "workflow_model_binding_ambiguous",
                "Imported workflow must bind one exact current ComfyUI model identity.",
                "validation",
            )
        selected = matches[0]
    trust_binding = {
        "backend": "comfyui",
        "endpoint_identity": selected["endpoint_identity"],
        "backend_model_id": selected["backend_model_id"],
        "backend_identity_token": identity_token(selected),
        "template_id": registered["template_id"],
        "template_version": registered["template_version"],
        "workflow_sha256": registered["workflow_sha256"],
    }
    if component_bundle is not None:
        trust_binding["component_bundle_sha256"] = component_bundle["bundle_sha256"]
    public_registration = {
        "template_id": registered["template_id"],
        "template_version": registered["template_version"],
        "workflow_sha256": registered["workflow_sha256"],
    }
    return trust_binding, public_registration, component_bundle


def _registered_id_workflow_binding(
    services: Any,
    record: dict[str, object],
    registered_workflow_id: str,
    component_identity_tokens: list[str] | None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    registered = services.workflows.load_registered(registered_workflow_id)
    if component_identity_tokens is None:
        raise AssetEngineError(
            "invalid_component_bundle",
            "Registered workflow trust requires exact selected component identities.",
            "validation",
        )
    selected, component_bundle = _workflow_component_bundle(
        services,
        record,
        registered["graph"],
        registered,
        component_identity_tokens,
    )
    trust_binding = {
        "backend": "comfyui",
        "endpoint_identity": selected["endpoint_identity"],
        "backend_model_id": selected["backend_model_id"],
        "backend_identity_token": identity_token(selected),
        "template_id": registered["template_id"],
        "template_version": registered["template_version"],
        "workflow_sha256": registered["workflow_sha256"],
        "component_bundle_sha256": component_bundle["bundle_sha256"],
    }
    public_registration = {
        "source": "registered",
        "template_id": registered["template_id"],
        "template_version": registered["template_version"],
        "workflow_sha256": registered["workflow_sha256"],
    }
    return trust_binding, public_registration, component_bundle


def _shipped_workflow_binding(
    services: Any,
    record: dict[str, object],
    template_id: str,
    capabilities: dict[str, object],
    component_identity_tokens: list[str] | None = None,
    two_stage_layout: object = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object] | None]:
    normalized_two_stage_layout = None
    if template_id == TWO_STAGE_TEMPLATE_ID:
        normalized_two_stage_layout = validate_two_stage_layout(two_stage_layout)
    elif two_stage_layout is not None:
        raise AssetEngineError(
            "invalid_two_stage_layout",
            "Two-stage layout is allowed only for the reviewed two-stage shipped workflow.",
            "validation",
        )
    if record.get("backend") not in {"comfyui", "filesystem"}:
        raise AssetEngineError(
            "shipped_workflow_requires_backend_identity",
            "A shipped workflow must bind a current ComfyUI or cryptographic filesystem identity.",
            "validation",
        )
    operations = capabilities.get("operations") if isinstance(capabilities, dict) else None
    recommended = capabilities.get("recommended") if isinstance(capabilities, dict) else None
    resolution = recommended.get("resolution") if isinstance(recommended, dict) else None
    if (
        not isinstance(operations, list)
        or len(operations) != 1
        or not isinstance(operations[0], str)
        or not isinstance(recommended, dict)
        or not isinstance(resolution, dict)
    ):
        raise AssetEngineError(
            "invalid_workflow_capabilities",
            "Shipped workflow binding requires one operation and complete recommended settings.",
            "validation",
        )
    try:
        parameters = {
            "positive_prompt": "catalog validation",
            "negative_prompt": "",
            "seed": 0,
            "steps": recommended["steps"],
            "guidance_scale": recommended["guidance"],
            "sampler": recommended["sampler"],
            "scheduler": recommended["scheduler"],
            "width": resolution["width"],
            "height": resolution["height"],
        }
    except KeyError as error:
        raise AssetEngineError(
            "invalid_workflow_capabilities",
            "Shipped workflow binding requires complete recommended settings.",
            "validation",
        ) from error
    resolved_model_id = str(record["backend_model_id"])
    if record.get("backend") == "filesystem":
        resolved_model_id = resolved_model_id.replace("\\", "/").rsplit("/", 1)[-1]
    resolved = services.workflows.inspect_shipped(
        template_id,
        resolved_model_id,
        operations[0],
        parameters,
    )
    if resolved.get("model_family") != capabilities.get("model_family"):
        raise AssetEngineError(
            "workflow_model_family_mismatch",
            "Shipped workflow model family does not match the declared capability boundary.",
            "validation",
        )
    public_registration = {
        "source": "shipped",
        "template_id": resolved["template_id"],
        "template_version": resolved["template_version"],
        "workflow_sha256": resolved["workflow_sha256"],
    }
    component_bundle = None
    if component_identity_tokens is not None:
        selected, component_bundle = _workflow_component_bundle(
            services,
            record,
            resolved.get("graph"),
            public_registration,
            component_identity_tokens,
        )
    else:
        metadata = record.get("metadata")
        loader_bindings = _workflow_loader_bindings(resolved.get("graph"))
        expected = (
            metadata.get("loader_class"),
            metadata.get("loader_input"),
            record.get("backend_model_id"),
        ) if isinstance(metadata, dict) else (None, None, record.get("backend_model_id"))
        if loader_bindings != [expected]:
            raise AssetEngineError(
                "workflow_model_binding_ambiguous",
                "Shipped workflow must bind the exact confirmed ComfyUI loader identity.",
                "validation",
            )
        selected = record
    trust_binding = {
        "backend": "comfyui",
        "endpoint_identity": selected["endpoint_identity"],
        "backend_model_id": selected["backend_model_id"],
        "backend_identity_token": identity_token(selected),
        "template_id": resolved["template_id"],
        "template_version": resolved["template_version"],
        "workflow_sha256": resolved["workflow_sha256"],
    }
    if normalized_two_stage_layout is not None:
        control_sha256 = build_control_identity(
            normalized_two_stage_layout,
            resolved["workflow_sha256"],
            "base-subject-v1",
        )
        trust_binding["control_sha256"] = control_sha256
        public_registration["control_sha256"] = control_sha256
    if component_bundle is not None:
        trust_binding["component_bundle_sha256"] = component_bundle["bundle_sha256"]
    return trust_binding, public_registration, component_bundle


def _workflow_loader_bindings(graph: object) -> list[tuple[object, object, object]]:
    bindings = []
    if not isinstance(graph, dict):
        return bindings
    for node in graph.values():
        if not isinstance(node, dict):
            continue
        loader_class = node.get("class_type")
        loader_input = MODEL_LOADER_INPUTS.get(loader_class)
        inputs = node.get("inputs")
        if loader_input is not None and isinstance(inputs, dict):
            bindings.append((loader_class, loader_input, inputs.get(loader_input)))
    return bindings


def _trust_call(services: Any, arguments: dict[str, Any]) -> dict[str, object]:
    token = arguments["identity_token"]
    if arguments["action"] == "revoke":
        return services.trust.revoke(
            arguments.get("catalog_id"),
            token,
            arguments["confirmation"],
        )

    record = _inventory_identity(services, token)
    workflow_binding = None
    registered_workflow = None
    component_bundle = None
    component_tokens = arguments.get("component_identity_tokens")
    if "workflow_template_id" in arguments:
        workflow_binding, registered_workflow, component_bundle = _shipped_workflow_binding(
            services,
            record,
            arguments["workflow_template_id"],
            arguments["capabilities"],
            component_tokens,
            arguments.get("two_stage_layout"),
        )
    elif "registered_workflow_id" in arguments:
        workflow_binding, registered_workflow, component_bundle = _registered_id_workflow_binding(
            services,
            record,
            arguments["registered_workflow_id"],
            component_tokens,
        )
    elif "workflow_path" in arguments:
        workflow_binding, registered_workflow, component_bundle = _registered_workflow_binding(
            services,
            record,
            arguments["workflow_path"],
            arguments["workflow_binding"],
            component_tokens,
        )
    if arguments["action"] == "inspect_workflow_binding":
        if component_bundle is None:
            raise AssetEngineError(
                "invalid_component_bundle",
                "Workflow inspection did not produce a component bundle.",
                "validation",
            )
        return {
            "identity_token": token,
            "component_bundle": component_bundle,
            "registered_workflow": registered_workflow,
            "confirmations": {
                action: services.trust.confirmation_value(
                    action,
                    record,
                    component_bundle,
                    workflow_binding=workflow_binding,
                )
                for action in ("approve_private", "approve_public_candidate")
            },
        }
    preference = arguments.get("preference", 0)
    if arguments["action"] == "approve_private":
        approval_options = {
            "capabilities": arguments["capabilities"],
            "workflow_binding": workflow_binding,
            "preference": preference,
        }
        if component_bundle is not None:
            approval_options["component_bundle"] = component_bundle
        approved = services.trust.approve_private(record, arguments["confirmation"], **approval_options)
    else:
        approval_options = {
            "metadata": arguments["public_metadata"],
            "capabilities": arguments["capabilities"],
            "workflow_binding": workflow_binding,
            "preference": preference,
        }
        if component_bundle is not None:
            approval_options["component_bundle"] = component_bundle
        approved = services.trust.approve_public_candidate(record, arguments["confirmation"], **approval_options)
    result = {
        field: approved[field]
        for field in ("catalog_id", "identity_token", "identity_strength", "scope")
    }
    if registered_workflow is not None:
        result["registered_workflow"] = registered_workflow
    if component_bundle is not None:
        result["component_bundle"] = component_bundle
    return result


def unreachable_dispatch_error(name: object) -> dict[str, Any]:
    """Report a tool that passed schema lookup but matched no dispatch branch.

    Reaching this means the routing group and the per-tool branches have
    desynchronized. It is reported explicitly instead of silently falling
    through to whichever handler happens to be last.
    """
    return tool_error(
        "unknown_tool",
        "validation",
        f"Unknown tool: {name}",
        {"toolName": name},
    )


def handle_tool_call(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    tool = next((candidate for candidate in tool_schema() if candidate["name"] == name), None)
    if tool is None:
        return tool_error(
            "unknown_tool",
            "validation",
            f"Unknown tool: {name}",
            {"toolName": name},
        )

    arguments = params.get("arguments", {})
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        return tool_error(
            "invalid_arguments",
            "validation",
            "Tool arguments must be a JSON object.",
        )
    validation_error = validate_tool_arguments(tool, arguments)
    if validation_error:
        return validation_error

    if name == "local_gpu_imagegen_check":
        code, stdout, stderr = run_script("check_gpu.py")
        result = script_json_result("check_gpu.py", code, stdout, stderr, {0, 1})
        report = result.get("structuredContent")
        if (
            not result["isError"]
            and isinstance(report, dict)
            and report.get("ready") is False
        ):
            return tool_success({**report, "bootstrap": bootstrap_guidance(report)})
        return result

    if name == "local_gpu_generate_image":
        prompt = arguments.get("prompt")

        args = ["--prompt", prompt]
        mapping = {
            "negative_prompt": "--negative-prompt",
            "model": "--model",
            "backend": "--backend",
            "mode": "--mode",
            "webui_url": "--webui-url",
            "sampler_name": "--sampler-name",
            "scheduler": "--scheduler",
            "input_image": "--input-image",
            "mask_image": "--mask-image",
            "strength": "--strength",
            "lora_scale": "--lora-scale",
            "width": "--width",
            "height": "--height",
            "steps": "--steps",
            "guidance_scale": "--guidance-scale",
            "seed": "--seed",
            "output_dir": "--output-dir",
            "filename": "--filename",
        }
        for key, flag in mapping.items():
            if key in arguments and arguments[key] is not None:
                args.extend([flag, str(arguments[key])])
        loras = arguments.get("lora") or []
        for lora in loras:
            args.extend(["--lora", str(lora)])
        if arguments.get("allow_cpu"):
            args.append("--allow-cpu")
        if arguments.get("cpu_offload"):
            args.append("--cpu-offload")
        if arguments.get("vae_tiling"):
            args.append("--vae-tiling")
        if arguments.get("disable_safety_checker"):
            args.append("--disable-safety-checker")
        if arguments.get("allow_download"):
            args.append("--allow-download")
        code, stdout, stderr = run_script("generate_image.py", args)
        return script_json_result("generate_image.py", code, stdout, stderr)

    try:
        if name in {
            "local_gpu_discover_models",
            "local_gpu_inspect_workflow",
            "local_gpu_register_workflow",
            "local_gpu_set_model_trust",
            "local_gpu_recommend_models",
        }:
            services = get_runtime_services()
            if name == "local_gpu_discover_models":
                data = _successful_engine_data(_discovery_call(services, arguments))
                return tool_success(_bounded_discovery_data(data))
            if name == "local_gpu_inspect_workflow":
                data = services.onboarding.inspect(Path(arguments["workflow_path"]))
                return tool_success(_successful_engine_data(data))
            if name == "local_gpu_register_workflow":
                data = services.onboarding.register(
                    Path(arguments["workflow_path"]),
                    arguments["proposal_digest"],
                    arguments["confirmation"],
                )
                return tool_success(_successful_engine_data(data))
            if name == "local_gpu_set_model_trust":
                return tool_success(_successful_engine_data(_trust_call(services, arguments)))
            if name == "local_gpu_recommend_models":
                return tool_success(_successful_engine_data(services.router.recommend(arguments)))
            return unreachable_dispatch_error(name)
        engine = get_asset_engine()
        if name == "local_gpu_list_profiles":
            data = _successful_engine_data(engine.list_profiles(arguments.get("authorization_scope", "private")))
            return tool_success(data)
        if name == "local_gpu_start_run":
            data = _successful_engine_data(engine.start_run(arguments))
            return tool_success(data)
        if name == "local_gpu_get_run":
            data = _successful_engine_data(engine.get_run(arguments))
            return tool_success(data)
        if name == "local_gpu_branch_run":
            data = _successful_engine_data(engine.branch_run(arguments))
            return tool_success(data)
        if name == "local_gpu_prepare_mask":
            data, preview = engine.prepare_mask(arguments)
            return tool_success(_successful_engine_data(data), _preview_block(preview))
        if name == "local_gpu_confirm_mask":
            data = _successful_engine_data(engine.confirm_mask(arguments))
            return tool_success(data)
        if name == "local_gpu_generate_round":
            data, preview = engine.generate_round(arguments)
            return tool_success(_successful_engine_data(data), _preview_block(preview))
        if name == "local_gpu_record_review":
            review = {
                field: arguments[field]
                for field in (
                    "scores", "hard_failures", "critique", "constraint_results",
                    "visual_checks", "stage_checks", "preservation_results", "next_action",
                )
                if field in arguments
            }
            data = _successful_engine_data(engine.record_review({
                "run_id": arguments["run_id"],
                "round_number": arguments["round_number"],
                "review": review,
            }))
            return tool_success(data)
        if name == "local_gpu_finalize_run":
            data = _successful_engine_data(engine.finalize_run(arguments))
            return tool_success(data)
        if name == "local_gpu_cleanup_run":
            data = _successful_engine_data(engine.cleanup_run(arguments))
            return tool_success(data)
    except AssetEngineError as error:
        return _asset_error(error)

    raise AssertionError(f"Unhandled tool schema: {name}")


def handle_request(request: dict[str, Any]) -> None:
    request_id = request.get("id")
    method = request.get("method")

    if request_id is None:
        return

    if request.get("jsonrpc") != "2.0":
        send(jsonrpc_error(request_id, -32600, "jsonrpc must be 2.0", "invalid_request"))
        return

    if method == "initialize":
        send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "local-gpu-imagegen", "version": SERVER_VERSION},
                },
            }
        )
        return

    if method == "tools/list":
        send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tool_schema()}})
        return

    if method == "ping":
        send({"jsonrpc": "2.0", "id": request_id, "result": {}})
        return

    if method == "tools/call":
        params = request.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            send(jsonrpc_error(request_id, -32602, "tools/call params must be a JSON object.", "invalid_params"))
            return
        send({"jsonrpc": "2.0", "id": request_id, "result": handle_tool_call(params)})
        return

    send(jsonrpc_error(request_id, -32601, f"Method not found: {method}", "method_not_found"))


def process_line(line: str) -> None:
    try:
        request = json.loads(line.lstrip("\ufeff"))
    except json.JSONDecodeError as exc:
        send(
            jsonrpc_error(
                None,
                -32700,
                "Parse error.",
                "parse_error",
                {"line": exc.lineno, "column": exc.colno},
            )
        )
        return

    if not isinstance(request, dict):
        send(jsonrpc_error(None, -32600, "Request must be a JSON object.", "invalid_request"))
        return

    request_id = request.get("id")
    try:
        handle_request(request)
    except Exception as exc:
        send(
            jsonrpc_error(
                request_id,
                -32603,
                "Internal server error.",
                "internal_error",
                {"exceptionType": type(exc).__name__},
            )
        )


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        process_line(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
