"""Check retained data and regenerate result tables; never contact a backend.

Windows report equality and byte-match flags are historical inspection receipts,
not independently recomputed checks against files absent from this package.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CPU_IDS = [f'{fault}-{path}' for fault in ('F00', 'F02', 'F03')
           for path in ('single-stage', 'two-stage')]
WINDOWS_IDS = ['B2_F00', 'W3_F00', 'B2_F02', 'W3_F02']
RECOVERY_LABELS = {
    'not_needed': 'Not needed',
    'new_submission_after_fault': 'New submission',
    'outcome_unknown': 'Unknown',
    'outcome_unknown_blocked': 'Unknown; blocked',
    'same_job_reconciled': 'Same job reconciled',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text())


def indexed(rows, expected, field, context):
    keys = [row[field] for row in rows]
    require(len(keys) == len(set(keys)) and set(keys) == set(expected),
            f'{context}: missing, duplicate or unexpected case')
    return {row[field]: row for row in rows}


def audit(root):
    out = root / 'paper/evidence'
    windows_path = out / 'windows-audit.json'
    w = load(windows_path)
    require(w['report_sha256'] == '5c946b67f840876fa4a6a44bf39c7cdf4604d655fdc0197123acd675cebc55f2',
            'Unexpected historical report identity')
    require(w['jsonl_rows'] == 4, 'Unexpected JSONL row count')
    cases = indexed(w['cases'], WINDOWS_IDS, 'case_id', 'Windows')
    ids, windows = [], []
    artifact_checks = 0
    for name in WINDOWS_IDS:
        c = cases[name]
        n = 2 if name.endswith('F02') else 1
        require(c['report_equals_jsonl_case'] is True, f'{name}: recorded report/JSONL mismatch')
        require(c['submissions'] == c['executions'] == len(c['bindings']) == len(c['calls']) == n,
                f'{name}: counts disagree')
        require(c['classifications']['oracle_evaluable'] == 1, f'{name}: not evaluable')
        states = [x['state'] for x in c['calls']]
        require(states == (['unresolved', 'resolved'] if n == 2 else ['resolved']),
                f'{name}: unexpected call sequence')
        require(c['classifications']['resolved'] == int('resolved' in states)
                and c['classifications']['unresolved'] == int('unresolved' in states),
                f'{name}: any-call flags disagree')
        require(len(c['receipts']) == n and
                sum(x['response_dropped'] is True for x in c['receipts']) == (n == 2),
                f'{name}: receipt/injection count disagrees')
        for binding in c['bindings']:
            require(binding['history_completed'] is True and binding['terminal_event'] == 'executing',
                    f'{name}: missing completion binding')
            require(binding['finished_at'] >= binding['started_at'], f'{name}: invalid binding times')
            ids.append(binding['execution_instance_id'])
        for call in c['calls']:
            require(call['exit_code'] == 0 and call['timed_out'] is False, f'{name}: call failed')
            checks = call['artifact_checks']
            require(len(checks) == (1 if call['state'] == 'resolved' else 0),
                    f'{name}: missing or unexpected artifact check')
            for check in checks:
                require(check['matches_current_output_bytes'] is True and
                        check['recorded_hash'] in c['current_output_content_hashes'],
                        f'{name}: artifact inspection receipt inconsistent')
                artifact_checks += 1
        if n == 2:
            require(c['receipts'][1]['received_at'] > c['bindings'][0]['finished_at'],
                    f'{name}: second receipt preceded first completion binding')
        windows.append({'case': name, 'submissions': c['submissions'],
                        'retained_execution_bindings': len(c['bindings']), 'call_states': states})
    require(len(ids) == len(set(ids)) == 6, 'Windows execution IDs not six distinct bindings')
    base = root / 'docs/research/runs'
    paths = [base / f'paired-v2-{k}.json' for k in ('b2', 'w3', 'comparison')]
    raw = {k: indexed(load(base / f'paired-v2-{k}.json')['cases'], CPU_IDS, 'case_id', k)
           for k in ('b2', 'w3')}
    pairs = indexed(load(paths[2])['pairs'], CPU_IDS, 'case_id', 'CPU comparison')
    cpu = []
    for name in CPU_IDS:
        pair = pairs[name]
        row = {'case': name}
        for k in ('b2', 'w3'):
            case = raw[k][name]
            events = case['oracle_state']['events']
            starts = [e['execution_instance_id'] for e in events if e['event'] == 'execution_started']
            ends = [e['execution_instance_id'] for e in events if e['event'] == 'execution_finished']
            require(len(starts) == len(set(starts)) == len(ends) == len(set(ends))
                    == case['oracle_execution_count'] == pair[k + '_execution_count']
                    and set(starts) == set(ends), f'{name}/{k}: execution events disagree')
            submissions = sum(e['event'] == 'request_received' for e in events)
            require(submissions == case['backend_submission_count'] == pair[k + '_submission_count'],
                    f'{name}/{k}: submissions disagree')
            require(type(case['valid_completion']) is bool and
                    case['valid_completion'] == pair[k + '_valid_completion'],
                    f'{name}/{k}: completion disagrees')
            require(case['recovery']['state'] == pair[k + '_recovery_state'],
                    f'{name}/{k}: recovery disagrees')
            row[k] = {'submissions': submissions, 'executions': len(starts),
                      'completion': case['valid_completion'], 'recovery': case['recovery']['state']}
        cpu.append(row)
    return {
        'scope': 'offline consistency check of retained data; no experiment or host access',
        'windows_cases': windows, 'unique_windows_binding_ids': len(set(ids)),
        'recorded_artifact_hash_matches': artifact_checks,
        'windows_verification_boundary': 'report/JSONL equality and image-byte matching are retained inspection receipts; originals are not in this package',
        'raw_windows_event_reconstruction': 'unavailable: no complete raw events/history snapshots',
        'cpu_cases': cpu,
        'input_hashes': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [windows_path, *paths]},
    }


def write_tables(root, result):
    folder = root / 'paper/tables'
    folder.mkdir(exist_ok=True)
    cpu = []
    for row in result['cpu_cases']:
        fault, path = row['case'].split('-', 1)
        b, w = row['b2'], row['w3']
        fields = [fault, 'Single stage' if path == 'single-stage' else 'Two stage',
                  f"{b['submissions']}/{b['executions']}", f"{w['submissions']}/{w['executions']}",
                  f"{'yes' if b['completion'] else 'no'}/{'yes' if w['completion'] else 'no'}",
                  RECOVERY_LABELS[b['recovery']], RECOVERY_LABELS[w['recovery']]]
        cpu.append(' & '.join(fields) + r'\\')
    windows = []
    for row in result['windows_cases']:
        system, fault = row['case'].split('_')
        fields = [system, fault, str(len(row['call_states'])),
                  f"{row['submissions']}/{row['retained_execution_bindings']}",
                  r'U $\to$ R' if len(row['call_states']) == 2 else 'R']
        windows.append(' & '.join(fields) + r'\\')
    for name, rows in [('cpu-rows.tex', cpu), ('windows-rows.tex', windows)]:
        columns = 'llcccll' if name == 'cpu-rows.tex' else 'llccc'
        heading = (r'Fault & Path & B2 S/E & W3 S/E & Complete (B2/W3) & B2 recovery & W3 recovery\\'
                   if name == 'cpu-rows.tex' else r'System & Case & Calls & S/E & Call sequence\\')
        (folder / name).write_text('% Generated by audit_retained_evidence.py; do not edit.\n'
                                  + r'\begin{tabular}{' + columns + '}\n' + r'\hline' + '\n'
                                  + heading + '\n' + r'\hline' + '\n' + '\n'.join(rows)
                                  + '\n' + r'\hline' + '\n' + r'\end{tabular}' + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    result = audit(args.root)
    (args.root / 'paper/evidence/audit-results.json').write_text(json.dumps(result, indent=2) + '\n')
    write_tables(args.root, result)
    print(f"PASS: {len(result['windows_cases'])} Windows cases, {result['unique_windows_binding_ids']} retained binding IDs, "
          f"{result['recorded_artifact_hash_matches']} recorded byte-match receipts, {2 * len(result['cpu_cases'])} synthetic traces")


if __name__ == '__main__':
    main()
