"""Offline audit of private Windows capture; stdout contains no raw identifiers.

Hashes establish retained-byte consistency, not independent authenticity or
completeness of events not received by the observer. Never calls a backend.
"""
import argparse
import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(report_path, capture):
    report = json.loads(report_path.read_text())
    require(report['protocol_version'] in ('same-run-guard-v1', 'same-run-guard-v2'), 'wrong protocol')
    require(report['preflight']['status'] == 'PASS', 'preflight did not pass')
    for name, key in [('preflight.json', 'private_capture_sha256'),
                      ('configuration.json', 'private_configuration_sha256')]:
        require(digest(capture / name) == report['preflight'][key], 'root capture hash mismatch')
    results = []
    for case in report['records']:
        root = capture / case['case_id']
        for name, expected in case['private_capture_sha256'].items():
            require(digest(root / name) == expected, 'case capture hash mismatch')
        session = json.loads((root / 'session.json').read_text())
        args = session['generate_arguments']
        arguments_hash = sha256(json.dumps(args, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        require(arguments_hash == session['generate_arguments_sha256'], 'session argument hash mismatch')
        run_hash = sha256(session['run_id'].encode()).hexdigest()
        for index, call in enumerate(case['product_calls'], 1):
            require(call['generate_arguments_sha256'] == arguments_hash and call['run_id_sha256'] == run_hash,
                    'run or argument identity mismatch')
            for phase in ('before', 'after'):
                require(digest(root / f'call-{index}-{phase}.json') == call[f'manifest_{phase}_sha256'],
                        'manifest hash mismatch')
        transport = json.loads((root / 'oracle-transport-final.json').read_text())
        require(transport['retained'] is True, 'raw retention disabled')
        groups = {}
        types = Counter()
        for index, item in enumerate(transport['websocket_messages'], 1):
            require(item['sequence'] == index, 'WS sequence gap')
            body = base64.b64decode(item['body_base64'], validate=True)
            require(sha256(body).hexdigest() == item['body_sha256'], 'WS payload hash mismatch')
            event = json.loads(body)
            types[event['type']] += 1
            data = event.get('data', {})
            pid = data.get('prompt_id')
            if isinstance(pid, str):
                groups.setdefault(pid, []).append(event)
        histories = {}
        for index, item in enumerate(transport['history_responses'], 1):
            require(item['sequence'] == index and item['http_status'] == 200, 'history sequence/status mismatch')
            body = base64.b64decode(item['body_base64'], validate=True)
            require(sha256(body).hexdigest() == item['body_sha256'], 'history payload hash mismatch')
            histories[item['prompt_id']] = json.loads(body)[item['prompt_id']]
        receipts = json.loads((root / 'proxy-receipts.json').read_text())
        posts = [r for r in receipts if r['method'] == 'POST' and r['path'] == '/prompt']
        require(len(posts) == case['proxy_prompt_count'] == 1, 'unexpected POST count')
        pid = posts[0]['accepted_job_id']
        events = groups[pid]
        starts = sum(e['type'] == 'execution_start' for e in events)
        terminals = sum(e['type'] == 'executing' and e['data'].get('node', 'missing') is None for e in events)
        require(starts == terminals == 1, 'start/terminal count mismatch')
        require(histories[pid]['status']['status_str'] == 'success', 'history not successful')
        # Explicit separators avoid interpreting the final component as an octal escape.
        expected_id = 'execution:' + sha256((transport['backend_boot_identity'] + '\0' + pid + '\0' + '1').encode()).hexdigest()
        require(case['oracle']['bindings'][0]['execution_instance_id'] == expected_id,
                'binding does not reconstruct from retained raw start')
        last = json.loads((root / f"call-{len(case['product_calls'])}-after.json").read_text())
        attempts = last['attempts']
        second_error = case['product_calls'][-1].get('client_error_code') if len(case['product_calls']) == 2 else None
        if case['fault_mode'] == 'F02':
            require(posts[0]['response_dropped'] is True, 'fault injection missing')
            require(last['state'] == 'unresolved' and attempts[-1]['submission_outcome'] == 'unknown'
                    and attempts[-1].get('backend_job') is None, 'original ambiguity lost')
            require(case['submission_guard_observed'] is (second_error == 'submission_outcome_unknown'),
                    'guard result attributed to wrong rejection')
        results.append({'case': case['case_id'], 'product_calls': len(case['product_calls']),
                        'submissions': len(posts), 'raw_starts': starts, 'raw_terminal_node_null': terminals,
                        'retained_bindings': len(case['oracle']['bindings']),
                        'websocket_messages': len(transport['websocket_messages']),
                        'history_responses': len(transport['history_responses']),
                        'cached_events': types['execution_cached'], 'progress_events': types['progress'],
                        'call_states': [c['reported_state'] for c in case['product_calls']],
                        'second_error': second_error, 'original_run_state': last['state'],
                        'guard_observed': case['submission_guard_observed']})
    return {'audit_status': 'PASS', 'campaign_status': report['status'],
            'scope': 'retained-byte and event-binding consistency; no authenticity or completeness guarantee',
            'report_sha256': digest(report_path), 'cases': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('capture', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.report, args.capture), sort_keys=True, indent=2))
