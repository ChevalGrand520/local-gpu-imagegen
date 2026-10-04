"""Offline, private Windows capture conversion; no backend or artifact reads.

Only a redacted interpretation summary is public. Full records retain source
fields in a user-supplied private directory. No artifact validator is invented.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper.scripts.audit_same_run_capture import audit
from scripts.research.export_records import export_record

VERSION = 'windows-capture-conversion-v1'


def convert(report: Path, capture: Path):
    checked = audit(report, capture)
    private, summaries = [], []
    for case in checked['cases']:
        root = capture / case['case']
        manifest_path = root / f"call-{case['product_calls']}-after.json"
        manifest = json.loads(manifest_path.read_text())
        decision = json.loads((root / 'oracle-snapshot-1.json').read_text())['decision']
        bindings = decision['bindings']
        if len(bindings) != 1 or not bindings[0]['history_completed']:
            raise ValueError('conversion requires exactly one audited completed binding')
        oracle = {'execution_state': 'succeeded', 'oracle_evaluable': True,
                  'job_id': bindings[0]['prompt_id'], 'execution_started': 1,
                  'execution_finished': 1, 'execution_instances': copy.deepcopy(bindings),
                  'source_decision': copy.deepcopy(decision),
                  'semantics': 'bound backend lifecycle; not physical GPU computation'}
        source = {'record_id': case['case'], 'reported_state': manifest, 'oracle_state': oracle,
                  'conversion_version': VERSION,
                  'conversion_reasons': {'execution': 'audited start, node-null terminal and successful history',
                                         'artifact': 'no independent byte validator retained; omitted'},
                  'source_hashes': {manifest_path.name: hashlib.sha256(manifest_path.read_bytes()).hexdigest()}}
        variants = [('retained', source)]
        missing = copy.deepcopy(source); missing['reported_state'].pop('state', None)
        variants.append(('synthetic_missing_state', missing))
        conflict = copy.deepcopy(source); conflict['job_id'] = 'deliberate-conflict-not-a-backend-job'
        variants.append(('synthetic_identity_conflict', conflict))
        for variant, record in variants:
            exported = export_record(record)
            assert not exported['interpreted_state']['execution_verified']
            if variant == 'synthetic_identity_conflict':
                assert exported['interpreted_state']['evidence_state'] == 'mismatch'
            private.append({'case': case['case'], 'variant': variant, 'input': record, 'export': exported})
            summaries.append({'case': case['case'], 'variant': variant,
                              'interpreted_state': exported['interpreted_state'],
                              'mapping_reason': exported['mapping_reason'],
                              'validator_version': exported['validator_version']})
    return private, {'conversion_version': VERSION, 'source_report_sha256': checked['report_sha256'],
                     'scope': 'offline conversion; synthetic stress variants are not experiments',
                     'records': summaries}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path); p.add_argument('capture', type=Path)
    p.add_argument('private_output', type=Path); p.add_argument('summary_output', type=Path)
    a = p.parse_args(); records, summary = convert(a.report, a.capture)
    with a.private_output.open('x', encoding='utf-8') as f: json.dump(records, f, indent=2)
    with a.summary_output.open('x', encoding='utf-8') as f: json.dump(summary, f, indent=2); f.write('\n')
    print('Converted 2 retained cases and 4 synthetic stress variants; no composite verification')


if __name__ == '__main__':
    main()
