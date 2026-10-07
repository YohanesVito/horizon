#!/usr/bin/env bash
set -euo pipefail
release="${1:?Provide the release ID}"
[[ "$release" =~ ^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{10}$ ]]
base=/opt/horizon/releases
mkdir -p "$base/$release"
tar -xzf "$base/$release.tar.gz" -C "$base/$release"
cd "$base/$release"
python3 - <<'PY'
from pathlib import Path
import hashlib, json
manifest=json.loads(Path('manifest.json').read_text())
for entry in manifest['files']:
    path=Path(entry['path'])
    assert not path.is_absolute() and '..' not in path.parts
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], entry['path']
print('RELEASE_FILE_CHECKSUMS_VERIFIED', len(manifest['files']))
PY
source release.env
docker build --pull -t "$HORIZON_IMAGE" .
# Exercise the complete packaged application against disposable SQLite only.
docker run --rm --read-only --tmpfs /app/.runtime:uid=10001,gid=10001,mode=0700 \
  --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges:true \
  --entrypoint python "$HORIZON_IMAGE" -c '
from fastapi.testclient import TestClient
from backend.main import app
with TestClient(app) as client:
    assert client.get("/api/health").json()["storage"] == "sqlite-local"
    for path in ["/api/catalog", "/api/intelligence", "/api/timeline", "/api/timeline/LPPF?preview=true"]:
        assert client.get(path).status_code == 200, path
print("PACKAGED_APPLICATION_SMOKE_PASSED")
'
docker image inspect "$HORIZON_IMAGE" --format '{{.Id}}' > image-id.txt
python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import json
Path('build-result.json').write_text(json.dumps({'status':'passed', 'completed_at_utc':datetime.now(timezone.utc).isoformat(), 'image_id':Path('image-id.txt').read_text().strip(), 'packaged_application_smoke':'passed'}, indent=2))
PY
