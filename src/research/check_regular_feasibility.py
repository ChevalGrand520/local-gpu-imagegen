"""Bounded logical witnesses, not a backend experiment or independent benchmark."""
import copy
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from scripts.research.export_records import export_record


def main():
    base = {
        'reported_state': {'state': 'generated'},
        'job_id': 'job-1', 'artifact_hash': 'a' * 64,
        'approval_state': 'valid',
        'artifact_validation': {'status': 'verified', 'independent': True},
        'oracle_state': {'execution_state': 'succeeded', 'oracle_evaluable': True,
                         'execution_started': 1, 'execution_finished': 1,
                         'job_id': 'job-1', 'artifact_hash': 'a' * 64},
    }
    rows = []
    for label, state in [('complete_summary', 'generated'), ('original_run_unresolved', 'unresolved')]:
        record = copy.deepcopy(base)
        record['reported_state']['state'] = state
        output = export_record(record)
        # Only for this frozen, complete-summary pair. NOT a general equivalent implementation.
        simple_policy = state == 'generated'
        actual = output['interpreted_state']['execution_verified']
        assert actual == simple_policy
        rows.append({'case': label, 'input': record, 'interpreted': output['interpreted_state'],
                     'simple_complete_summary_policy': simple_policy,
                     'missing_provenance_fields': [k for k in ('source_sha', 'backend_instance', 'validator_version') if output[k] is None]})
    print(json.dumps({
        'protocol': 'regular-feasibility-logical-witness-v1',
        'scope': 'two synthetic summary records; no real execution or measured accuracy',
        'exporter_sha256': hashlib.sha256((ROOT/'scripts/research/export_records.py').read_bytes()).hexdigest(),
        'witnesses': rows,
        'conclusions': [
            'For this complete-summary pair, a simple policy matches the exporter; not global equivalence.',
            'A verified output is possible without source, backend-instance or validator-version provenance.',
            'The exporter trusts supplied oracle and independent-validator assertions; it does not authenticate their origin.',
            'Identical supplied records yield identical decisions even if one record is stale or fabricated; this is a trust-boundary limit, not an observed production failure.',
        ],
    }, indent=2))


if __name__ == '__main__':
    main()
