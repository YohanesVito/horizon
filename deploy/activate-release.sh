#!/usr/bin/env bash
set -euo pipefail
release="${1:?Provide the release ID}"
[[ "$release" =~ ^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{10}$ ]]
cd "/opt/horizon/releases/$release"
python3 - <<'PY'
from pathlib import Path
import json
assert json.loads(Path('build-result.json').read_text())['status'] == 'passed', 'Image smoke must pass first'
assert Path('/opt/horizon/shared/backend.env').stat().st_mode & 0o777 == 0o600
PY
# The previous backend must be stopped first: the database lease allows one worker.
docker compose --env-file release.env -f deploy/compose.yaml config --quiet
docker compose --env-file release.env -f deploy/compose.yaml up -d --wait --wait-timeout 120
docker compose --env-file release.env -f deploy/compose.yaml ps --format json > container-status.json
python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import json
Path('start-result.json').write_text(json.dumps({'status':'healthy', 'started_at_utc':datetime.now(timezone.utc).isoformat(), 'public_api_verification':'pending'}, indent=2))
PY
