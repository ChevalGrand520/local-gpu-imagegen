"""Verify retained records and produce paper tables; never invokes a backend."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'paper/evidence'
def load(p): return json.loads(p.read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
w=load(OUT/'windows-audit.json')
assert w['report_sha256']=='5c946b67f840876fa4a6a44bf39c7cdf4604d655fdc0197123acd675cebc55f2'
assert w['jsonl_rows']==4
ids=[];windows=[]
for c in w['cases']:
 assert c['report_equals_jsonl_case']
 n=2 if c['case_id'].endswith('F02') else 1
 assert c['submissions']==c['executions']==len(c['bindings'])==len(c['calls'])==n
 assert c['classifications']['oracle_evaluable']==1
 assert [x['state'] for x in c['calls']]==(['unresolved','resolved'] if n==2 else ['resolved'])
 assert len(c['receipts'])==n
 assert sum(bool(x['response_dropped']) for x in c['receipts'])==(n==2)
 for b in c['bindings']:
  assert b['history_completed'] and b['terminal_event']=='executing'
  assert b['finished_at']>=b['started_at'];ids.append(b['execution_instance_id'])
 for call in c['calls']:
  assert call['exit_code']==0 and not call['timed_out']
  assert all(x['matches_current_output_bytes'] for x in call['artifact_checks'])
 # Receipt timestamps are observer-side; ordering only, not GPU duration.
 if n==2:assert c['receipts'][1]['received_at']>c['bindings'][0]['finished_at']
 windows.append({'case':c['case_id'],'submissions':n,'retained_execution_bindings':n,'call_states':[x['state'] for x in c['calls']]})
assert len(ids)==len(set(ids))==6
base=ROOT/'docs/research/runs'
raw={k:load(base/f'paired-v2-{k}.json') for k in ['b2','w3']}
comparison=load(base/'paired-v2-comparison.json');cpu=[]
for pair in comparison['pairs']:
 row={'case':pair['case_id']}
 for k in ['b2','w3']:
  case=next(c for c in raw[k]['cases'] if c['case_id']==pair['case_id'])
  ev=case['oracle_state']['events'];starts=[e['execution_instance_id'] for e in ev if e['event']=='execution_started'];ends=[e['execution_instance_id'] for e in ev if e['event']=='execution_finished']
  assert len(starts)==len(set(starts))==case['oracle_execution_count']==pair[k+'_execution_count']
  assert set(starts)==set(ends)
  assert sum(e['event']=='request_received' for e in ev)==case['backend_submission_count']==pair[k+'_submission_count']
  row[k]={'submissions':case['backend_submission_count'],'executions':len(starts),'completion':pair[k+'_valid_completion'],'recovery':pair[k+'_recovery_state']}
 cpu.append(row)
result={'scope':'read-only reanalysis of existing evidence; no new experiment','windows_cases':windows,'unique_windows_binding_ids':len(set(ids)),'artifact_byte_checks':4,'raw_windows_event_reconstruction':'unavailable: retained export has bindings/event_counts, not raw events/history snapshots','cpu_cases':cpu,'input_hashes':{str(p.relative_to(ROOT)):digest(p) for p in [OUT/'windows-audit.json',base/'paired-v2-b2.json',base/'paired-v2-w3.json',base/'paired-v2-comparison.json']}}
(OUT/'audit-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 4 Windows records, 6 unique retained bindings, 4 output-byte matches, 12 synthetic event traces')
