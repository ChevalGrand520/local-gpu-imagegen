"""Subprocess worker for CPU fault experiments; never used by product code."""
import json
import os
from pathlib import Path
import sys

import bridge as b


def main():
    config = json.loads(Path(sys.argv[1]).read_text())
    mode, action, fault = sys.argv[2:5]
    client = b.DurableClient(config['database'],config['command'],config['endpoint'],mode=mode,timeout=8)
    graph = config['graph']
    key = 'key'
    if action == 'changed_key':
        key = 'different-key'
    if action == 'changed_seed':
        graph['2']['inputs']['seed'] += 1
    original_call = client._call
    if fault == 'before_send':
        def crash_before_call(*args):
            os._exit(71)
        client._call = crash_before_call
    elif fault == 'before_binding':
        # Both policies crash AFTER receiving the actual upstream tool result,
        # before native return or durable ID binding. Exit after owned child cleanup.
        def crash_after_reply(*args):
            original_call(*args)
            os._exit(72)
        client._call = crash_after_reply
    try:
        if action == 'history':
            if mode == 'native':
                prompt_id = config['known_id_from_successful_receipt']
                value = client._call('get_history',{'action':'list','prompt_id':prompt_id})
            else:
                value = client.read_history('run')
        elif action == 'inspect':
            value = client.inspect('run')
        else:
            value = client.submit('run',key,graph)
        if fault == 'after_binding':
            os._exit(73)
        print(json.dumps({'ok':True,'result':value}),flush=True)
    except Exception as exc:
        print(json.dumps({'ok':False,'error_type':type(exc).__name__,'error':str(exc)}),flush=True)
        sys.exit(2)
    finally:
        client.close()


if __name__ == '__main__':
    main()
