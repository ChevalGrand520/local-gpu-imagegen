"""DRAFT CPU-only matrix driver; syntax checked, NOT integration validated.

Execution is on hold after the M0 novelty review. See refine-logs/M0_M1_GATE_REPORT.md.
Native frozen product sources; no model or GPU access.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.research.cpu_evidence_contract import audit, constructed_checks, digest

SCHEDULES = ('before_intent', 'after_intent_before_entry', 'after_recovery')
FAULTS = ('healthy', 'reject_before_accept', 'unknown_before_accept', 'accepted_response_lost', 'completion_response_lost')


def specs():
    # Healthy controls are first; order is fixed before observations.
    b1 = [('B1', f, s, 'same', 'single') for f in FAULTS for s in SCHEDULES]
    b3 = [('B3-scope', 'accepted_response_lost', s, scope, 'single') for scope in ('same','new') for s in SCHEDULES]
    b3 += [('B3-known', 'completion_response_lost', s, 'same', 'two') for s in SCHEDULES]
    return b1 + b3


def load_product(product_root):
    # Import the selected product before the common driver imports its HTTP fixture.
    sys.path.insert(0, str(product_root))
    sys.path.insert(0, str(product_root / 'scripts'))
    import tests.test_asset_run_engine as fixture_module
    import local_gpu_imagegen.engine as engine_module
    from local_gpu_imagegen.backends.base import BoundedJsonClient
    from local_gpu_imagegen.errors import AssetEngineError, StateError
    from scripts.research.run_paired_fault_matrix import LocalhostJsonServer
    # The archive must really supply the product, not an already-imported current checkout.
    if product_root not in Path(engine_module.__file__).resolve().parents:
        raise RuntimeError('product import escaped frozen source root')
    return fixture_module, BoundedJsonClient, AssetEngineError, StateError, LocalhostJsonServer


class Ledger:
    def __init__(self, case):
        self.operation = case
        self.events = []
        self.snapshots = []
        self.owner = dict(run_id='unassigned', call_id='setup', attempt_id='setup')

    def event(self, kind, owner=None, **fields):
        n=len(self.events)+1
        e=dict(operation_id=self.operation, epoch='cpu-process-1', event_id=f'{self.operation}:e{n}',
               seq=n, monotonic_ns=time.monotonic_ns(), kind=kind, **(owner or self.owner))
        e.update(fields);self.events.append(e)
        return e

    def snapshot(self):
        self.snapshots.append(dict(first_seq=1,last_seq=len(self.events),events=copy.deepcopy(self.events)))

    def close(self):
        self.event('window_closed');self.snapshot()
        return dict(operation_id=self.operation,epoch='cpu-process-1',closed=True,
                    final_seq=len(self.events),snapshots=self.snapshots)


class Worker:
    def __init__(self, modules, ledger, fault, path_kind):
        fm, Client, self.AssetError, self.StateError, Server=modules
        self.ledger=ledger;self.fault=fault;self.path_kind=path_kind
        self.delegate=fm.FakeBackendRunner() if path_kind=='single' else fm.TwoStageBackendRunner()
        self.server=Server(self.post)
        self.Client=Client;self.pending={};self.jobs={};self.attempts=0
        self.submissions=0;self.entries=[];self.recoveries=0;self.injection=False

    def __enter__(self):
        self.server.__enter__();self.client=self.Client(self.server.url,timeout=2.0);return self

    def __exit__(self,*args):self.server.__exit__(*args)

    def __call__(self,request):
        if 'recovery_job_id' in request:
            self.recoveries+=1
            job=self.jobs[request['recovery_job_id']]
            self.ledger.event('known_job_query',job_id=request['recovery_job_id'])
            if 'result' not in job:
                raise self.StateError('comfyui_job_timed_out','Synthetic job still pending.',{'job_id':job['id'],'state':'running'})
            for p,b in job['artifacts'].items():
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            return copy.deepcopy(job['result'])
        self.attempts+=1
        token=f'call-token-{self.attempts}'
        self.pending[token]=(request,copy.deepcopy(self.ledger.owner))
        response=self.client.post_json('/submit',{'request_token':token})
        if self.server.handler_errors:raise RuntimeError(self.server.handler_errors[-1])
        if response.get('rejected'):
            raise self.StateError('backend_request_failed','Explicit synthetic rejection before acceptance.',{'status':503})
        job=self.jobs[response['job_id']]
        callback=request.get('backend_job_callback')
        self.ledger.event('job_id_observed_by_adapter',job_id=job['id'],persisted_callback=callable(callback))
        if callable(callback):callback(job['id'])
        if self.fault=='completion_response_lost' and self.attempts==1:
            self.injection=True
            raise self.StateError('comfyui_job_timed_out','Synthetic completion response unavailable.',{'job_id':job['id'],'state':'running'})
        return copy.deepcopy(job['result'])

    def post(self,body):
        request,owner=self.pending.pop(body['request_token'])
        self.submissions+=1;first=self.submissions==1
        self.ledger.event('post_received',owner)
        if first and self.fault in ('reject_before_accept','unknown_before_accept'):
            self.injection=True;self.ledger.event('not_forwarded',owner)
            return ({'rejected':True},False) if self.fault=='reject_before_accept' else (None,True)
        job_id=f'job-{len(self.jobs)+1}'
        job=dict(id=job_id,request=request,owner=owner)
        self.jobs[job_id]=job;self.ledger.event('accepted',owner,job_id=job_id)
        if first and self.fault=='accepted_response_lost':
            self.injection=True;return None,True
        if not (first and self.fault=='completion_response_lost'):
            self.finish(job)
        return {'job_id':job_id},False

    def finish(self,job):
        if 'result' in job:return
        execution_id=f'execution-{len(self.entries)+1}'
        self.entries.append(execution_id)
        self.ledger.event('execution_start',job['owner'],job_id=job['id'],execution_id=execution_id)
        result=self.delegate(job['request'])
        if self.path_kind=='two':result['workflow_job_id']=job['id']
        paths=set()
        def collect(v):
            if isinstance(v,dict):
                for k,x in v.items():
                    if k=='path' and isinstance(x,str):paths.add(Path(x))
                    else:collect(x)
            elif isinstance(v,list):
                for x in v:collect(x)
        collect(result)
        artifacts={p:p.read_bytes() for p in paths}
        job.update(result=result,artifacts=artifacts)
        self.ledger.event('terminal',job['owner'],job_id=job['id'],execution_id=execution_id,
                          node=None,history_completed=True,artifact_sha256=sorted(hashlib.sha256(b).hexdigest() for b in artifacts.values()))

    def complete_first(self):
        if self.jobs:self.finish(next(iter(self.jobs.values())))


def sanitize(value, root):
    if isinstance(value,dict):return {k:sanitize(v,root) for k,v in value.items()}
    if isinstance(value,list):return [sanitize(v,root) for v in value]
    if isinstance(value,str):return value.replace(str(root),'<fixture>')
    return value


def run_case(modules, strategy, spec):
    block,fault,schedule,scope,path_kind=spec
    case=':'.join((strategy,*spec));ledger=Ledger(case)
    fixture=modules[0].AssetRunEngineTests('runTest');fixture.setUp()
    requests=[];errors=[];entry_calls=[]
    def start():
        if path_kind=='single':
            r=fixture.start(max_rounds=2);rid=r['run_id'];args=fixture.generate_arguments(rid,key='logical-operation',seed=42,max_rounds=2)
        else:
            r=fixture.engine.start_run(fixture.two_stage_start_arguments());rid=r['run_id']
            route=fixture.engine.get_run({'run_id':rid})['request']['route']
            args=dict(run_id=rid,idempotency_key='logical-operation',action='initial',edit_mode='txt2img',seed=42,
                      change_summary='Controlled CPU operation.',plan=fixture.two_stage_plan(route))
        return rid,args
    def invoke(args, number):
        ledger.owner=dict(run_id=args['run_id'],call_id=f'call-{number}',attempt_id=f'attempt-{number}')
        entry_calls.append(dict(entry='AssetRunEngine.generate_round',run_id=args['run_id'],call=number))
        requests.append(copy.deepcopy(args));ledger.event('product_entry')
        try:fixture.engine.generate_round(args);error=None
        except modules[2] as e:error=dict(code=e.code,details=e.details)
        errors.append(error);ledger.event('product_return',error=error)
        return error
    try:
        with Worker(modules,ledger,fault,path_kind) as worker:
            fixture.engine.backend_runner=worker
            original,args=start();invoke(args,1)
            first=fixture.engine.get_run({'run_id':original});ledger.snapshot()
            has_pending=any('result' not in j for j in worker.jobs.values())
            if schedule=='before_intent':worker.complete_first()
            recovery_run=original;decision='not_needed'
            if fault!='healthy':
                ledger.event('recovery_intent')
                if schedule=='after_intent_before_entry':worker.complete_first()
                if scope=='new':recovery_run,args=start()
                manifest=fixture.engine.get_run({'run_id':recovery_run})
                latest=(manifest.get('attempts') or [{}])[-1]
                if strategy=='P-stop' and latest.get('submission_outcome')=='unknown':
                    decision='policy_stop';ledger.event('policy_stop')
                else:
                    decision='generate_round';invoke(args,2)
            worker.complete_first()
            final=fixture.engine.get_run({'run_id':original})
            recovered=fixture.engine.get_run({'run_id':recovery_run})
            evidence=ledger.close();judgment=audit(evidence)
            semantic=[]
            for request in requests:
                semantic.append(digest({k:v for k,v in request.items() if k not in ('run_id','idempotency_key')}))
            result=dict(case_id=case,block=block,strategy=strategy,fault=fault,schedule=schedule,scope=scope,path_kind=path_kind,
                        schedule_has_pending_job=has_pending,original_run_id=original,recovery_run_id=recovery_run,
                        original_completed=final.get('state')=='generated',recovery_run_completed=recovered.get('state')=='generated',
                        first_state=first.get('state'),final_state=final.get('state'),errors=errors,decision=decision,
                        product_entries=entry_calls,semantic_input_sha256=semantic,
                        transport_payload_sha256=[digest(x) for x in worker.server.requests],
                        injection_confirmed=worker.injection,post_count=worker.submissions,
                        worker_entry_ids=worker.entries,worker_entry_count=len(worker.entries),known_job_queries=worker.recoveries,
                        evidence=evidence,audit=judgment,
                        manifests=dict(first=first,original_final=final,recovery_final=recovered))
            return sanitize(result,Path(fixture.temporary_directory.name))
    finally:fixture.tearDown()


def main():
    p=argparse.ArgumentParser();p.add_argument('--product-root',type=Path,required=True)
    p.add_argument('--strategy',choices=['P-retry','P-stop','P-guard'],required=True)
    p.add_argument('--source-sha',required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():raise FileExistsError(args.output)
    modules=load_product(args.product_root.resolve());checks=constructed_checks()
    source_files={str(f.relative_to(args.product_root)):hashlib.sha256(f.read_bytes()).hexdigest()
                  for f in sorted((args.product_root/'scripts/local_gpu_imagegen').rglob('*.py'))}
    result=dict(protocol='regular-cpu-gate-v1',source_sha=args.source_sha,strategy=args.strategy,
                python=platform.python_version(),product_files_sha256=source_files,
                fixture_sha256=hashlib.sha256(Path(modules[0].__file__).read_bytes()).hexdigest(),
                harness_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                contract_sha256=hashlib.sha256((ROOT/'scripts/research/cpu_evidence_contract.py').read_bytes()).hexdigest(),
                b0=checks,cases=[],status='running',scope='synthetic CPU worker; not GPU or deployment rates')
    started=time.monotonic()
    try:
        if not all(c['passed'] for c in checks):raise RuntimeError('B0 audit failed')
        for spec in specs():
            if time.monotonic()-started>600:raise RuntimeError('strategy runtime budget reached')
            case=run_case(modules,args.strategy,spec);result['cases'].append(case)
            if case['audit']['state']!='verified' or case['audit']['executions']!=case['worker_entry_count']:
                raise RuntimeError('CPU evidence gate failed: '+case['case_id'])
            if case['fault']=='healthy' and (not case['original_completed'] or case['post_count']!=1 or case['worker_entry_count']!=1):
                raise RuntimeError('healthy control failed: '+case['case_id'])
            if case['fault']!='healthy' and not case['injection_confirmed']:
                raise RuntimeError('fault not confirmed: '+case['case_id'])
        result['status']='complete'
    except Exception as e:
        result['status']='stopped';result['stop_reason']=str(e)
        raise
    finally:
        result['elapsed_seconds']=time.monotonic()-started
        encoded=json.dumps(result,ensure_ascii=True,indent=2,sort_keys=True)+'\n'
        if len(encoded.encode())>1024**3:raise RuntimeError('evidence size budget exceeded')
        with args.output.open('x') as f:f.write(encoded)
        print(f"{args.strategy}: {result['status']}, {len(result['cases'])}/24 cases; {args.output.name}")


if __name__=='__main__':main()
