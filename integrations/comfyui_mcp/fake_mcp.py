"""CPU-only MCP boundary fixture, NOT ComfyUI or the upstream implementation."""
import json
import os
from pathlib import Path
import sys

for line in sys.stdin:
    request = json.loads(line)
    if 'id' not in request:
        continue
    method = request['method']
    if method == 'initialize':
        result = {'protocolVersion': '2024-11-05', 'capabilities': {},
                  'serverInfo': {'name': 'cpu-fixture', 'version': '1'}}
    elif method == 'tools/list':
        result = {'tools': []}
    else:
        args = request['params']
        event_file = Path(os.environ['BRIDGE_TEST_EVENTS'])
        with event_file.open('a') as f:
            f.write(json.dumps(args)+'\n')
        fault = os.environ.get('BRIDGE_TEST_FAULT', '')
        if args['name'] == 'enqueue_workflow':
            if fault == 'crash':
                os._exit(72)
            if fault == 'is_error':
                result = {'isError': True, 'content': [{'type': 'text', 'text': 'unknown'}]}
            elif fault == 'no_id':
                result = {'content': [{'type': 'text', 'text': '{"status":"unknown"}'}]}
            else:
                result = {'content': [{'type': 'text', 'text': '{"prompt_id":"fixture-job-1"}'}]}
        else:
            if fault == 'history_error':
                result = {'isError': True, 'content': []}
            else:
                result = {'content': [{'type': 'text', 'text': 'No history found for prompt fixture-job-1.'}]}
    print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)
