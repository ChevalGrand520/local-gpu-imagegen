"""Run pinned upstream MCP tool handlers against fake HTTP. No ComfyUI/GPU.

Uses an SDK stdio harness rather than upstream boot's panel/install/download
services. The actual enqueue_workflow and get_history handlers are unchanged.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bridge', HERE/'bridge.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
PIN = '6996d06ff511dd7b3b05adf89716e7667df2c1b9'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('upstream', type=Path)
    p.add_argument('--receipt', type=Path, required=True)
    args = p.parse_args()
    upstream = args.upstream.resolve()
    sha = subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip()
    if sha != PIN or subprocess.check_output(['git','diff','HEAD','--','src'],cwd=upstream):
        raise RuntimeError('Pinned, unchanged upstream src required')
    events = []
    graph = {'1': {'class_type':'SaveImage','inputs':{'filename_prefix':'cpu-fixture','images':['2',0]}}}
    fault = {'mode':''}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            events.append({'method':'GET','path':self.path})
            path = self.path.removeprefix('/api')
            if path.startswith('/history'):
                value = {'fixture-job-1': {'prompt':[0,'fixture-job-1',graph,{},['1']],
                         'outputs':{'1':{'images':[{'filename':'fixture.png','subfolder':'','type':'output'}]}},
                         'status':{'status_str':'success','completed':True,'messages':[]}}}
            elif path.startswith('/object_info'):
                value = {'SaveImage':{'input':{'required':{}},'output':[],'category':'image','output_node':True}}
            elif path.startswith('/system_stats'):
                value = {'system':{'comfyui_version':'CPU-FAKE'},'devices':[]}
            elif path.startswith('/queue'):
                value = {'queue_running':[],'queue_pending':[]}
            else:
                value = {}
            self.answer(value)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            events.append({'method':'POST','path':self.path,'body':body})
            if fault['mode'] == 'bad_json':
                self.send_response(200);self.end_headers();self.wfile.write(b'{')
                return
            self.answer({'prompt_id':'fixture-job-1','number':0,'node_errors':{}})

        def answer(self, value):
            data = json.dumps(value).encode()
            self.send_response(200);self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

    server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread = threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    old_env = dict(os.environ)
    records = []
    try:
        with tempfile.TemporaryDirectory(prefix='comfyui-mcp-smoke-') as td:
            tmp = Path(td)
            (tmp/'empty.env').write_text('')
            harness = tmp/'harness.mjs'
            harness.write_text('''import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const root=process.argv[2];
const require=createRequire(root+'/package.json');
const {McpServer}=await import(pathToFileURL(require.resolve('@modelcontextprotocol/sdk/server/mcp.js')));
const {StdioServerTransport}=await import(pathToFileURL(require.resolve('@modelcontextprotocol/sdk/server/stdio.js')));
const {registerWorkflowExecuteTools}=await import(pathToFileURL(root+'/dist/tools/workflow-execute.js'));
const {registerDiagnosticsTools}=await import(pathToFileURL(root+'/dist/tools/diagnostics.js'));
const server=new McpServer({name:'upstream-tool-harness',version:'0.52.206'});
registerWorkflowExecuteTools(server);registerDiagnosticsTools(server);
await server.connect(new StdioServerTransport());
''')
            endpoint = f'http://127.0.0.1:{server.server_port}'
            os.environ.update({'COMFYUI_URL':endpoint,'COMFYUI_MCP_ENV_FILE':str(tmp/'empty.env'),
                               'COMFYUI_MCP_DATA_DIR':str(tmp/'data'),
                               'COMFYUI_MCP_LOCAL_TARGET_FILE':str(tmp/'target.json'),
                               'COMFYUI_MCP_PANEL_AUTOINSTALL':'0','COMFYUI_MCP_AUTOUPDATE':'0'})
            # No cloud credentials in this local CPU harness.
            for name in ['COMFYUI_API_KEY','COMFY_API_KEY','COMFYUI_PATH']:
                os.environ.pop(name,None)
            command = [shutil.which('node'),str(harness),str(upstream)]
            for mode in ['native','stop','full']:
                start = len(events)
                client = b.DurableClient(tmp/f'{mode}.sqlite',command,endpoint,mode=mode)
                try:
                    client.submit('run','key',graph)
                finally:
                    client.close()
                client = b.DurableClient(tmp/f'{mode}.sqlite',command,endpoint,mode=mode)
                try:
                    reply = client.submit('run','key',graph)
                    if mode == 'stop':
                        reply = client.read_history('run')
                    if mode != 'native':
                        assert 'fixture.png' in json.dumps(reply), reply
                finally:
                    client.close()
                scoped = events[start:]
                posts = [x for x in scoped if x['method']=='POST']
                assert len(posts) == (2 if mode=='native' else 1), scoped
                assert all(x['body']['prompt']==graph for x in posts)
                history_reads = sum(x['path'].split('?',1)[0].removeprefix('/api')=='/history/fixture-job-1' for x in scoped)
                if mode != 'native':
                    assert history_reads >= 1, scoped
                records.append({'mode':mode,'prompt_posts':len(posts),
                                'exact_history_reads':history_reads,
                                'http_paths':[x['path'] for x in scoped],
                                'scope':'CPU fake HTTP; stop uses explicit history, full same-key history'})
            fault['mode']='bad_json'
            start=len(events)
            client=b.DurableClient(tmp/'unknown.sqlite',command,endpoint)
            try:
                try:
                    client.submit('run','key',graph)
                except b.BridgeError:
                    pass
                else:
                    raise AssertionError('Expected actual upstream ENQUEUE_UNVERIFIED')
            finally:
                client.close()
            client=b.DurableClient(tmp/'unknown.sqlite',command,endpoint)
            try:
                try:
                    client.submit('run','key',graph)
                except b.BridgeError as exc:
                    assert 'no automatic resubmission' in str(exc)
                else:
                    raise AssertionError('Expected durable block')
            finally:
                client.close()
            assert sum(x['method']=='POST' for x in events[start:])==1
            records.append({'case':'upstream-accepted-http-malformed-json','prompt_posts':1,
                            'reentry':'blocked','backend_acceptance':'synthetic fixture only'})
        receipt={'status':'PASS','upstream_revision':sha,'upstream_version':'0.52.206',
                 'real_upstream_tool_handlers':True,'full_upstream_boot':False,
                 'real_comfyui':False,'gpu_executed':False,'cases':records,
                 'limits':'No real generation, artifact download, completion proof, user benefit or native retry policy claim.'}
        args.receipt.parent.mkdir(parents=True,exist_ok=True)
        args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt,indent=2))
    finally:
        os.environ.clear();os.environ.update(old_env)
        server.shutdown();server.server_close();thread.join()


if __name__=='__main__':
    main()
