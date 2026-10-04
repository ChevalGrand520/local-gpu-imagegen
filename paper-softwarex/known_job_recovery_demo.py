"""CPU fixture walkthrough of retained-job recovery; no GPU or real ComfyUI.

Reuses source-snapshot fixtures. Engine and HTTP-adapter checks are separate;
this deliberately does not pretend their combination is a real backend run.
"""
from pathlib import Path
import copy
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from tests.test_asset_run_engine import AssetRunEngineTests, RecoveringTwoStageBackendRunner
from tests.test_comfyui_adapter import ComfyUIAdapterTests
from local_gpu_imagegen.errors import StateError


def main():
    engine_case = AssetRunEngineTests()
    engine_case.setUp()
    try:
        engine = engine_case.engine
        runner = RecoveringTwoStageBackendRunner()
        engine.backend_runner = runner
        run_id = str(engine.start_run(engine_case.two_stage_start_arguments())['run_id'])
        route = engine.get_run({'run_id': run_id})['request']['route']
        args = {
            'run_id': run_id, 'idempotency_key': 'fixture-recovery-key',
            'action': 'initial', 'edit_mode': 'txt2img', 'seed': 42,
            'change_summary': 'Recover the exact retained fixture job.',
            'plan': engine_case.two_stage_plan(route),
        }
        try:
            engine.generate_round(args)
        except StateError as error:
            assert error.code == 'comfyui_job_timed_out'
        else:
            raise AssertionError('Fixture timeout expected')
        before = engine.get_run({'run_id': run_id})
        assert before['state'] == 'unresolved'
        assert before['attempts'][-1]['backend_job']['job_id'] == 'job-two-stage-timeout'
        assert before['recoverable_next_actions'] == ['get_run', 'generate_round:recover']
        assert len(runner.calls) == 1  # Retrieval performs no backend call.
        control = copy.deepcopy(before)  # Defined stop-only policy performs no further action.
        changed = copy.deepcopy(args); changed['idempotency_key'] = 'different-key'
        try:
            engine.generate_round(changed)
        except StateError as error:
            assert error.code == 'backend_job_unresolved'
        else:
            raise AssertionError('Changed key must be rejected')
        assert len(runner.calls) == 1
        result, _ = engine.generate_round(args)
        after = engine.get_run({'run_id': run_id})
        assert result['ok'] is True and after['state'] == 'generated'
        assert runner.calls[-1]['recovery_job_id'] == 'job-two-stage-timeout'
        assert after['rounds'][0]['image']['path']
        image_path = engine_case.output_root / 'runs' / run_id / after['rounds'][0]['image']['path']
        assert image_path.is_file()
        engine_receipt = {
            'before_state': before['state'],
            'retained_backend_job_id': before['attempts'][-1]['backend_job']['job_id'],
            'next_actions': before['recoverable_next_actions'],
            'get_run_backend_calls_added': 0,
            'changed_key_error': 'backend_job_unresolved',
            'recovery_job_id_forwarded': runner.calls[-1]['recovery_job_id'],
            'after_state': after['state'], 'rounds': len(after['rounds']),
            'image_recorded_and_exists': True,
            'stop_only_control_state': control['state'],
            'control_scope': 'Defined no-further-action policy on the same retained manifest; not P-stop Windows/CPU campaign',
        }
    finally:
        engine_case.tearDown()
    adapter_case = ComfyUIAdapterTests()
    adapter_case.setUp()
    try:
        adapter_case.server.requests.clear()
        output = adapter_case.adapter.generate(adapter_case.request(recovery_job_id='prompt-1'))
        paths = [item['path'] for item in adapter_case.server.requests]
        assert paths == ['/history/prompt-1', '/view?filename=result.png&subfolder=&type=output']
        assert output['workflow_job_id'] == 'prompt-1'
        adapter_receipt = {'request_paths': paths, 'prompt_posts': 0, 'workflow_job_id': output['workflow_job_id']}
    finally:
        adapter_case.tearDown()
    print(json.dumps({
        'schema': 'known-job-cpu-walkthrough-v1', 'status': 'PASS',
        'scope': 'Separate engine fixture and real adapter against loopback fake HTTP server',
        'gpu_executed': False, 'real_comfyui_executed': False,
        'fixtures_source': 'dfc8378', 'engine_fixture': engine_receipt,
        'adapter_fixture': adapter_receipt,
        'limits': 'Synthetic images and known job IDs; not missing-ID reconciliation, F03 Windows evidence, or policy superiority',
    }, indent=2))


if __name__ == '__main__':
    main()
