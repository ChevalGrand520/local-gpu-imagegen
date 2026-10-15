"""Recompute HTTP fixture counts and cross-step outcomes from a campaign receipt.

Deterministic consistency check by the same author/tooling; not independent
execution authentication or independent peer review.
"""
import argparse
import hashlib
import json
from pathlib import Path

CASES = {'normal','before_send','response_loss','before_binding','after_binding',
         'history_failure','changed_key','changed_seed'}
MODES = {'native','stop','full'}


def audit(receipt):
    assert receipt['status']=='PASS'
    assert receipt['real_comfyui'] is False and receipt['gpu_executed'] is False
    assert receipt['human_study'] is False
    rows=receipt['cases']
    identities=[(r['case'],r['mode']) for r in rows]
    assert len(identities)==24 and set(identities)=={(c,m) for c in CASES for m in MODES}
    summary=[]
    for row in rows:
        case,mode=row['case'],row['mode']
        posts=[event for event in row['http_trace'] if event['method']=='POST']
        history=[event['path'].rsplit('/',1)[1] for event in row['http_trace']
                 if event['method']=='GET' and event['path'].startswith('/history/')]
        assert len(posts)==row['prompt_posts']
        assert [p['accepted_id'] for p in posts]==row['synthetic_accepted_ids']
        assert len(set(p['accepted_id'] for p in posts))==len(posts)
        assert history==row['exact_history_ids']
        assert all(pid in row['synthetic_accepted_ids'] for pid in history)
        expected = (1 if case in ('before_send','history_failure') else 2) if mode=='native' else (0 if case=='before_send' else 1)
        assert len(posts)==expected
        steps=row['steps']
        crash={'before_send':71,'before_binding':72,'after_binding':73}
        assert steps[0]['exit']==crash.get(case,2 if case=='response_loss' else 0)
        if mode!='native' and case in ('before_send','before_binding','response_loss'):
            assert row['journal']=={'state':'submitting','prompt_id':None}
            assert steps[1]['exit']==2 and not history
            assert 'no automatic resubmission' in steps[1]['reply']['error']
        if mode!='native' and case.startswith('changed_'):
            assert steps[1]['exit']==2 and 'conflict' in steps[1]['reply']['error']
            assert not history
        if case=='changed_seed' and mode=='native':
            old=posts[0]['graph'];new=posts[1]['graph']
            assert old['2']['inputs']['seed']==42 and new['2']['inputs']['seed']==43
        else:
            assert all(p['graph']['2']['inputs']['seed']==42 for p in posts)
        if row['synthetic_output_reference_retrieved']:
            text=json.dumps(steps[-1]['reply'])
            assert history[-1]+'.png' in text
            assert steps[-1]['exit']==0
        if case=='history_failure':
            assert [s['exit'] for s in steps]==[0,2,0]
            assert len(history)==2 and len(posts)==1
        summary.append({'case':case,'mode':mode,'post_count':len(posts),
                        'history_reads':len(history),'synthetic_output_reference':row['synthetic_output_reference_retrieved']})
    for case in CASES:
        stop=next(r for r in summary if r['case']==case and r['mode']=='stop')
        full=next(r for r in summary if r['case']==case and r['mode']=='full')
        assert {k:v for k,v in stop.items() if k!='mode'}=={k:v for k,v in full.items() if k!='mode'}
    return {'status':'RECEIPT_CONSISTENCY_PASS','cases_checked':len(rows),
            'stop_full_equal_in_compared_fields':True,'summary':summary,
            'scope':'Synthetic HTTP receipt recomputation; not independent authentication or real execution'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=audit(json.loads(args.receipt.read_text()))
    report['receipt_sha256']=hashlib.sha256(args.receipt.read_bytes()).hexdigest()
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='summary'},indent=2))


if __name__=='__main__':main()
