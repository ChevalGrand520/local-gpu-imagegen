"""Tool schema catalogue and registry-backed enum queries."""

from __future__ import annotations

import json
from typing import Any

from _constants import ROOT
from local_gpu_imagegen.postprocess import SUPPORTED_MODELS
from local_gpu_imagegen.two_stage_layout import TWO_STAGE_LAYOUT_MODE
from local_gpu_imagegen.visual_review import STAGE_CHECK_NAMES


def _object_schema(
    properties: dict[str, Any],
    required: list[str],
) -> dict[str, Any]:
    return {
        "type": "object",
        "required": required,
        "properties": properties,
        "additionalProperties": False,
    }


def _output_schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    common = {
        "ok": {"type": "boolean"},
        "warnings": {"type": "array", "items": {"type": "string"}},
    }
    success = _object_schema({**common, **properties}, ["ok", *required, "warnings"])
    error_value = _object_schema(
        {
            "code": {"type": "string"},
            "category": {"type": "string"},
            "message": {"type": "string"},
            "details": {"type": "object", "additionalProperties": True},
        },
        ["code", "category", "message"],
    )
    error = _object_schema({"error": error_value}, ["error"])
    return {"type": "object", "oneOf": [success, error]}


def tool_schema() -> list[dict[str, Any]]:
    tools = [
        {
            "name": "local_gpu_imagegen_check",
            "description": "Check Python packages and CUDA readiness for local GPU image generation.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "required": ["ready"],
                "properties": {
                    "ready": {"type": "boolean"},
                    "diffusers_ready": {"type": "boolean"},
                    "webui_ready": {"type": "boolean"},
                    "bootstrap": _object_schema(
                        {
                            "support_status": {
                                "type": "string",
                                "enum": ["supported", "unknown", "unsupported"],
                            },
                            "reason_codes": {"type": "array", "items": {"type": "string"}},
                            "estimated_download_bytes": {"type": "integer", "minimum": 0},
                            "estimated_disk_bytes": {"type": "integer", "minimum": 0},
                            "next_action": {"type": "string"},
                        },
                        [
                            "support_status",
                            "reason_codes",
                            "estimated_download_bytes",
                            "estimated_disk_bytes",
                            "next_action",
                        ],
                    ),
                },
                "additionalProperties": True,
            },
        },
        {
            "name": "local_gpu_generate_image",
            "description": "Compatibility tool for WebUI or Diffusers image generation; not for ComfyUI routes and never a bypass for the confirmed high-level run workflow.",
            "inputSchema": {
                "type": "object",
                "required": ["prompt"],
                "properties": {
                    "prompt": {"type": "string"},
                    "negative_prompt": {"type": "string"},
                    "model": {"type": "string"},
                    "backend": {"type": "string", "enum": ["auto", "webui", "diffusers"]},
                    "mode": {"type": "string", "enum": ["txt2img", "img2img", "inpaint"]},
                    "webui_url": {"type": "string"},
                    "sampler_name": {"type": "string"},
                    "scheduler": {"type": "string", "enum": ["default", "dpmpp", "euler", "euler-a", "ddim", "unipc", "lcm"]},
                    "input_image": {"type": "string"},
                    "mask_image": {"type": "string"},
                    "strength": {"type": "number", "minimum": 0, "maximum": 1},
                    "lora": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "lora_scale": {"type": "number", "minimum": 0, "maximum": 2},
                    "cpu_offload": {"type": "boolean"},
                    "vae_tiling": {"type": "boolean"},
                    "disable_safety_checker": {"type": "boolean"},
                    "width": {"type": "integer", "minimum": 256, "maximum": 1536},
                    "height": {"type": "integer", "minimum": 256, "maximum": 1536},
                    "steps": {"type": "integer", "minimum": 1, "maximum": 80},
                    "guidance_scale": {"type": "number", "minimum": 0, "maximum": 20},
                    "seed": {"type": "integer"},
                    "output_dir": {"type": "string"},
                    "filename": {"type": "string"},
                    "allow_cpu": {"type": "boolean"},
                    "allow_download": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "required": ["ok", "path", "backend", "mode"],
                "properties": {
                    "ok": {"type": "boolean"},
                    "path": {"type": "string"},
                    "backend": {"type": "string", "enum": ["webui", "diffusers"]},
                    "mode": {"type": "string", "enum": ["txt2img", "img2img", "inpaint"]},
                },
                "additionalProperties": True,
            },
        },
    ]
    json_object = {"type": "object", "additionalProperties": True}
    json_value = {"type": ["object", "array", "string", "number", "boolean", "null"]}
    json_array = {"type": "array", "items": json_value}
    workflow_defaults = _object_schema({
        "positive_prompt": {"type": "string"},
        "negative_prompt": {"type": "string"},
        "width": {
            "type": "integer", "minimum": 256, "maximum": 1536, "multipleOf": 8,
        },
        "height": {
            "type": "integer", "minimum": 256, "maximum": 1536, "multipleOf": 8,
        },
        "seed": {"type": "integer", "minimum": 0, "maximum": 2**64 - 1},
        "steps": {"type": "integer", "minimum": 1, "maximum": 80},
        "guidance_scale": {
            "type": "number", "exclusiveMinimum": 0, "maximum": 30,
        },
        "sampler_name": {"type": "string", "minLength": 1},
        "scheduler": {"type": "string", "minLength": 1},
    }, [
        "positive_prompt", "negative_prompt", "width", "height", "seed",
        "steps", "guidance_scale", "sampler_name", "scheduler",
    ])
    preserve_item = _object_schema({
        "target": {"type": "string", "minLength": 1},
        "strength": {"type": "string", "enum": ["hard", "soft"]},
    }, ["target", "strength"])
    revision_contract = _object_schema({
        "preserve": {"type": "array", "items": preserve_item},
        "change": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    }, ["preserve", "change"])
    point = _object_schema({
        "x": {"type": "number", "minimum": 0, "maximum": 1},
        "y": {"type": "number", "minimum": 0, "maximum": 1},
    }, ["x", "y"])
    geometry_item = _object_schema({
        "type": {"type": "string", "enum": ["rectangle", "polygon"]},
        "x": {"type": "number", "minimum": 0, "maximum": 1},
        "y": {"type": "number", "minimum": 0, "maximum": 1},
        "width": {"type": "number", "minimum": 0, "maximum": 1},
        "height": {"type": "number", "minimum": 0, "maximum": 1},
        "points": {"type": "array", "minItems": 3, "items": point},
    }, ["type"])
    regional_conditioning = _object_schema({
        "copy_prompt": {"type": "string", "minLength": 1},
        "copy_strength": {"type": "number", "minimum": 0, "maximum": 2},
        "subject_prompt": {"type": "string", "minLength": 1},
        "subject_strength": {"type": "number", "minimum": 0, "maximum": 2},
    }, ["copy_prompt", "copy_strength", "subject_prompt", "subject_strength"])
    two_stage_conditioning = _object_schema({
        "subject_prompt": {"type": "string", "minLength": 1, "maxLength": 2000},
        "subject_negative_prompt": {"type": "string", "minLength": 1, "maxLength": 2000},
        "subject_denoise": {"type": "number", "minimum": 0.8, "maximum": 1.0},
    }, ["subject_prompt", "subject_negative_prompt", "subject_denoise"])
    integer_rect = _object_schema({
        "x": {"type": "integer", "minimum": 0},
        "y": {"type": "integer", "minimum": 0},
        "width": {"type": "integer", "minimum": 1},
        "height": {"type": "integer", "minimum": 1},
    }, ["x", "y", "width", "height"])
    two_stage_layout = _object_schema({
        "mode": {"type": "string", "enum": [TWO_STAGE_LAYOUT_MODE]},
        "canvas": _object_schema({
            "width": {"type": "integer", "minimum": 256, "maximum": 1536},
            "height": {"type": "integer", "minimum": 256, "maximum": 1536},
        }, ["width", "height"]),
        "copy_protected_rect": integer_rect,
        "subject_mask_rect": integer_rect,
        "feather_pixels": {"type": "integer", "minimum": 0, "maximum": 64},
        "vae_grow_mask_by": {"type": "integer", "minimum": 0, "maximum": 64},
    }, [
        "mode", "canvas", "copy_protected_rect", "subject_mask_rect",
        "feather_pixels", "vae_grow_mask_by",
    ])
    start_run_boundary = _object_schema({
        "profile": {"type": "string", "enum": _registered_profile_ids()},
        "style": {"type": ["string", "null"], "enum": [None, *_registered_style_ids()]},
        "constraints": _object_schema({
            "width": {
                "type": "integer", "minimum": 256, "maximum": 1536,
                "multipleOf": 8,
            },
            "height": {
                "type": "integer", "minimum": 256, "maximum": 1536,
                "multipleOf": 8,
            },
        }, ["width", "height"]),
        "model_choice": {"type": "string", "minLength": 1},
        "backend": {"type": "string", "enum": ["webui", "diffusers", "comfyui"]},
        "authorization_scope": {
            "type": "string", "enum": ["private", "public_evidence"],
        },
        "route_token": {"type": "string", "pattern": "^route:[0-9a-f]{64}$"},
    }, [
        "profile", "style", "constraints", "model_choice", "backend",
        "authorization_scope", "route_token",
    ])
    recommendation_route = {
        "type": "object",
        "properties": {"start_run_boundary": start_run_boundary},
        "required": ["start_run_boundary"],
        "additionalProperties": True,
    }
    visual_check = _object_schema({
        "status": {
            "type": "string",
            "enum": ["pass", "fail", "uncertain", "not_applicable"],
        },
        "observation": {"type": "string", "minLength": 1, "maxLength": 500},
    }, ["status", "observation"])
    visual_checks = _object_schema({
        "full_resolution_inspected": {"type": "boolean", "const": True},
        "prominent_human": {"type": "boolean"},
        "limb_separation": visual_check,
        "feet_and_contact": visual_check,
        "hands_and_held_objects": visual_check,
        "text_and_watermarks": visual_check,
    }, [
        "full_resolution_inspected",
        "prominent_human",
        "limb_separation",
        "feet_and_contact",
        "hands_and_held_objects",
        "text_and_watermarks",
    ])
    stage_check = _object_schema({
        "status": {"type": "string", "enum": ["pass", "fail", "uncertain"]},
        "observation": {"type": "string", "minLength": 1, "maxLength": 500},
    }, ["status", "observation"])
    stage_checks = _object_schema(
        {name: stage_check for name in STAGE_CHECK_NAMES},
        list(STAGE_CHECK_NAMES),
    )
    run_manifest_properties = {
        "run_id": {"type": "string"},
        "schema_version": {"type": "integer"},
        "manifest_revision": {"type": "integer"},
        "state": {"type": "string"},
        "last_stable_state": {"type": "string"},
        "active_attempt": json_value,
        "parent": json_value,
        "revision": json_value,
        "request": json_object,
        "attempts": json_array,
        "rounds": json_array,
        "reviews": json_array,
        "masks": json_array,
        "final": json_value,
        "finalization_candidate": json_value,
        "recoverable_next_actions": {"type": "array", "items": {"type": "string"}},
    }
    tools.extend([
        {
            "name": "local_gpu_discover_models",
            "description": "Plan or execute bounded local model discovery without loading model weights.",
            "inputSchema": _object_schema({
                "phase": {"type": "string", "enum": ["plan", "execute"]},
                "mode": {"type": "string", "enum": ["api_only", "selected_folders", "common_locations", "full_drive", "exact_file"]},
                "stage": {"type": "string", "enum": ["index", "fingerprint", "verify", "revoke"]},
                "backends": {"type": "array", "items": {"type": "string", "enum": ["webui", "comfyui"]}},
                "roots": {"type": "array", "items": {"type": "string"}},
                "explicit_includes": {"type": "array", "items": {"type": "string"}},
                "plan_id": {"type": "string", "minLength": 1},
                "confirmation": {"type": "string", "minLength": 1},
                "network_confirmation": {"type": "string", "minLength": 1},
                "selected_candidates": {"type": "array", "items": {"type": "string"}},
                "expected_backend_model_id": {"type": "string", "minLength": 1},
                "authorization_id": {"type": "string", "pattern": "^verification:[0-9a-f]{24}$"},
            }, ["phase"]),
            "outputSchema": _output_schema({
                "plan_id": {"type": "string"},
                "scope_hash": {"type": "string"},
                "expires_at": {"type": "number"},
                "confirmation": {"type": "string"},
                "network_confirmation": {"type": "string"},
                "incomplete": {"type": "boolean"},
                "candidates": json_array,
                "trusted": {"type": "boolean"},
                "confirmation_required": {"type": "boolean"},
                "expected_backend_model_id": {"type": "string"},
                "authorization_id": {"type": ["string", "null"]},
                "byte_size": {"type": "integer", "minimum": 0},
                "modified_ns": {"type": "integer", "minimum": 0},
                "authorization": json_object,
            }, []),
        },
        {
            "name": "local_gpu_inspect_workflow",
            "description": "Inspect one local ComfyUI API workflow and infer a safe ordinary txt2img binding without writing state.",
            "inputSchema": _object_schema({
                "workflow_path": {"type": "string", "minLength": 1},
            }, ["workflow_path"]),
            "outputSchema": _output_schema({
                "status": {"type": "string", "enum": ["diagnostic", "registerable"]},
                "registrable": {"type": "boolean"},
                "source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "workflow_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "topology": {"type": "string", "enum": ["single_checkpoint", "split_model"]},
                "binding": json_object,
                "owned_output": json_object,
                "workflow_defaults": workflow_defaults,
                "components": json_array,
                "limitations": {"type": "array", "items": {"type": "string"}},
                "recoverable_next_actions": {"type": "array", "items": {"type": "string"}},
                "proposal_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "confirmation": {"type": "string"},
                "inventory_diagnostics": json_array,
            }, [
                "status", "registrable", "source_sha256", "workflow_sha256", "topology",
                "binding", "owned_output", "workflow_defaults", "components", "limitations",
                "recoverable_next_actions",
            ]),
        },
        {
            "name": "local_gpu_register_workflow",
            "description": "Recheck and immutably register one exact previously inspected ComfyUI workflow proposal.",
            "inputSchema": _object_schema({
                "workflow_path": {"type": "string", "minLength": 1},
                "proposal_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "confirmation": {"type": "string", "minLength": 1},
            }, ["workflow_path", "proposal_digest", "confirmation"]),
            "outputSchema": _output_schema({
                "registered_workflow_id": {"type": "string", "pattern": "^imported:[0-9a-f]{64}$"},
                "template_version": {"type": "integer", "minimum": 1},
                "source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "workflow_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "topology": {"type": "string", "enum": ["single_checkpoint", "split_model"]},
                "owned_output": json_object,
                "components": json_array,
                "recoverable_next_actions": {"type": "array", "items": {"type": "string"}},
            }, [
                "registered_workflow_id", "template_version", "source_sha256",
                "workflow_sha256", "topology", "owned_output", "components",
                "recoverable_next_actions",
            ]),
        },
        {
            "name": "local_gpu_set_model_trust",
            "description": "Inspect, approve, or revoke one exact current local model identity. A trust mutation requires the exact confirmation previously returned for the same mutation boundary, displayed to the user, and repeated in a later user message.",
            "inputSchema": _object_schema({
                "action": {"type": "string", "enum": ["inspect_workflow_binding", "approve_private", "approve_public_candidate", "revoke"]},
                "identity_token": {"type": "string", "minLength": 1},
                "confirmation": {"type": "string", "minLength": 1},
                "capabilities": json_object,
                "public_metadata": _object_schema({
                    "source": {"type": "string", "minLength": 1},
                    "license_id": {"type": "string", "minLength": 1},
                    "license_url": {"type": "string", "minLength": 1},
                    "output_redistribution_status": {"type": "string", "minLength": 1},
                    "components": {
                        "type": "array",
                        "items": _object_schema({
                            "role": {"type": "string", "enum": ["primary_model", "text_encoder", "vae"]},
                            "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                            "source": {"type": "string", "minLength": 1},
                            "license_id": {"type": "string", "minLength": 1},
                            "license_url": {"type": "string", "minLength": 1},
                            "output_redistribution_status": {"type": "string", "const": "approved"},
                        }, ["role", "sha256", "source", "license_id", "license_url", "output_redistribution_status"]),
                    },
                }, ["source", "license_id", "license_url", "output_redistribution_status"]),
                "component_identity_tokens": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"type": "string", "pattern": "^model:[0-9a-f]{64}$"},
                },
                "workflow_template_id": {
                    "type": "string",
                    "enum": _shipped_workflow_template_ids(),
                },
                "registered_workflow_id": {
                    "type": "string",
                    "pattern": "^imported:[0-9a-f]{64}$",
                },
                "workflow_path": {"type": "string", "minLength": 1},
                "workflow_binding": json_object,
                "catalog_id": {
                    "type": "string",
                    "pattern": "^local:[0-9a-f]{24}$",
                },
                "preference": {"type": "integer", "minimum": -100, "maximum": 100},
                "two_stage_layout": two_stage_layout,
            }, ["action", "identity_token"]),
            "outputSchema": _output_schema({
                "catalog_id": {"type": "string"},
                "identity_token": {"type": "string"},
                "identity_strength": {"type": "string"},
                "scope": {"type": "string"},
                "revoked": {"type": "boolean"},
                "registered_workflow": json_object,
                "component_bundle": json_object,
                "confirmations": json_object,
            }, ["identity_token"]),
        },
        {
            "name": "local_gpu_recommend_models",
            "description": "Recommend one exact confirmed-capability route and at most two alternatives. preferred_model_id must be an exact catalog ID. Requires prior api_only discovery and model trust (local_gpu_discover_models then local_gpu_set_model_trust). Display the selected route and start_run_boundary, then wait for later user confirmation before local_gpu_start_run.",
            "inputSchema": _object_schema({
                "authorization_scope": {"type": "string", "enum": ["private", "public_evidence"]},
                "operation": {"type": "string", "enum": ["txt2img", "img2img", "inpaint"]},
                "profile": {"type": "string", "enum": _registered_profile_ids()},
                "style": {"type": ["string", "null"], "enum": [None, *_registered_style_ids()]},
                "width": {"type": "integer", "minimum": 256, "maximum": 1536},
                "height": {"type": "integer", "minimum": 256, "maximum": 1536},
                "affinity_tags": {"type": "array", "items": {"type": "string"}},
                "required_vram_gb": {"type": ["number", "null"]},
                "preferred_model_id": {
                    "type": ["string", "null"],
                    "pattern": "^local:[0-9a-f]{24}$",
                },
                "regional_layout": {"type": "object"},
                "two_stage_layout": {"type": "object"},
            }, [
                "authorization_scope", "operation", "profile", "style", "width", "height",
                "affinity_tags", "required_vram_gb", "preferred_model_id",
            ]),
            "outputSchema": _output_schema({
                "requirements": json_object,
                "routes": {"type": "array", "items": recommendation_route},
                "reason": {"type": ["string", "null"]},
                "next_action": {"type": "string", "enum": ["display_and_wait"]},
            }, ["requirements", "routes", "reason", "next_action"]),
        },
        {
            "name": "local_gpu_list_profiles",
            "description": "List registered visual-asset profiles and current local backend capabilities.",
            "inputSchema": _object_schema({
                "authorization_scope": {"type": "string", "enum": ["private", "public_evidence"]},
            }, []),
            "outputSchema": _output_schema({
                "profiles": json_object,
                "styles": json_object,
                "models": json_object,
                "capabilities": json_object,
            }, ["profiles", "styles", "models", "capabilities"]),
        },
        {
            "name": "local_gpu_start_run",
            "description": "Create a visual-asset run only after later user confirmation; copy start_run_boundary exactly from the previously displayed recommendation and add the remaining run fields.",
            "inputSchema": _object_schema({
                "intent": {"type": "string", "minLength": 1},
                "profile": {"type": "string", "enum": _registered_profile_ids()},
                "subtype": {"type": "string", "enum": _registered_subtype_ids()},
                "style": {"type": ["string", "null"], "enum": [None, *_registered_style_ids()]},
                "constraints": json_object,
                "initial_regional_conditioning": regional_conditioning,
                "initial_two_stage_conditioning": two_stage_conditioning,
                "model_choice": {"type": "string", "minLength": 1},
                "backend": {"type": "string", "enum": ["webui", "diffusers", "comfyui"]},
                "authorization_scope": {"type": "string", "enum": ["private", "public_evidence"]},
                "route_token": {"type": "string", "minLength": 1},
                "max_rounds": {"type": "integer", "minimum": 1, "maximum": 3},
                "upscale_policy": {"type": "string", "enum": ["auto", "off"]},
            }, [
                "intent", "profile", "subtype", "style", "constraints", "model_choice", "backend",
                "authorization_scope", "route_token", "max_rounds", "upscale_policy",
            ]),
            "outputSchema": _output_schema({
                "run_id": {"type": "string"},
                "state": {"type": "string"},
                "max_rounds": {"type": "integer"},
                "merged_rubric": json_object,
            }, ["run_id", "state", "max_rounds", "merged_rubric"]),
        },
        {
            "name": "local_gpu_get_run",
            "description": "Get the current persisted state of a visual-asset run.",
            "inputSchema": _object_schema({"run_id": {"type": "string", "minLength": 1}}, ["run_id"]),
            "outputSchema": _output_schema(run_manifest_properties, ["run_id", "state", "rounds", "recoverable_next_actions"]),
        },
        {
            "name": "local_gpu_branch_run",
            "description": "Create an immutable child revision run from one reviewed parent round.",
            "inputSchema": _object_schema({
                "parent_run_id": {"type": "string", "minLength": 1},
                "parent_round": {"type": "integer", "minimum": 1, "maximum": 3},
                "contract": revision_contract,
                "max_rounds": {"type": "integer", "minimum": 1, "maximum": 3},
                "edit_mode": {"type": "string", "enum": ["prompt-refine", "img2img", "inpaint"]},
                "denoising_strength": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
            }, ["parent_run_id", "parent_round", "contract", "max_rounds", "edit_mode"]),
            "outputSchema": _output_schema(
                run_manifest_properties,
                ["run_id", "state", "parent", "revision"],
            ),
        },
        {
            "name": "local_gpu_prepare_mask",
            "description": "Prepare an unconfirmed child-run inpaint mask and return its JPEG overlay.",
            "inputSchema": _object_schema({
                "run_id": {"type": "string", "minLength": 1},
                "user_mask_path": {"type": "string", "minLength": 1},
                "geometry": {"type": "array", "minItems": 1, "items": geometry_item},
                "feather_pixels": {"type": "integer", "minimum": 0, "maximum": 64},
            }, ["run_id"]),
            "outputSchema": _output_schema({
                "mask_id": {"type": "string"},
                "source": {"type": "string", "enum": ["geometry", "user"]},
                "source_image_sha256": {"type": "string"},
                "mask_sha256": {"type": "string"},
                "geometry": json_value,
                "feather_pixels": {"type": "integer"},
                "mask_path": {"type": "string"},
                "overlay_path": {"type": "string"},
                "confirmed": {"type": "boolean"},
                "confirmed_at": json_value,
            }, ["mask_id", "mask_path", "overlay_path", "confirmed"]),
        },
        {
            "name": "local_gpu_confirm_mask",
            "description": "Confirm an unchanged prepared mask after explicit overlay approval.",
            "inputSchema": _object_schema({
                "run_id": {"type": "string", "minLength": 1},
                "mask_id": {"type": "string", "minLength": 1},
            }, ["run_id", "mask_id"]),
            "outputSchema": _output_schema({
                "mask_id": {"type": "string"},
                "source": {"type": "string", "enum": ["geometry", "user"]},
                "source_image_sha256": {"type": "string"},
                "mask_sha256": {"type": "string"},
                "geometry": json_value,
                "feather_pixels": {"type": "integer"},
                "mask_path": {"type": "string"},
                "overlay_path": {"type": "string"},
                "confirmed": {"type": "boolean"},
                "confirmed_at": json_value,
            }, ["mask_id", "mask_path", "overlay_path", "confirmed"]),
        },
        {
            "name": "local_gpu_generate_round",
            "description": "Generate one root or immutable revision round and return an optional bounded JPEG preview. Construct the plan from the frozen run returned by local_gpu_get_run, copying every confirmed route, identity, workflow, compiler, policy, and budget field.",
            "inputSchema": _object_schema({
                "run_id": {"type": "string", "minLength": 1},
                "idempotency_key": {"type": "string", "minLength": 1},
                "action": {"type": "string", "enum": ["initial", "refine", "explore"]},
                "edit_mode": {"type": "string", "enum": ["txt2img", "img2img", "inpaint"]},
                "mask_id": {"type": "string", "minLength": 1},
                "plan": json_object,
                "seed": {"type": "integer"},
                "change_summary": {"type": "string", "minLength": 1},
            }, ["run_id", "idempotency_key", "action", "edit_mode", "plan", "seed", "change_summary"]),
            "outputSchema": _output_schema({
                "run_id": {"type": "string"},
                "state": {"type": "string"},
                "round": json_object,
                "full_image_path": {"type": "string"},
                "recoverable_next_actions": {"type": "array", "items": {"type": "string"}},
            }, ["run_id", "state", "round", "full_image_path"]),
        },
        {
            "name": "local_gpu_record_review",
            "description": "Record human or model review evidence for one generated round.",
            "inputSchema": _object_schema({
                "run_id": {"type": "string", "minLength": 1},
                "round_number": {"type": "integer", "minimum": 1, "maximum": 3},
                "scores": json_object,
                "hard_failures": {"type": "array", "items": {"type": "string"}},
                "critique": {"type": "string", "minLength": 1},
                "constraint_results": json_object,
                "visual_checks": visual_checks,
                "stage_checks": stage_checks,
                "preservation_results": {"type": "array", "items": json_object},
                "next_action": {"type": "string", "enum": ["refine", "explore", "finalize"]},
            }, [
                "run_id",
                "round_number",
                "scores",
                "hard_failures",
                "critique",
                "constraint_results",
                "visual_checks",
                "next_action",
            ]),
            "outputSchema": _output_schema(run_manifest_properties, ["run_id", "state", "rounds", "reviews", "recoverable_next_actions"]),
        },
        {
            "name": "local_gpu_finalize_run",
            "description": "Publish the selected reviewed round as the run's final PNG.",
            "inputSchema": _object_schema({
                "run_id": {"type": "string", "minLength": 1},
                "round_number": {"type": "integer", "minimum": 1, "maximum": 3},
                "summary": {"type": "string", "minLength": 1},
                "confirmation": {"type": "string", "minLength": 1},
                "postprocess": _object_schema({
                    "type": {"type": "string", "enum": ["anime_upscale"]},
                    "model": {"type": "string", "enum": sorted(SUPPORTED_MODELS)},
                }, ["type", "model"]),
            }, ["run_id", "round_number", "summary", "confirmation"]),
            "outputSchema": _output_schema({
                **run_manifest_properties,
                "max_rounds": {"type": ["integer", "null"]},
                "full_image_path": {"type": "string"},
            }, ["run_id", "state", "final", "full_image_path", "recoverable_next_actions"]),
        },
        {
            "name": "local_gpu_cleanup_run",
            "description": "Remove run intermediates or a fully confirmed run directory.",
            "inputSchema": _object_schema({
                "run_id": {"type": "string", "minLength": 1},
                "scope": {"type": "string", "enum": ["intermediates", "all"]},
                "confirmation": {"type": "string"},
            }, ["run_id", "scope", "confirmation"]),
            "outputSchema": _output_schema({
                "run_id": {"type": "string"},
                "scope": {"type": "string", "enum": ["intermediates", "all"]},
            }, ["run_id", "scope"]),
        },
    ])
    return tools


def _registered_profile_ids() -> list[str]:
    return sorted(path.stem for path in (ROOT / "profiles" / "use-cases").glob("*.json"))


def _registered_style_ids() -> list[str]:
    return sorted(path.stem for path in (ROOT / "profiles" / "styles").glob("*.json"))


def _registered_subtype_ids() -> list[str]:
    subtypes: set[str] = set()
    for path in (ROOT / "profiles" / "use-cases").glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        values = document.get("subtypes") if isinstance(document, dict) else None
        if isinstance(values, list):
            subtypes.update(value for value in values if isinstance(value, str) and value)
    return sorted(subtypes)


def _shipped_workflow_template_ids() -> list[str]:
    template_ids = []
    for path in (ROOT / "workflows" / "comfyui").glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        template_id = document.get("template_id") if isinstance(document, dict) else None
        if _workflow_template_is_public(template_id):
            template_ids.append(template_id)
    return sorted(template_ids)


def _workflow_template_is_public(template_id: object) -> bool:
    return isinstance(template_id, str) and bool(template_id)


def _approved_model_ids() -> list[str]:
    from local_gpu_imagegen.profile_registry import ProfileRegistry

    models = ProfileRegistry(ROOT / "profiles").list_catalog()["models"]
    return sorted(
        model_id
        for model_id, model in models.items()
        if model.get("enabled") is True and model.get("license_status") == "approved"
    )
