"""Check exact Windows source snapshots against retained campaign receipts.

Hash matches establish byte correspondence, not runtime attestation. Does not
execute the snapshots, connect to a backend or access private captures.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]


def main():
    checked = 0
    for version, report in [('v1', 'windows-same-run-20261001.json'),
                            ('v2', 'windows-same-run-v2-20261001.json')]:
        record = json.loads((ROOT / 'paper/evidence' / report).read_text())
        for name, expected in record['harness_source_sha256'].items():
            if Path(name).name != name:
                raise ValueError('unsafe source name')
            file = ROOT / 'paper/evidence/execution-source' / version / name
            if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
                raise ValueError(f'{version}/{name}: source bytes differ')
            checked += 1
    print(f'PASS: {checked} exact source-file hashes; no execution attestation')


if __name__ == '__main__':
    main()
