from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.research import f02_product_client


class _DiscoveryClient:
    def __init__(self) -> None:
        self.recommendation_arguments: dict[str, object] | None = None

    def call(self, name: str, arguments: dict[str, object]) -> dict[str, object]:
        if name == "local_gpu_discover_models":
            if arguments["phase"] == "plan":
                return {"plan_id": f"plan-{arguments['stage']}-{arguments['mode']}"}
            if arguments["mode"] == "api_only":
                return {
                    "candidates": [{
                        "backend_model_id": f02_product_client.BACKEND_MODEL_ID,
                        "endpoint_identity": "test-endpoint",
                        "metadata": {
                            "loader_class": "CheckpointLoaderSimple",
                            "loader_input": "ckpt_name",
                        },
                    }]
                }
            if arguments["stage"] == "index":
                return {
                    "candidates": [{
                        "candidate_id": "candidate-1",
                        "filename": f02_product_client.BACKEND_MODEL_ID,
                    }]
                }
            return {
                "candidates": [{
                    "filename": f02_product_client.BACKEND_MODEL_ID,
                    "sha256": f02_product_client.MODEL_SHA256,
                    "identity_token": f02_product_client.MODEL_IDENTITY_TOKEN,
                }]
            }
        if name == "local_gpu_list_profiles":
            bundle = {
                "bundle_sha256": f02_product_client.COMPONENT_BUNDLE_SHA256,
                "workflow": {
                    "sha256": f02_product_client.WORKFLOW_SHA256,
                    "template_id": "sdxl-txt2img",
                    "template_version": 1,
                },
            }
            return {
                "models": {
                    f02_product_client.MODEL_ID: {
                        "backend": "comfyui",
                        "backend_model_id": f02_product_client.BACKEND_MODEL_ID,
                        "endpoint_identity": "test-endpoint",
                        "sha256": f02_product_client.MODEL_SHA256,
                        "trust_identity_token": f02_product_client.MODEL_IDENTITY_TOKEN,
                        "component_bundle_sha256": f02_product_client.COMPONENT_BUNDLE_SHA256,
                        "workflow_template_id": "sdxl-txt2img",
                        "component_bundle": bundle,
                    }
                }
            }
        if name == "local_gpu_recommend_models":
            self.recommendation_arguments = arguments
            return {
                "routes": [{
                    "start_run_boundary": {
                        "backend": "comfyui",
                        "model_choice": f02_product_client.MODEL_ID,
                        "authorization_scope": "private",
                        "route_token": "test-route-token",
                    }
                }]
            }
        raise AssertionError(f"unexpected tool: {name}")


class ProductClientRouteTests(unittest.TestCase):
    def test_recommendation_vram_ceiling_matches_pinned_gpu_class(self) -> None:
        fake = _DiscoveryClient()
        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / f02_product_client.BACKEND_MODEL_ID
            model_path.write_bytes(b"fixture")
            with patch.dict(os.environ, {"LOCAL_GPU_IMAGEGEN_RESEARCH_MODEL_PATH": str(model_path)}):
                f02_product_client._discover_route(fake)

        self.assertIsNotNone(fake.recommendation_arguments)
        self.assertEqual(
            fake.recommendation_arguments["preferred_model_id"],
            f02_product_client.MODEL_ID,
        )
        self.assertEqual(
            fake.recommendation_arguments["required_vram_gb"],
            f02_product_client.ROUTE_VRAM_CEILING_GB,
        )
        self.assertEqual(f02_product_client.ROUTE_VRAM_CEILING_GB, 12.0)
