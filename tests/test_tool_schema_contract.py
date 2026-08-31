"""Contract tests for the agent-facing tool schema.

An MCP tool schema is the entire interface an agent has before it calls. These
tests keep that interface honest in two directions:

* every documented constraint must be enforced by the validator, and
* every parameter must explain itself.

They exist because both properties had already silently drifted: the
``local_gpu_generate_image`` schema advertised width/height as any integer in
256..1536 while the validator additionally required divisibility by 8, and 109
of 118 parameters carried no description at all.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _schema  # noqa: E402
from _validation import validate_tool_arguments  # noqa: E402


def _iter_properties(schema: dict) -> list[tuple[str, dict]]:
    """Yield (dotted_name, subschema) for every declared property, recursively."""
    found: list[tuple[str, dict]] = []

    def walk(node: object, prefix: str) -> None:
        if not isinstance(node, dict):
            return
        properties = node.get("properties")
        if isinstance(properties, dict):
            for name, sub in properties.items():
                if not isinstance(sub, dict):
                    continue
                dotted = f"{prefix}.{name}" if prefix else name
                found.append((dotted, sub))
                walk(sub, dotted)
        items = node.get("items")
        if isinstance(items, dict):
            walk(items, f"{prefix}[]")
        for combinator in ("oneOf", "anyOf", "allOf"):
            branches = node.get(combinator)
            if isinstance(branches, list):
                for index, branch in enumerate(branches):
                    walk(branch, f"{prefix}({combinator}{index})")

    walk(schema, "")
    return found


def _placeholder(schema: dict) -> object:
    """Build a minimal value satisfying a required sibling argument."""
    if "enum" in schema and isinstance(schema["enum"], list) and schema["enum"]:
        for candidate in schema["enum"]:
            if candidate is not None:
                return candidate
    declared = schema.get("type")
    kind = declared[0] if isinstance(declared, list) and declared else declared
    if kind == "integer":
        return int(schema.get("minimum", 1)) or 1
    if kind == "number":
        return float(schema.get("minimum", 1)) or 1.0
    if kind == "boolean":
        return True
    if kind == "array":
        return []
    if kind == "object":
        return {}
    return "placeholder"


class ToolSchemaDescriptionCoverageTest(unittest.TestCase):
    """Every agent-visible parameter must describe itself."""

    def test_every_tool_has_a_description(self) -> None:
        for tool in _schema.tool_schema():
            with self.subTest(tool=tool["name"]):
                description = tool.get("description")
                self.assertIsInstance(description, str)
                self.assertTrue(description.strip())

    def test_every_top_level_parameter_has_a_description(self) -> None:
        missing: list[str] = []
        for tool in _schema.tool_schema():
            properties = (tool.get("inputSchema") or {}).get("properties") or {}
            for name, sub in properties.items():
                if not isinstance(sub, dict) or not str(sub.get("description", "")).strip():
                    missing.append(f"{tool['name']}.{name}")
        self.assertEqual(
            missing,
            [],
            "Every tool parameter must carry a description; missing: " + ", ".join(missing),
        )

    def test_nested_object_parameters_have_descriptions(self) -> None:
        missing: list[str] = []
        for tool in _schema.tool_schema():
            for dotted, sub in _iter_properties(tool.get("inputSchema") or {}):
                if "." not in dotted and "[" not in dotted and "(" not in dotted:
                    continue
                if not str(sub.get("description", "")).strip():
                    missing.append(f"{tool['name']}.{dotted}")
        self.assertEqual(
            missing,
            [],
            "Nested schema fields must also describe themselves; missing: " + ", ".join(missing),
        )


class ToolSchemaEnforcementParityTest(unittest.TestCase):
    """Documented numeric constraints must actually be enforced."""

    def _tool(self, name: str) -> dict:
        for tool in _schema.tool_schema():
            if tool["name"] == name:
                return tool
        raise AssertionError(f"unknown tool {name}")

    def test_multiple_of_is_enforced_wherever_it_is_documented(self) -> None:
        checked = 0
        for tool in _schema.tool_schema():
            input_schema = tool.get("inputSchema") or {}
            properties = input_schema.get("properties") or {}
            required = list(input_schema.get("required") or [])
            for name, sub in properties.items():
                step = sub.get("multipleOf")
                minimum = sub.get("minimum")
                if not isinstance(step, int) or not isinstance(minimum, int):
                    continue
                offending = minimum + 1
                if offending % step == 0:
                    offending += 1
                arguments: dict[str, object] = {name: offending}
                for other in required:
                    if other == name:
                        continue
                    arguments.setdefault(other, _placeholder(properties.get(other) or {}))
                error = validate_tool_arguments(tool, arguments)
                self.assertIsNotNone(
                    error,
                    f"{tool['name']}.{name} documents multipleOf={step} but accepted {offending}",
                )
                checked += 1
        self.assertGreater(checked, 0, "expected at least one multipleOf constraint to verify")

    def test_generate_image_rejects_width_not_divisible_by_eight(self) -> None:
        tool = self._tool("local_gpu_generate_image")
        error = validate_tool_arguments(tool, {"prompt": "test", "width": 513})
        self.assertIsNotNone(error)
        self.assertEqual(error["structuredContent"]["error"]["code"], "invalid_dimensions")

    def test_generate_image_accepts_width_divisible_by_eight(self) -> None:
        tool = self._tool("local_gpu_generate_image")
        self.assertIsNone(validate_tool_arguments(tool, {"prompt": "test", "width": 512}))

    def test_documented_bounds_are_enforced(self) -> None:
        tool = self._tool("local_gpu_generate_image")
        below = validate_tool_arguments(tool, {"prompt": "test", "width": 8})
        self.assertIsNotNone(below)
        above = validate_tool_arguments(tool, {"prompt": "test", "width": 4096})
        self.assertIsNotNone(above)


class ToolDispatchRegistryTest(unittest.TestCase):
    """Dispatch must be explicit, never a fallthrough."""

    def test_every_tool_name_is_unique(self) -> None:
        names = [tool["name"] for tool in _schema.tool_schema()]
        self.assertEqual(len(names), len(set(names)))

    def test_tool_count_is_the_published_seventeen(self) -> None:
        self.assertEqual(len(_schema.tool_schema()), 17)


if __name__ == "__main__":
    unittest.main()
