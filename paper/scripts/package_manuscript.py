"""Build an author-review package, not an anonymized submission artifact."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'paper'
EXCLUDED = {'build', 'delivery', '__pycache__'}
SUFFIXES = {'.aux', '.bbl', '.blg', '.out', '.log', '.pyc'}


def main():
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', 'paper'], cwd=ROOT)
    files = [ROOT / name.decode('utf-8') for name in tracked.split(b'\0') if name]
    files = [p for p in files if p.is_file()
             and not any(x in EXCLUDED for x in p.relative_to(PAPER).parts)
             and p.suffix not in SUFFIXES]
    files += [ROOT / 'docs/research/runs' / name for name in
              ('paired-v2-b2.json', 'paired-v2-w3.json', 'paired-v2-comparison.json', 'paired-v2-commands.md')]
    files += [ROOT / 'docs/research/dsn-evidence-reconciliation-20260927.md']
    files += [ROOT / 'docs/research/dsn-next-evidence-gates-20260929.md']
    files += [ROOT / name for name in (
        'scripts/research/export_records.py',
        'scripts/research/f02_campaign.py',
        'scripts/research/f02_oracle.py',
        'scripts/research/f02_product_client.py',
        'scripts/research/f02_loopback.py',
        'scripts/local_gpu_imagegen/engine.py',
        'scripts/local_gpu_imagegen/run_store.py',
        'scripts/local_gpu_imagegen/backends/base.py',
    )]
    manifest = {
        'purpose': 'author review; not a certified anonymous submission package',
        'scope': 'manuscript and retained-evidence reanalysis; not full generation-tool source',
        'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(files)},
    }
    dest = PAPER / 'delivery/dsn-tool-description-v0.8.zip'
    dest.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(p, str(p.relative_to(ROOT)))
        z.writestr('PACKAGE_MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    print(f'{dest.name}: {len(files)} files plus checksum manifest, {dest.stat().st_size} bytes')


if __name__ == '__main__':
    main()
