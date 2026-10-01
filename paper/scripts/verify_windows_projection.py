"""Offline semantic projection replay; no raw capture, GPU or backend access."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from scripts.research.export_records import export_record


def main():
    manifest_path = ROOT / 'PACKAGE_MANIFEST.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for name, digest in manifest['files'].items():
            file = (ROOT / name).resolve()
            if not file.is_relative_to(ROOT) or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                raise ValueError('package checksum mismatch')
    path = ROOT / 'paper/examples/windows-conversion-projection.json'
    before = path.read_bytes()
    data = json.loads(before)
    if data['projection_version'] != 'windows-anonymous-semantic-projection-v1':
        raise ValueError('unsupported projection version')
    rows = data['records']
    if len(rows) != 6 or len({(x['case'], x['variant']) for x in rows}) != 6:
        raise ValueError('unexpected projection case set')
    for row in rows:
        state = export_record(row['input'])['interpreted_state']
        if state != row['expected_interpreted_state'] or state['execution_verified']:
            raise ValueError('projection interpretation differs')
        if row['variant'] == 'synthetic_identity_conflict' and state['evidence_state'] != 'mismatch':
            raise ValueError('identity conflict was not withheld')
        if row['variant'] == 'synthetic_missing_state' and state['recovery_state'] != 'unknown':
            raise ValueError('missing recovery state was promoted')
    if path.read_bytes() != before:
        raise ValueError('input changed')
    print('PASS: 2 retained semantic projections + 4 synthetic stress variants; no composite verification')
    print('Scope: offline mapping replay, not independent raw-event audit or live guard reproduction')


if __name__ == '__main__':
    main()
