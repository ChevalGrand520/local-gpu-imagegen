"""Fixed CPU process/fault traces with real pinned upstream MCP tool handlers."""
from __future__ import annotations

import argparse
import copy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit

from upstream_smoke import PIN, write_tool_harness

HERE = Path(__file__).resolve().parent
MODES = ('native','stop','full','minimal')
CASES = ('normal','before_send','response_loss','before_binding','after_binding',
         'history_failure','changed_key','changed_seed')


class Fixture:
    def __init__(self):
        self.events = []
        self.jobs = {}
        self.lock = threading.Lock()
        self.post_fault = ''
        self.fail_next_history = False
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def respond(self, value, status=200, raw=False):
                data = value if raw else json.dumps(value).encode()
                self.send_response(status)
                self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_POST(self):
                path = urlsplit(self.path).path
                value = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                if path != '/prompt':
                    self.respond({},404);return
                with fixture.lock:
                    pid = f'fixture-job-{len(fixture.jobs)+1}'
                    fixture.jobs[pid] = copy.deepcopy(value['prompt'])
                    fixture.events.append({'method':'POST','path':path,'accepted_id':pid,
                                           'graph':copy.deepcopy(value['prompt'])})
                    fault = fixture.post_fault
                    fixture.post_fault = ''
                if fault == 'response_loss':
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                self.respond({'prompt_id':pid,'number':0,'node_errors':{}})

            def do_GET(self):
                path = urlsplit(self.path).path.removeprefix('/api')
                with fixture.lock:
                    fixture.events.append({'method':'GET','path':path})
                    jobs = copy.deepcopy(fixture.jobs)
                    fail = path.startswith('/history/') and fixture.fail_next_history
                    if fail:
                        fixture.fail_next_history = False
                if fail:
                    self.respond(b'{',raw=True);return
                if path.startswith('/history/'):
                    pid = path.rsplit('/',1)[1]
                    value = {} if pid not in jobs else {pid:{
                        'prompt':[0,pid,jobs[pid],{},['1']],
                        'outputs':{'1':{'images':[{'filename':pid+'.png','subfolder':'','type':'output'}]}},
                        'status':{'status_str':'success','completed':True,'messages':[]}}}
                elif path == '/object_info':
                    value = {
                        'SaveImage':{'input':{'required':{'images':['IMAGE'],
                                      'filename_prefix':['STRING',{'default':'test'}]}},
                                     'output':[],'output_node':True},
                        'EmptyLatentImage':{'input':{'required':{'seed':['INT',{'default':42}]}},
                                            'output':['LATENT']}}
                elif path == '/queue':
                    value = {'queue_running':[],'queue_pending':[]}
                elif path == '/system_stats':
                    value = {'system':{'comfyui_version':'CPU-FAKE'},'devices':[]}
                else:
                    self.respond({},404);return
                self.respond(value)

        self.server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown();self.server.server_close();self.thread.join()


def worker(config_path, env, mode, action='submit', fault=''):
    command = [sys.executable,str(HERE/'fault_worker.py'),str(config_path),mode,action,fault]
    # Owned process group includes Node child if a deadline is exceeded.
    child = subprocess.Popen(command,env=env,text=True,stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,start_new_session=True)
    try:
        out, err = child.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid,signal.SIGKILL)
        child.communicate()
        raise RuntimeError('Worker deadline exhausted; owned process group killed')
    result = json.loads(out) if out.strip() else None
    return {'exit':child.returncode,'reply':result}


def run_case(upstream, root, mode, case):
    fixture = Fixture()
    try:
        root.mkdir()
        harness = root/'upstream-tools.mjs';write_tool_harness(harness)
        env_file=root/'empty.env';env_file.write_text('')
        endpoint=f'http://127.0.0.1:{fixture.server.server_port}'
        env = dict(os.environ)
        env.update({'COMFYUI_URL':endpoint,'COMFYUI_MCP_ENV_FILE':str(env_file),
                    'COMFYUI_MCP_DATA_DIR':str(root/'upstream-state'),
                    'COMFYUI_MCP_LOCAL_TARGET_FILE':str(root/'target.json'),
                    'COMFYUI_MCP_PANEL_AUTOINSTALL':'0','COMFYUI_MCP_AUTOUPDATE':'0'})
        for name in ('COMFYUI_API_KEY','COMFY_API_KEY','COMFYUI_PATH',
                     'COMFYUI_AUTH_TOKEN','CF_ACCESS_CLIENT_ID','CF_ACCESS_CLIENT_SECRET'):
            env.pop(name,None)
        graph = {'1':{'class_type':'SaveImage','inputs':{'images':['2',0],'filename_prefix':'cpu'}},
                 '2':{'class_type':'EmptyLatentImage','inputs':{'seed':42}}}
        config={'database':str(root/'runs.sqlite'),
                'command':[shutil.which('node'),str(harness),str(upstream)],
                'endpoint':endpoint,'graph':graph}
        config_path=root/'config.json';config_path.write_text(json.dumps(config))
        if case == 'response_loss':fixture.post_fault='response_loss'
        crash=case if case in ('before_send','before_binding','after_binding') else ''
        first=worker(config_path,env,mode,fault=crash)
        steps=[first]
        if case == 'history_failure':
            assert first['exit']==0, first
            first_result=first['reply']['result']
            if mode=='native':
                # Controller uses only returned caller data, NOT fixture oracle ID.
                content=json.loads(first_result['content'][0]['text'])
                config['known_id_from_successful_receipt']=content['prompt_id']
                config_path.write_text(json.dumps(config))
            fixture.fail_next_history=True
            steps.append(worker(config_path,env,mode,'history'))
            assert steps[-1]['exit']==2, steps[-1]
            steps.append(worker(config_path,env,mode,'history'))
            assert steps[-1]['exit']==0, steps[-1]
        else:
            action=case if case in ('changed_key','changed_seed') else 'submit'
            steps.append(worker(config_path,env,mode,action))
            if mode in ('stop','minimal') and case in ('normal','after_binding'):
                steps.append(worker(config_path,env,mode,'history'))
        posts=[e for e in fixture.events if e['method']=='POST']
        history=[e['path'].rsplit('/',1)[1] for e in fixture.events if e['path'].startswith('/history/')]
        if case in ('before_send','before_binding','after_binding'):
            assert first['exit']=={'before_send':71,'before_binding':72,'after_binding':73}[case], first
        elif case=='response_loss':
            assert first['exit']==2, first
        else:
            assert first['exit']==0, first
        if mode=='native':
            expected=1 if case in ('before_send','history_failure') else 2
            assert steps[-1]['exit']==0, steps[-1]
        else:
            expected=0 if case=='before_send' else 1
            should_block=case in ('before_send','before_binding','response_loss','changed_key','changed_seed')
            assert steps[1]['exit']==(2 if should_block else (2 if case=='history_failure' else 0)), steps
            if should_block:
                error=steps[1]['reply']['error']
                assert ('conflict' in error if case.startswith('changed_') else 'no automatic resubmission' in error), error
        assert len(posts)==expected,(mode,case,posts)
        recovered=False
        if case=='history_failure' or (mode!='native' and case in ('normal','after_binding')):
            assert history and all(pid in fixture.jobs for pid in history), history
            text=json.dumps(steps[-1]['reply'])
            assert history[-1]+'.png' in text,text
            recovered=True
        if case!='changed_seed':
            assert all(e['graph']==graph for e in posts)
        journal_state=None
        if mode!='native':
            with sqlite3.connect(root/'runs.sqlite') as db:
                if mode=='minimal':
                    pid=db.execute('SELECT job FROM operations').fetchone()[0]
                    row=('submitting' if pid is None else 'known_job',pid)
                else:
                    row=db.execute('SELECT state,prompt_id FROM runs').fetchone()
                journal_state={'state':row[0],'prompt_id':row[1]}
                if case in ('before_send','before_binding','response_loss'):
                    assert row==('submitting',None),row
        return {'mode':mode,'case':case,'steps':steps,'prompt_posts':len(posts),
                'synthetic_accepted_ids':list(fixture.jobs),'exact_history_ids':history,
                'synthetic_output_reference_retrieved':recovered,'journal':journal_state,
                'http_trace':fixture.events}
    finally:
        fixture.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('upstream',type=Path)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    upstream=args.upstream.resolve()
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip()
    assert sha==PIN
    assert not subprocess.check_output(['git','diff','HEAD','--','src'],cwd=upstream)
    if os.name!='posix':raise RuntimeError('Campaign supervisor validated only on POSIX')
    start=time.monotonic();rows=[]
    receipt={'status':'RUNNING','scope':'CPU fixed traces; real upstream tools, fake HTTP',
             'upstream_revision':sha,'gpu_executed':False,'real_comfyui':False,
             'human_study':False,'cases':rows}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='comfy-mcp-fault-') as td:
            for case in CASES:
                for mode in MODES:
                    if time.monotonic()-start>300:raise RuntimeError('Campaign budget exhausted')
                    row=run_case(upstream,Path(td)/f'{case}-{mode}',mode,case)
                    rows.append(row)
                    print(f'{case}/{mode}: POST={row["prompt_posts"]}, history={len(row["exact_history_ids"])}',flush=True)
        receipt['status']='PASS'
    except BaseException as exc:
        receipt['status']='FAIL';receipt['error']=f'{type(exc).__name__}: {exc}'
        raise
    finally:
        receipt['wall_seconds']=round(time.monotonic()-start,3)
        receipt['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                 [HERE/'bridge.py',HERE/'minimal_baseline.py',HERE/'fault_worker.py',HERE/'fault_campaign.py',HERE/'upstream_smoke.py']}
        args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
