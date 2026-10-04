"""Tool argument validation against the JSON schema catalogue."""

from __future__ import annotations

import math
from typing import Any

from _protocol import tool_error
from local_gpu_imagegen.two_stage_layout import TWO_STAGE_TEMPLATE_ID, validate_two_stage_layout


def schema_type_matches(value: object, schema_type: object) -> bool:
    if isinstance(schema_type, list):
        return any(schema_type_matches(value, candidate) for candidate in schema_type)
    if schema_type == "null":
        return value is None
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "boolean":
        return type(value) is bool
    if schema_type == "integer":
        return type(value) is int
    if schema_type == "number":
        return type(value) in (int, float) and math.isfinite(value)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "object":
        return isinstance(value, dict)
    return False


def _validate_nested_object(field: str, value: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any] | None:
    properties = schema.get("properties", {})
    unknown = sorted(set(value) - set(properties))
    if unknown:
        fields = [f"{field}.{name}" for name in unknown]
        return tool_error(
            "unknown_argument",
            "validation",
            f"Unknown nested tool argument(s): {', '.join(fields)}.",
            {"fields": fields},
        )
    for name in schema.get("required", []):
        if name not in value:
            nested_field = f"{field}.{name}"
            return tool_error(
                "missing_argument",
                "validation",
                f"{field} requires {name}.",
                {"field": nested_field},
            )
    for name, nested_value in value.items():
        nested_schema = properties[name]
        expected_type = nested_schema.get("type")
        nested_field = f"{field}.{name}"
        if expected_type and not schema_type_matches(nested_value, expected_type):
            return tool_error(
                "invalid_argument_type",
                "validation",
                f"{nested_field} must be a JSON {expected_type}.",
                {"field": nested_field, "expectedType": expected_type},
            )
        if "enum" in nested_schema and nested_value not in nested_schema["enum"]:
            return tool_error(
                "invalid_argument_value",
                "validation",
                f"{nested_field} is not supported.",
                {"field": nested_field, "allowed": nested_schema["enum"]},
            )
    return None


def validate_tool_arguments(tool: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any] | None:
    schema = tool["inputSchema"]
    properties = schema.get("properties", {})
    unknown = sorted(set(arguments) - set(properties))
    if unknown:
        return tool_error(
            "unknown_argument",
            "validation",
            f"Unknown tool argument(s): {', '.join(unknown)}.",
            {"fields": unknown},
        )

    for field in schema.get("required", []):
        if field not in arguments:
            tool_name = tool["name"]
            message = (
                "local_gpu_generate_image requires a non-empty prompt."
                if field == "prompt"
                else f"{tool_name} requires {field}."
            )
            return tool_error(
                "invalid_prompt" if field == "prompt" else "missing_argument",
                "validation",
                message,
                {"field": field},
            )

    for field, value in arguments.items():
        field_schema = properties[field]
        expected_type = field_schema.get("type")
        if expected_type and not schema_type_matches(value, expected_type):
            code = "invalid_lora" if field == "lora" else "invalid_argument_type"
            type_name = " or ".join(expected_type) if isinstance(expected_type, list) else expected_type
            message = "lora must be an array of strings." if field == "lora" else f"{field} must be a JSON {type_name}."
            return tool_error(code, "validation", message, {"field": field, "expectedType": expected_type})
        if "enum" in field_schema and value not in field_schema["enum"]:
            allowed_text = ", ".join("null" if item is None else str(item) for item in field_schema["enum"])
            return tool_error(
                "invalid_argument_value",
                "validation",
                f"{field} must be one of: {allowed_text}.",
                {"field": field, "allowed": field_schema["enum"]},
            )
        if expected_type in ("integer", "number"):
            if "exclusiveMinimum" in field_schema and value <= field_schema["exclusiveMinimum"]:
                return tool_error(
                    "invalid_argument_value",
                    "validation",
                    f"{field} must be greater than {field_schema['exclusiveMinimum']}.",
                    {"field": field, "exclusiveMinimum": field_schema["exclusiveMinimum"]},
                )
            if "minimum" in field_schema and value < field_schema["minimum"]:
                return tool_error(
                    "invalid_argument_value",
                    "validation",
                    f"{field} must be at least {field_schema['minimum']}.",
                    {"field": field, "minimum": field_schema["minimum"]},
                )
            if "maximum" in field_schema and value > field_schema["maximum"]:
                return tool_error(
                    "invalid_argument_value",
                    "validation",
                    f"{field} must be at most {field_schema['maximum']}.",
                    {"field": field, "maximum": field_schema["maximum"]},
                )
            if "multipleOf" in field_schema and value % field_schema["multipleOf"] != 0:
                return tool_error(
                    "invalid_dimensions" if field in ("width", "height") else "invalid_argument_value",
                    "validation",
                    f"{field} must be divisible by {field_schema['multipleOf']}.",
                    {"field": field, "multipleOf": field_schema["multipleOf"]},
                )
        if "const" in field_schema and value != field_schema["const"]:
            return tool_error(
                "invalid_argument_value",
                "validation",
                f"{field} must equal {field_schema['const']}.",
                {"field": field, "expected": field_schema["const"]},
            )
        if expected_type == "string" and "minLength" in field_schema and len(value.strip()) < field_schema["minLength"]:
            return tool_error(
                "invalid_argument_value",
                "validation",
                f"{field} must be a non-empty string.",
                {"field": field},
            )
        if expected_type == "array" and "items" in field_schema:
            if "minItems" in field_schema and len(value) < field_schema["minItems"]:
                return tool_error(
                    "invalid_argument_value",
                    "validation",
                    f"{field} must contain at least {field_schema['minItems']} item(s).",
                    {"field": field, "minItems": field_schema["minItems"]},
                )
            item_type = field_schema["items"].get("type")
            if item_type and not all(schema_type_matches(item, item_type) for item in value):
                return tool_error(
                    "invalid_lora" if field == "lora" else "invalid_argument_type",
                    "validation",
                    f"{field} must be an array of {item_type}s.",
                    {"field": field, "itemType": item_type},
                )

    if tool["name"] == "local_gpu_finalize_run" and "postprocess" in arguments:
        postprocess = arguments["postprocess"]
        assert isinstance(postprocess, dict)
        nested_error = _validate_nested_object("postprocess", postprocess, properties["postprocess"])
        if nested_error is not None:
            return nested_error

    if tool["name"] == "local_gpu_start_run" and "initial_regional_conditioning" in arguments:
        conditioning = arguments["initial_regional_conditioning"]
        assert isinstance(conditioning, dict)
        nested_error = _validate_nested_object(
            "initial_regional_conditioning",
            conditioning,
            properties["initial_regional_conditioning"],
        )
        if nested_error is not None:
            return nested_error

    if tool["name"] == "local_gpu_discover_models":
        phase = arguments.get("phase")
        if phase == "plan":
            forbidden = sorted(set(arguments) & {"plan_id", "confirmation", "network_confirmation"})
            if forbidden:
                return tool_error(
                    "invalid_discovery_phase",
                    "validation",
                    "Discovery planning cannot include execution confirmation fields.",
                    {"fields": forbidden},
                )
        elif phase == "execute" and "plan_id" not in arguments:
            return tool_error(
                "missing_argument",
                "validation",
                "Discovery execution requires plan_id.",
                {"field": "plan_id"},
            )

    if tool["name"] == "local_gpu_set_model_trust":
        action = arguments.get("action")
        if "two_stage_layout" in arguments:
            layout = arguments["two_stage_layout"]
            assert isinstance(layout, dict)
            nested_error = _validate_nested_object(
                "two_stage_layout",
                layout,
                properties["two_stage_layout"],
            )
            if nested_error is not None:
                return nested_error
        template_id = arguments.get("workflow_template_id")
        has_two_stage_layout = "two_stage_layout" in arguments
        if has_two_stage_layout and (
            action == "revoke" or template_id != TWO_STAGE_TEMPLATE_ID
        ) or (
            action != "revoke"
            and template_id == TWO_STAGE_TEMPLATE_ID
            and not has_two_stage_layout
        ):
            return tool_error(
                "invalid_two_stage_layout",
                "validation",
                "Two-stage layout is required only for the reviewed two-stage shipped workflow.",
                {"field": "two_stage_layout", "workflowTemplateId": template_id},
            )
        if has_two_stage_layout:
            try:
                validate_two_stage_layout(arguments["two_stage_layout"])
            except AssetEngineError as error:
                return tool_error(error.code, error.category, error.args[0], error.details)
        if action in {"inspect_workflow_binding", "approve_private", "approve_public_candidate"} and "capabilities" not in arguments:
            return tool_error(
                "missing_argument",
                "validation",
                "Model approval requires declared capabilities.",
                {"field": "capabilities"},
            )
        if action in {"approve_private", "approve_public_candidate", "revoke"} and "confirmation" not in arguments:
            return tool_error(
                "missing_argument",
                "validation",
                "Trust mutation requires exact confirmation.",
                {"field": "confirmation"},
            )
        if action == "approve_public_candidate" and "public_metadata" not in arguments:
            return tool_error(
                "missing_argument",
                "validation",
                "Public candidate approval requires public_metadata.",
                {"field": "public_metadata"},
            )
        if ("workflow_path" in arguments) != ("workflow_binding" in arguments):
            return tool_error(
                "invalid_workflow_binding",
                "validation",
                "workflow_path and workflow_binding must be provided together.",
                {"fields": ["workflow_path", "workflow_binding"]},
            )
        workflow_sources = [
            "workflow_template_id" in arguments,
            "registered_workflow_id" in arguments,
            "workflow_path" in arguments,
        ]
        if sum(workflow_sources) > 1:
            return tool_error(
                "invalid_workflow_binding",
                "validation",
                "Choose one shipped, registered, or legacy imported workflow source.",
                {
                    "fields": [
                        "workflow_template_id",
                        "registered_workflow_id",
                        "workflow_path",
                        "workflow_binding",
                    ],
                },
            )
        has_workflow = any(workflow_sources)
        has_components = "component_identity_tokens" in arguments
        if has_components and not has_workflow:
            return tool_error(
                "invalid_component_bundle",
                "Component identities require one reviewed workflow.",
                {"field": "component_identity_tokens"},
            )
        if action == "inspect_workflow_binding" and (not has_workflow or not has_components):
            return tool_error(
                "invalid_component_bundle",
                "Workflow inspection requires a reviewed workflow and selected component identities.",
                {"fields": ["workflow_template_id", "registered_workflow_id", "workflow_path", "component_identity_tokens"]},
            )

    if tool["name"] == "local_gpu_branch_run":
        edit_mode = arguments.get("edit_mode")
        has_strength = "denoising_strength" in arguments
        if edit_mode == "prompt-refine" and has_strength or edit_mode in {"img2img", "inpaint"} and not has_strength:
            return tool_error(
                "invalid_denoising_strength",
                "validation",
                "denoising_strength is required only for img2img and inpaint revisions.",
                {"field": "denoising_strength", "edit_mode": edit_mode},
            )

    if tool["name"] == "local_gpu_prepare_mask":
        has_user_mask = "user_mask_path" in arguments
        has_geometry = "geometry" in arguments
        if has_user_mask == has_geometry:
            return tool_error(
                "invalid_mask_source",
                "validation",
                "Provide exactly one of user_mask_path or geometry.",
                {"fields": ["user_mask_path", "geometry"]},
            )

    prompt = arguments.get("prompt")
    if "prompt" in properties and (not isinstance(prompt, str) or not prompt.strip()):
        return tool_error(
            "invalid_prompt",
            "validation",
            "local_gpu_generate_image requires a non-empty prompt.",
            {"field": "prompt"},
        )

    mode = arguments.get("mode", "txt2img")
    if mode in ("img2img", "inpaint") and not arguments.get("input_image"):
        return tool_error(
            "invalid_mode_arguments",
            "validation",
            f"input_image is required for {mode} mode.",
            {"field": "input_image", "mode": mode},
        )
    if mode == "inpaint" and not arguments.get("mask_image"):
        return tool_error(
            "invalid_mode_arguments",
            "validation",
            "mask_image is required for inpaint mode.",
            {"field": "mask_image", "mode": mode},
        )
    if mode == "txt2img" and (arguments.get("input_image") or arguments.get("mask_image")):
        return tool_error(
            "invalid_mode_arguments",
            "validation",
            "input_image and mask_image are only valid for img2img/inpaint modes.",
            {"mode": mode},
        )
    if (
        tool["name"] == "local_gpu_cleanup_run"
        and arguments.get("scope") == "all"
        and arguments.get("confirmation") != arguments.get("run_id")
    ):
        return tool_error(
            "invalid_confirmation",
            "validation",
            "confirmation must exactly equal run_id when scope is all.",
            {"field": "confirmation"},
        )
    if tool["name"] == "local_gpu_generate_round":
        plan = arguments.get("plan")
        parameters = plan.get("parameters") if isinstance(plan, dict) else None
        nested_mode = parameters.get("mode") if isinstance(parameters, dict) else None
        if nested_mode is not None and nested_mode != arguments.get("edit_mode"):
            return tool_error(
                "edit_mode_mismatch",
                "validation",
                "Generation plan parameters.mode must match the authoritative edit_mode.",
                {"edit_mode": arguments.get("edit_mode"), "plan_mode": nested_mode},
            )
    return None
