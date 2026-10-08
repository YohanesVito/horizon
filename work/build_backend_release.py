"""Create an allowlisted backend release, scanning against local secrets."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import tarfile
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
patterns = [
    'Dockerfile', '.dockerignore', 'deploy/compose.yaml',
    'backend/*.py', 'backend/data/*.json', 'backend/requirements.lock', 'backend/migrations/*.sql',
    'outputs/dividend-research/*.json', 'outputs/mvp-sectors/*.json',
    'outputs/sectors-live/bbca-dividend.json',
    'outputs/dividend-discovery/*.json',
    'outputs/intelligence/raw/*.json', 'outputs/rotation/raw/*.json',
    'outputs/timeline-audit/*.json', 'outputs/timeline-audit/raw/*.json',
]
files = sorted({path for pattern in patterns for path in ROOT.glob(pattern) if path.is_file()})
private = [v.encode() for k, v in dotenv_values(ROOT / '.env.local').items()
           if v and len(v) >= 16 and any(s in k for s in ('KEY', 'PASSWORD', 'DATABASE_URL'))]
records = []
for path in files:
    if path.is_symlink():
        raise SystemExit('Symlink not permitted in release: ' + str(path.relative_to(ROOT)))
    data = path.read_bytes()
    if any(secret in data for secret in private):
        raise SystemExit('Private value found; release aborted: ' + str(path.relative_to(ROOT)))
    records.append({'path': str(path.relative_to(ROOT)), 'bytes': len(data),
                    'sha256': hashlib.sha256(data).hexdigest()})
digest = hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
release = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + digest[:10]
folder = ROOT / '.runtime/deploy' / release
folder.mkdir(parents=True, exist_ok=False)
manifest = {'release': release, 'source_sha256': digest, 'files': records,
            'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'includes_uncommitted_work': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
            'secret_scan': 'passed', 'image': 'horizon-api:' + release.lower()}
(folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(folder / 'release.env').write_text('HORIZON_IMAGE=' + manifest['image'] + '\n')
with tarfile.open(folder / 'release.tar.gz', 'w:gz') as archive:
    for path in files:
        archive.add(path, arcname=str(path.relative_to(ROOT)), recursive=False)
    archive.add(folder / 'manifest.json', arcname='manifest.json')
    archive.add(folder / 'release.env', arcname='release.env')
print(json.dumps({'release': release, 'archive': str(folder / 'release.tar.gz'),
                  'files': len(files), 'bytes': (folder / 'release.tar.gz').stat().st_size,
                  'source_sha256': digest, 'secret_scan': 'passed'}, indent=2))
